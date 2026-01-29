import discord
from config import game_list_path, token_path, commands
from utils import isUserAdmin, isValidGameName, write_to_game_list_file, getHelpCommand

# Discord client handling
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Game list handling
with open (game_list_path, "r") as game_list_file:
    game_list = game_list_file.read().splitlines()

# Token handling
with open(token_path, "r") as token:
    token = token.readline()
    token = token.strip()

# Input/Output logic
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Ping
    if message.content == commands["ping"]["command"]:
        await message.channel.send("pong")

    # Show game list
    if message.content == commands["show_game_list"]["command"]:
        separator = "\n"
        game_list_printable_format = separator.join(game_list)
        await message.channel.send(game_list_printable_format)

    # Add games
    if message.content.startswith(commands["add_game"]["command"]):
        if isUserAdmin(message.author.id) == False:
            await message.channel.send("You are not an administrator, you can't add or remove games from the game list.")
        else:
            command_length = len(commands["add_game"]["command"]) + 1
            message_suffix = message.content[command_length:]
            if isValidGameName(message_suffix) == False:
                await message.channel.send("Please enter a valid game title")
            elif message_suffix in game_list:
                await message.channel.send(f"Error: Game {message_suffix} cannot be added to game list, {message_suffix} is already in game list.")
            else:
                game_list.append(message_suffix)
                write_to_game_list_file(game_list)
                await message.channel.send(f"{message_suffix} has been added to the game list")
                print(f"{message_suffix} has been added to the game list file.")

    # Remove games
    if message.content.startswith(commands["remove_game"]["command"]):
        if isUserAdmin(message.author.id) == False:
            await message.channel.send("You are not an administrator, you can't add or remove games from the game list.")
        else:
            command_length = len(commands["remove_game"]["command"]) + 1
            message_suffix = message.content[command_length:]
            if isValidGameName(message_suffix) == False:
                await message.channel.send("Please enter a valid game title")
            elif message_suffix not in game_list:
                await message.channel.send(f"Error: Game {message_suffix} cannot be removed from game list, {message_suffix} is not in game list")
            else:
                game_list.remove(message_suffix)
                write_to_game_list_file(game_list)
                await message.channel.send(f"{message_suffix} has been removed from the game list")
                print(f"{message_suffix} has been removed from the game list file.")

    # Help
    if message.content.startswith(commands["help_command"]["command"]):
        await message.channel.send(f"{getHelpCommand(commands)}")

client.run(token)
