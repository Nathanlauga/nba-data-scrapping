from time import time
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

games = pd.read_csv('data/games_no_dup.csv')
ranking = pd.read_csv('data/ranking.csv')
teams = pd.read_csv('data/teams.csv')
games_detail = pd.read_csv('data/games_details.csv')

print(games_detail.shape, games.shape, ranking.shape, teams.shape)

def filter_by_game_id(df, game_id):
    return df[df['GAME_ID'] == game_id]

def filter_by_team_id(df, team_id):
    return df[df['TEAM_ID'] == team_id]

def filter_by_player_id(df, player_id):
    return df[df['PLAYER_ID'] == player_id]

def filter_on_season(df, season):
    return df[df['GAME_ID'].astype(str).str[1:3] == season]

def split_starters_bench(df):
    is_starter = df['START_POSITION'].notna()
    return df[is_starter], df[~is_starter]

def extract_player_id(df):
    return df['PLAYER_ID'].unique().tolist()

def pivot_by_position(df):
    start_pos = df['START_POSITION']
    df['START_POSITION'] = np.where(start_pos.duplicated(keep=False), 
                      start_pos + df.groupby('START_POSITION').cumcount().add(1).astype(str),
                      start_pos)
    df = df.pivot(index='GAME_ID', columns='START_POSITION', values='PLAYER_ID')
    return df.reset_index(drop=False)

def get_df_id(df, cols_id):
    return df[cols_id].drop_duplicates().reset_index(drop=True)

def format_bench_df(values):
    return pd.DataFrame([[values]], columns=['BENCH'])

def filter_games_played(df):
    return df[df['MIN'].notna()]

def add_game_date_column(df):
    games_df = games.copy()[['GAME_ID', 'GAME_DATE_EST']]
    return df.merge(games_df, on='GAME_ID')

def sort_by_date(df, ascending):
    return df.sort_values('GAME_DATE_EST', ascending=ascending)

def get_last_games(df, nb_games):
    if len(df) < nb_games:
        nb_games = len(df)
    return df.iloc[0:nb_games]

def extract_stats_col(df):
    stats_cols = ['MIN', 'FG_PCT', 'FG3M', 'OREB', 'DREB', 'REB', 'BLK', 'PF', 'PTS', 'PLUS_MINUS']
    return df[stats_cols]

def format_column_player_stat(df, suffixe):
    df.columns = [col+'_'+suffixe for col in df.columns]
    return df        

def at_least_n_games_played_season(df, season, nb_games=10):
    df = filter_on_season(df, season=season)
    return len(df) >= nb_games

def get_current_ranking(df):
    return df.sort_values('STANDINGSDATE', ascending=False).iloc[0]

def convert_min(x):
    if type(x) != type(list()):
        return 0
    elif len(x) < 2:
        return int(x[0])
    else: 
        return int(x[0])*60+int(x[1])

def format_min_columns(df):
    if 'MIN' in df.columns:
        df['MIN'] = df['MIN'].str.split(':').apply(lambda x: convert_min(x))
    return df

def get_number_game_played(team_id, season, date):
    df = filter_by_team_id(ranking, team_id=team_id)
    df = df[df['SEASON_ID'].astype(str).str[-2:] == season]
    df = df[df['STANDINGSDATE'] < date]
    return len(df)

def get_game_players(game_id, team_id):
    df = games_detail.copy()
    df = filter_by_game_id(df=df, game_id=game_id)
    df = filter_by_team_id(df=df, team_id=team_id)
    
    starters, bench = split_starters_bench(df)
    
    bench_player = extract_player_id(bench)
    bench_player = format_bench_df(bench_player)
    start_player = pivot_by_position(starters)
    df_id = get_df_id(df, cols_id=['GAME_ID', 'TEAM_ID'])
    
    df = pd.concat([df_id, start_player, bench_player], axis=1)
    del df_id, start_player, bench_player
    return df

def get_player_stats(player_id, is_season, value):
    """
    
    Parameters
    ----------
    player_id
        Id of the player
    is_season: bool
        if we want the season stats or per games
    value:
        season if is_season is True
        number of games if is_season is False
    """
    df = games_detail.copy()
    df = filter_by_player_id(df=df, player_id=player_id)
    df = filter_games_played(df)
    df = add_game_date_column(df)
    df = sort_by_date(df, ascending=False)
    
    if is_season:
        if at_least_n_games_played_season(df, season=value, nb_games=10):
            df = filter_on_season(df, season=value)
        else:
            df = get_last_games(df, nb_games=10)
    else:
        df = get_last_games(df, nb_games=value)
    
    df = extract_stats_col(df)
    format_min_columns(df)
    df = df.mean()    
    return df.to_frame().T


def get_team_global_stats(df, team_id, is_home):
    season = df['GAME_ID'].astype(str).str[1:3].values[0]
    date = df['GAME_DATE_EST'].values[0]
    df = filter_on_season(games, season=season)
    nb_games = get_number_game_played(team_id, season, date)
    
    if nb_games < 10:
        season = str(int(season)-1)
        df = filter_on_season(games, season=season)
    
    if is_home:
        df = df[df['HOME_TEAM_ID'] == team_id]
        df = df[['PTS_home', 'PTS_away']]
    else:
        df = df[df['VISITOR_TEAM_ID'] == team_id]
        df = df[['PTS_away', 'PTS_home']]
        
    df.columns = ['PTS', 'PTS_CONCEDED']
    df = df.mean().to_frame().T
    
    return df
    

