import os

# Files handling
script_dir = os.path.dirname(__file__)
token_path = os.path.join(script_dir, ".token")
user_id_path = os.path.join(script_dir, ".userid")
game_list_path = os.path.join(script_dir, "game_list.txt")

# Dictionary implementation for commands
commands_dict = {
    "ping" : {
        "command" : "!ping",
        "description" : "Test if the bot responds.",
        "usage": "!ping"
    },
    "show_game_list" : {
        "command" : "!jujusgames",
        "description" : "IN CONSTRUCTION! Prints the list of Juju's favorite games with web links for their Wikipedia and their Steam page.",
        "usage": "!jujusgames"
    },
    "add_game" : {
        "command" : "!jujusgamesadd",
        "description" : "Add a game to the game list. Note that only authorized accounts can add games to the game list.",
        "usage": "!jujusgamesadd <game title>"
    },
    "remove_game" : {
        "command" : "!jujusgamesremove",
        "description" : "Remove a game from the game list. Note that only authorized accounts can remove games from the game list.",
        "usage": "!jujusgamesremove <game title>"
    },
    "help_command" : {
        "command" : "!jubothelp",
        "description" : "Prints a list of all the commands available for JuBot!",
        "usage": "!jubothelp"
    }
}
