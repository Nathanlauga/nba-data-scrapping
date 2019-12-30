from time import time
import pandas as pd
import numpy as np

from NBADataPreformater import NBADataPreformater
from utils import * 

def main():
    print('----- START -----')
    t0 = time()

    path = 'nba/data/'

    # Get old games data to find out the last date that the script was executed
    old_games = pd.read_csv(path+'games.csv')
    max_date = old_games['GAME_DATE_EST'].max()

    print('Last updated date : ', str(max_date))

    # Load old datasets
    old_ranking = pd.read_csv(path+'ranking.csv')
    old_games_details = pd.read_csv(path+'games_details.csv')

    # Dataset to retrieve from api
    datasets = ['GameHeader', 'LineScore',
                'EastConfStandingsByDay', 'WestConfStandingsByDay']

    # init dictionnary to collect data
    dfs = {}
    for dataset in datasets:
        dfs[dataset] = list()

    # Use a for loop to avoid while(True) infinite loop
    for i in range(1, 10000):
        date = get_date(i)
        if date <= max_date:
            break

        url = 'https://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate='+date

        print(url)
        game_day_dfs = get_data(url=url, datasets_name=datasets)
        for dataset in game_day_dfs.keys():
            dfs[dataset].append(game_day_dfs[dataset])

    # convert to pandas DataFrame
    for dataset in dfs.keys():
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

    dfs = list()

    # Retrieve game detail
    print('Retrieve new games details, # of games to get : ', str(len(new_games['GAME_ID'])))
    for game_id in new_games['GAME_ID']:
        df = get_game_detail(game_id)
        dfs.append(df)

    new_games_details = pd.concat(dfs)

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
    today = get_date(i)
    games.to_csv(path+'games_'+today+'.csv', index=False)
    games_details.to_csv(path+'games_details_'+today+'.csv', index=False)
    ranking.to_csv(path+'ranking_'+today+'.csv', index=False)

    print('-----  END  ----- execution time : %.2fs' % (time()-t0))


if __name__ == "__main__":
    main()