def get_team_players_stats(df, team_id):
    game_id = df['GAME_ID'].values[0]
    season = df['GAME_ID'].astype(str).str[1:3].values[0]
    df = get_game_players(game_id=game_id, team_id=team_id)
    
    players_stat = list()
    positions = [c for c in df.columns if c not in ['GAME_ID', 'TEAM_ID', 'GAME_ID', 'BENCH']]
    # positions = []
    
    for position in positions: # ['C','F1','F2','G1','G2']:
        player_id = df[position].values[0]
        
        player_stat = get_player_stats(player_id=player_id, is_season=False, value=3)
        player_stat = format_column_player_stat(player_stat, '3G_'+position)
        players_stat.append(player_stat)
        
        player_stat = get_player_stats(player_id=player_id, is_season=True, value=season)
        player_stat = format_column_player_stat(player_stat, 'SEASON_'+position)
        players_stat.append(player_stat)
    
    bench_stat = list()
    for player_id in df['BENCH'].values[0]:
        player_stat = get_player_stats(player_id=player_id, is_season=False, value=3)
        player_stat_3g = format_column_player_stat(player_stat, '3G_BENCH')
        player_stat = get_player_stats(player_id=player_id, is_season=True, value=season)
        player_stat_season = format_column_player_stat(player_stat, 'SEASON_BENCH')
        
        bench_stat.append(pd.concat([player_stat_3g, player_stat_season], axis=1))
        
    bench_stat = pd.concat(bench_stat)
    bench_stat = bench_stat.mean().to_frame().T
        
    df = pd.concat([df]+players_stat+[bench_stat], axis=1)            
    return df

def get_team_rank(df, team_id):
    date = df['GAME_DATE_EST'].values[0]
    season = df['SEASON'].values[0]
    
    team_ranking = filter_by_team_id(ranking, team_id=team_id)
    team_ranking = team_ranking[team_ranking['STANDINGSDATE'] < date]
    
    if len(team_ranking) == 0:
        return None
    
    current = get_current_ranking(team_ranking)
    if current['G'] < 10:
        team_ranking = team_ranking[team_ranking['SEASON_ID'].astype(str).str[-4:] == season]
        if len(team_ranking) > 0:            
            current = get_current_ranking(team_ranking)
    
    return current[['G','W_PCT','HOME_RECORD','ROAD_RECORD']].to_frame().T.reset_index(drop=True)

def get_team_details(df, col_team_id):
    team_id = df[col_team_id].values[0]
    is_home = 'HOME' in col_team_id
    
    team_global_stats = get_team_global_stats(df, team_id=team_id, is_home=is_home)
    team_player_stats = get_team_players_stats(df, team_id=team_id)
    team_rank = get_team_rank(df, team_id=team_id)
    df_id = get_df_id(df, cols_id=[col_team_id])
    df =  pd.concat([team_rank, team_player_stats, team_global_stats], axis=1)
    del df['GAME_ID']
    
    return df


def format_game(game_id):
    df = filter_by_game_id(games, game_id=game_id)
    if len(df) < 1:
        return None
    if len(df) > 1:
        df = df.drop_duplicates()
    
    home_team = get_team_details(df, 'HOME_TEAM_ID')
    away_team = get_team_details(df, 'VISITOR_TEAM_ID')
    
    df = df[['GAME_ID', 'HOME_TEAM_WINS', 'HOME_TEAM_ID','VISITOR_TEAM_ID']]
    df = df.merge(home_team, how='inner', left_on='HOME_TEAM_ID', right_on='TEAM_ID')
    df = df.merge(away_team, how='inner', left_on='VISITOR_TEAM_ID', right_on='TEAM_ID', suffixes=('_home','_away'))
    
    del df['TEAM_ID_home'], df['TEAM_ID_away'], df['BENCH_home'], df['BENCH_away']
    return df

available_game = games_detail['GAME_ID'].drop_duplicates().reset_index(drop=True)

available_game = games.merge(available_game, how='inner', on='GAME_ID')
games_train = available_game[available_game['GAME_ID'].astype(str).str[1:3] != '11']
games_train = games_train.sort_values('GAME_DATE_EST', ascending=False)
games_train['FILTER'] = games_train['GAME_ID'].astype(str).str[1:3].astype(int)
games_train = games_train[games_train['FILTER'] <= 17]
t0 = time()
season = '17'
games_list = list()

for game_id in games_train['GAME_ID']:
    games_list.append(format_game(game_id=game_id))
    
    if str(game_id)[1:3] != season and len(games_list) > 0:
        df_to_save = pd.concat(games_list)
        df_to_save.to_csv('data/games_formated_20'+season+'.csv', index=False)
        print('data/games_formated_20'+season+'.csv', '- time elapsed : %.2fs'%(time()-t0), df_to_save.shape)
        season = str(game_id)[1:3]


df_to_save = pd.concat(games_list)
df_to_save.to_csv('data/games_formated.csv', index=False)
print('data/games_formated.csv - time elapsed : %.2fs'%(time()-t0))