# NBA games : data collection & model creation

This repo is centered about NBA games. The main goal here is to create a model that will predict a winner for a NBA game.

There are differents steps for this project :
1. Collect data
2. Format data
3. Create model
4. Automatize data collection
5. Predict on next games (real)

At this moment I'm at **[step 3]**.

## 1. Collect data

You can find how I collect the data on the `scripts/` folder. 

I would like to thanks [nba stats website](https://stats.nba.com/) which allows all NBA data freely open to everyone and with a great api endpoint.

- `get_games.py` : collect all games from yesterday to 2003
- `get_teams.py` : collect all teams from NBA
- `get_players.py` : collect all players from NBA based on games dataset **[WORK IN PROGRESS]**
- `get_game_stats.py` : collect games details based on games dataset

Also this is the script that will get all new games (but you need old datasets available on Kaggle here : [dataset link](https://www.kaggle.com/nathanlauga/nba-games)) and don't forget to put it in data folder and to indicate it into the script :
- `get_new_games.py`

## 2. Format data

You can find the script that format data into `scripts` foled : 

- `format_games_for_model.py` : format dataset for the model


## 3. Create model

**[WORK IN PROGRESS]**

## 4. Automatize data collection


## 5. Predict on next games (real)


Thanks for reading,
*Nathan*