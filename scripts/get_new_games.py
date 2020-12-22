from time import time, sleep
import pandas as pd
import numpy as np
import datetime
import joblib
import os

from NBADataPreformater import NBADataPreformater
from utils import * 


USER_AGENTS = [
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    # 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
    # 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
]
# USER_AGENTS = [
#     ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'),  # chrome
#     ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'),  # chrome
#     ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'),  # firefox
#     ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'),  # chrome
#     ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'),  # chrome
#     ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'),  # chrome
# ]

HEADERS = {
    # 'Host': 'i.cdn.turner.com',
    # "Host": "httpbin.org", 
    # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Referer': 'https://www.nba.com/stats/',
    'Origin': 'https://www.nba.com',    
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
}


def main():
    print('----- START -----')
    t0 = time()

    path = 'data/'

    # Get old games data to find out the last date that the script was executed
    old_games = pd.read_csv(path+'games.csv')
    max_date = old_games['GAME_DATE_EST'].max()

    if max_date == get_date(1):
        print('Last update is yesterday : end script now.')
        return

    print('Last updated date : ', str(max_date))

    # Load old datasets
    old_ranking = pd.read_csv(path+'ranking.csv')
    old_games_details = pd.read_csv(path+'games_details.csv')

    # Dataset to retrieve from api
    datasets = ['GameHeader', 'LineScore',
                'EastConfStandingsByDay', 'WestConfStandingsByDay']
    ignore_keys = ['date']

    # init dictionnary to collect data
    dfs = {}
    for dataset in datasets + ignore_keys:
        dfs[dataset] = list()

    # Be sure this file is the save of the current run
    save_path = 'games.sav'
    if os.path.exists(save_path):
        dfs = joblib.load(save_path)
        min_date_already_saved = min(dfs['date'])


    # Use a for loop to avoid while(True) infinite loop
    for i in range(1, 10000):
        date = get_date(i)

        if date <= max_date:
            break
        elif date >= min_date_already_saved:
            continue

        url = 'https://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate='+date

        print(url)

        # update user agents
        HEADERS['User-Agent'] = np.random.choice(USER_AGENTS)
        # print(HEADERS['User-Agent'])

        game_day_dfs = get_data(url=url, datasets_name=datasets, headers=HEADERS)
        game_day_dfs['date'] = date
        sleep(0.2)

        # print(game_day_dfs['GameHeader'])
        print('There are %i games this day'%len(game_day_dfs['GameHeader']))

        for dataset in game_day_dfs.keys():
            dfs[dataset].append(game_day_dfs[dataset])

        joblib.dump(dfs, save_path)

    # convert to pandas DataFrame
    for dataset in dfs.keys():
        if dataset in ignore_keys:
            continue
        dfs[dataset] = pd.concat(dfs[dataset])
        print(dataset, dfs[dataset].shape)

    header_cols = ['GAME_DATE_EST', 'GAME_ID', 'GAME_STATUS_TEXT',
                   'HOME_TEAM_ID', 'VISITOR_TEAM_ID', 'SEASON']
    linescore_cols = ['GAME_ID', 'TEAM_ID', 'PTS',
                      'FG_PCT', 'FT_PCT', 'FG3_PCT', 'AST', 'REB']

    # Get wanted datasets with wanted columns
    west_ranking = dfs['WestConfStandingsByDay']
    east_ranking = dfs['EastConfStandingsByDay']
    games_header = dfs['GameHeader'][header_cols]
    line_score = dfs['LineScore'][linescore_cols]

    del dfs

    # Preformat NBA data
    print('Preformat nba data')
    preformater = NBADataPreformater(
        games_header, line_score, west_ranking, east_ranking)
    new_games = preformater.preformat_games()
    new_ranking = preformater.preformat_ranking()

    del games_header, line_score, west_ranking, east_ranking

    dfs_details = list()

    # Be sure this file is the save of the current run
    save_details_path = 'games_details.sav'
    if os.path.exists(save_details_path):
        dfs_details = joblib.load(save_details_path)
        game_details_already_saved = pd.concat(dfs_details)['GAME_ID'].unique()

    # Retrieve game detail
    print('Retrieve new games details, # of games to get : ', str(len(new_games['GAME_ID'])))
    for game_id in new_games['GAME_ID']:
        if game_id in game_details_already_saved:
            continue

        # HEADERS['User-Agent'] = np.random.choice(USER_AGENTS)
        HEADERS['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'

        df = get_game_detail(game_id, headers=HEADERS)
        if len(df) == 0:
            print('No data found')

        dfs_details.append(df)

        joblib.dump(dfs_details, save_details_path)

    new_games_details = pd.concat(dfs_details)

    # Merge old and new dataframe
    print('Merging old and new datasets')
    ranking = merge_news_old(new_ranking, old_ranking)
    games = merge_news_old(new_games, old_games)
    games_details = merge_news_old(new_games_details, old_games_details)

    games['GAME_ID'] = pd.to_numeric(games['GAME_ID'])
    games['GAME_DATE_EST'] = pd.to_datetime(games['GAME_DATE_EST'])
    games_details['GAME_ID'] = pd.to_numeric(games_details['GAME_ID'])
    ranking['STANDINGSDATE'] = pd.to_datetime(ranking['STANDINGSDATE'])

    # Save merge datasets
    print('Save new datasets to csv into ', path)
    today = get_date(0)
    games.to_csv(path+'games.csv', index=False)
    games_details.to_csv(path+'games_details.csv', index=False)
    ranking.to_csv(path+'ranking.csv', index=False)

    print('-----  END  ----- execution time : %.2fs' % (time()-t0))


if __name__ == "__main__":
    main()
