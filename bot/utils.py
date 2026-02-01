from config import game_list_path

def write_to_game_list_file(game_list):
    with open (game_list_path, "w") as game_list_file:
        separator = "\n"
        game_list_printable_format = separator.join(game_list)
        game_list_file.write(game_list_printable_format)
