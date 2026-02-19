import json

from config import game_list_path, suggestions_path


def write_to_game_list_file(game_list):
    with open(game_list_path, "w") as game_list_file:
        json.dump(obj=game_list, fp=game_list_file, indent=2)


def read_from_game_list_file():
    try:
        with open(game_list_path, "r") as game_list_file:
            game_list = json.load(game_list_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    if isinstance(game_list, dict):
        return game_list
    return {}


def write_to_suggestions_file(suggestions):
    with open(suggestions_path, "w") as suggestions_file:
        json.dump(obj=suggestions, fp=suggestions_file, indent=2)


def read_from_suggestions_file():
    try:
        with open(suggestions_path, "r") as suggestions_file:
            suggestions = json.load(suggestions_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

    if isinstance(suggestions, list):
        return suggestions

    return []
