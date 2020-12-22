import pandas as pd


def main():
    datasets = ['games.csv','games_details.csv']

    games = pd.read_csv('data/games.csv')

    print('====== GAMES ======')
    print(games.shape)
    print('Min date : %s'%(games['GAME_DATE_EST'].min()))
    print('Max date : %s'%(games['GAME_DATE_EST'].max()))


    games_details = pd.read_csv('data/games_details.csv')
    print('====== GAMES DETAILS ======')
    print(games_details.shape)
    print('N uniques games ID : %i'%(games_details['GAME_ID'].nunique()))


if __name__ == '__main__':
    main()