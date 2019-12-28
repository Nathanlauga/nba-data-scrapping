import requests
from time import sleep, time
import pandas as pd
import os


def get_data(url, dataset_name):
    HEADERS = {'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Referer': 'https://stats.nba.com/game/0021900253/'}

    response = requests.get(url, headers=HEADERS)
    status_200_ok = response.status_code == 200
    nb_error = 0
    
    while not status_200_ok and nb_error < 5:
        sleep(1)
        response = requests.get(url)
        status_200_ok = response.status_code == 200
        nb_error += 1
    
    # print(response.status_code, url)

    if nb_error == 5:
        return None
    
    json = response.json()
    
    json_dataset = [elem for elem in json['resultSets'] if elem['name'] == dataset_name][0]

    df = pd.DataFrame(json_dataset['rowSet'], columns=json_dataset['headers'])
    return df


t0 = time()

def get_game_detail(game_id: str):
    url = 'https://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=0&GameID='+str(game_id) \
        +'&RangeType=0&Season=2019-20&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
    df = get_data(url, dataset_name='PlayerStats')
    # print(game_id, '- time elapsed : %.2fs'%(time()-t0))
    return df


def format_game_id(df):
    return df['GAME_ID'].apply(lambda x: '00'+str(x))


games_df = pd.read_csv('data/games.csv')
print(games_df.shape)
games_df['GAME_ID'] = format_game_id(games_df)
games_df = games_df.sort_values('GAME_DATE_EST', ascending=False)
games_df['FILTER'] = games_df['GAME_ID'].str[3:5].astype(int)
games_df = games_df[games_df['FILTER'] < 9]

games_detail = list()
season = '08'

for idx, row in games_df.iterrows():
    game_id = row['GAME_ID']
    
    if game_id[3:5] != season and len(games_detail) > 0:
        print(season)
        games_detail_df = pd.concat(games_detail)
        games_detail_df.to_csv('data/games_details_20'+season+'.csv', index=False)
        print('data/games_details_20'+season+'.csv', '- time elapsed : %.2fs'%(time()-t0), games_detail_df.shape)
        season = game_id[3:5]

    games_detail.append(get_game_detail(row['GAME_ID']))

# games_detail = games_df['GAME_ID'].iloc[0:4].apply(lambda x: get_game_detail(x, last_season))
games_detail_df = pd.concat(games_detail)

games_detail_df.to_csv('data/games_details.csv', index=False)
print('data/games_details.csv', '- time elapsed : %.2fs'%(time()-t0))