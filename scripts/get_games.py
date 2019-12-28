import requests
import json
from time import sleep
import pandas as pd
import os
import datetime

HEADERS = {'Host': 'stats.nba.com',
'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
'Referer': 'https://stats.nba.com/game/0021900253/'}

def get_date(days: int):
    date = datetime.date.today() - datetime.timedelta(days=days)
    return date.strftime('%m/%d/%Y')


# Game by day
dataset_to_keep = ['GameHeader','LineScore','LastMeeting','EastConfStandingsByDay','WestConfStandingsByDay']
dfs = {}
wait = True

for i in range(1,10000):
    date = get_date(i)
    url = 'https://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate='+date

    if date == '09/30/2003':
        break

    response = requests.get(url, headers=HEADERS)
    status_200_ok = response.status_code == 200
    nb_error = 0

    while not status_200_ok and nb_error < 5:
        print(response.status_code, url)
        sleep(1)
        response = requests.get(url)
        status_200_ok = response.status_code == 200
        nb_error += 1

    print(response.status_code, url)

    if nb_error < 5:
        nba_day_json = response.json()

        for dataset in nba_day_json['resultSets']:
            df_name = dataset['name']
            df_head = dataset['headers']
            df_rows = dataset['rowSet']
            if df_name not in dataset_to_keep:
                continue

            new_df = pd.DataFrame(df_rows, columns=df_head)
            if df_name not in dfs:
                dfs[df_name] = new_df
            else: 
                dfs[df_name] = pd.concat([dfs[df_name], new_df])


for name in dfs:
    path = 'data/'+str(name)+'.csv'
    if os.path.isfile(path):
        print(exist) 
    dfs[name].to_csv(path, index=False)