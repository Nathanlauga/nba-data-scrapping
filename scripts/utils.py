import datetime
import pandas as pd
from Scrapper import Scrapper


def get_date(days: int):
    date = datetime.date.today() - datetime.timedelta(days=days)
    return date.strftime('%Y-%m-%d')


def merge_news_old(new_df, old_df):
    return pd.concat([new_df, old_df], sort=False).drop_duplicates().reset_index(drop=True)


def get_data(url, datasets_name):
    HEADERS = {
        'Referer': 'https://stats.nba.com',
        'Origin': 'https://stats.nba.com',
        'x-nba-stats-token': 'true',
        'x-nba-stats-origin': 'stats',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    scrapper = Scrapper(headers=HEADERS, max_call_errors=5)
    json = scrapper.retrieve_json_api_from_url(url=url)

    if json == None:
        return None

    dfs = {}
    for elem in json['resultSets']:
        if elem['name'] not in datasets_name:
            continue

        df = pd.DataFrame(elem['rowSet'], columns=elem['headers'])
        dfs[elem['name']] = df

    return dfs


def get_game_detail(game_id):
    if type(game_id) != type(str()):
        game_id = '00' + str(game_id)

    url = 'https://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=0&GameID='+str(game_id) \
        + '&RangeType=0&Season=2019-20&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'

    print(url)
    df = get_data(url, datasets_name=['PlayerStats'])
    return df['PlayerStats']
