from Scrapper import Scrapper
import datetime
import pandas as pd
import json


def main():

    date = datetime.datetime(2020,2,10).strftime('%Y-%m-%d')
    url = 'https://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate='+date

    url = 'https://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=0&GameID=0012000047&RangeType=0&Season=2019-20&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'

    datasets_name = ['GameHeader', 'LineScore',
                'EastConfStandingsByDay', 'WestConfStandingsByDay']

    HEADERS = {
        # 'Host': 'i.cdn.turner.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Referer': 'https://www.nba.com/stats/',
        'Origin': 'https://www.nba.com',    
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive'
    }
    

    scrapper = Scrapper(headers=HEADERS, max_call_errors=5)
    json_returned = scrapper.retrieve_json_api_from_url(url=url)

    if json_returned == None:
        return

    print(json.dumps(json_returned, indent=4, sort_keys=True))

    # dfs = {}
    # for elem in json_returned['resultSets']:
    #     if elem['name'] not in datasets_name:
    #         continue

    #     df = pd.DataFrame(elem['rowSet'], columns=elem['headers'])
    #     dfs[elem['name']] = df

    


if __name__ == "__main__":
    main()
