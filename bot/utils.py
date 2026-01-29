from config import game_list_path, user_id_path

# Reusable functions
def write_to_game_list_file(game_list):
    with open (game_list_path, "w") as game_list_file:
        separator = "\n"
        game_list_printable_format = separator.join(game_list)
        game_list_file.write(game_list_printable_format)

def isUserAdmin (user_id):
    with open (user_id_path, "r") as user_id_file:
        user_id_file = user_id_file.readline()
        user_id_file = user_id_file.strip()
        user_id = str(user_id)
        if user_id != user_id_file:
            return False
        if user_id == user_id_file:
            return True

def getHelpCommand(commands):
    lines = []
    for command_data in commands.values():
        lines.append(f"### {command_data['command']}\n  Description: {command_data['description']}\n  Usage: `{command_data['usage']}`")
    return "\n".join(lines)

def isValidGameName(message_suffix):
    message_suffix = message_suffix.strip()
    if not message_suffix:
        return False
    else:
        return True
