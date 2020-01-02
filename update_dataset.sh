#!/bin/bash
today=$(date +'%Y-%m-%d')

echo 'Save data'
zip $PWD/data/save/save_$today.zip $PWD/data/*.csv

echo 'Get new games'
python $PWD'/scripts/get_new_games.py'
