import json
from config import game_list_path

def write_to_game_list_file(game_list):
    with open (game_list_path, "w") as game_list_file:
        json.dump(obj=game_list,fp=game_list_file)

def read_from_game_list_file():
    with open (game_list_path, "r") as game_list_file:
        game_list = json.load(game_list_file)
    return game_list
