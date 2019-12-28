from time import time
import pandas as pd
import requests

def get_data(url, datasets_name):
    HEADERS = {'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Referer': 'https://stats.nba.com/game/0021900253/'}

    response = requests.get(url, headers=HEADERS)
    status_200_ok = response.status_code == 200
    nb_error = 0
    
    # If there are too much call, just try 5 times to be sure that we can't have the data
    while not status_200_ok and nb_error < 5:
        sleep(1)
        response = requests.get(url)
        status_200_ok = response.status_code == 200
        nb_error += 1
    
    if nb_error == 5:
        return None
    
    json = response.json()
    dfs = {}
    for elem in json['resultSets']:
        if elem['name'] not in datasets_name:
            continue
        
        df = pd.DataFrame(elem['rowSet'], columns=elem['headers'])
        dfs[elem['name']] = df
    
    return dfs


def get_team_detail(team_id: int):
    url = 'https://stats.nba.com/stats/teamdetails?TeamID='+str(team_id)    
    df = get_data(url, datasets_name=['TeamBackground'])
    return df['TeamBackground']

def main():
    print('----- START -----')
    t0 = time()

    # Load all teams
    url = 'https://stats.nba.com/stats/commonteamyears?LeagueID=00'
    teams = get_data(url, datasets_name=['TeamYears'])
    teams = teams['TeamYears']

    # Get team detail
    teams_detail = teams['TEAM_ID'].apply(lambda x: get_team_detail(x))
    teams_detail = pd.concat(teams_detail.values)

    # Merge both datasets
    teams_full = teams.merge(teams_detail, on=['TEAM_ID','ABBREVIATION'])

    # Save teams dataset
    teams_full.to_csv('data/teams.csv', index=False)

    print('-----  END  ----- execution time : %.2fs'%(time()-t0))


if __name__ == "__main__":
    main()