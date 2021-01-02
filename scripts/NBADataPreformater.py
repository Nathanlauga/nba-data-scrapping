import pandas as pd
import numpy as np
import os

class NBADataPreformater():
    """
    Preformater after data collection on nba stats api.

    """
    # path = os.path.dirname(os.path.abspath(__file__)) + '/data/'

    def __init__(self, games_header, line_score, west_ranking, east_ranking, path):
        self.path = path
        self.games_header = games_header
        self.line_score = line_score
        self.west_ranking = west_ranking
        self.east_ranking = east_ranking
        self.teams = pd.read_csv(self.path+'teams.csv')

    def merge_on_team(self, df, team_col):
        return df.merge(self.line_score,
                        how='inner',
                        left_on=['GAME_ID', team_col],
                        right_on=['GAME_ID', 'TEAM_ID'],
                        suffixes=('_home', '_away'))

    def home_team_win(self, df):
        return np.where(df['PTS_home'] > df['PTS_away'], 1, 0)

    def format_game_id(self, df):
        return df['GAME_ID'].apply(lambda x: '00'+str(x))

    def format_date(self, df):
        return pd.to_datetime(df['GAME_DATE_EST'])

    def filter_game_no_nba_team(self, df):
        teams_id_nba = self.teams['TEAM_ID'].unique()
        home_team_is_nba = df['HOME_TEAM_ID'].apply(
            lambda x: x in teams_id_nba)
        away_team_is_nba = df['VISITOR_TEAM_ID'].apply(
            lambda x: x in teams_id_nba)

        return df[(home_team_is_nba) & (away_team_is_nba)]

    def only_finished_game(self, df):
        return df[df['GAME_STATUS_TEXT'] == 'Final']

    def preformat_games(self):
        games_df = self.games_header.copy()
        games_df = self.merge_on_team(df=games_df, team_col='HOME_TEAM_ID')
        games_df = self.merge_on_team(df=games_df, team_col='VISITOR_TEAM_ID')

        games_df['HOME_TEAM_WINS'] = self.home_team_win(games_df)
        games_df['GAME_ID'] = self.format_game_id(games_df)
        games_df['GAME_DATE_EST'] = self.format_date(games_df)

        games_df = self.filter_game_no_nba_team(games_df)
        games_df = self.only_finished_game(games_df)

        games_df['GAME_ID'] = games_df['GAME_ID'].astype(int)
        games_df = games_df.drop_duplicates().reset_index(drop=True)

        return games_df

    def preformat_ranking(self):
        ranking = pd.concat([self.west_ranking, self.east_ranking])
        ranking['STANDINGSDATE'] = pd.to_datetime(ranking['STANDINGSDATE'])

        return ranking