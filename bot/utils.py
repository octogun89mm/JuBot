from config import game_list_path, user_id_path

def write_to_game_list_file(game_list):
    with open (game_list_path, "w") as game_list_file:
        separator = "\n"
        game_list_printable_format = separator.join(game_list)
        game_list_file.write(game_list_printable_format)

def is_user_admin (user_id):
    with open (user_id_path, "r") as user_id_file:
        user_id_file = user_id_file.readline()
        user_id_file = user_id_file.strip()
        user_id = str(user_id)
        return user_id == user_id_file
