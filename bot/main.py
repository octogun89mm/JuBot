import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import read_from_game_list_file, write_to_game_list_file

load_dotenv()

# Configuration
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set")

ADMIN_ROLE_ID = os.environ.get("ADMIN_ROLE_ID")
if not ADMIN_ROLE_ID:
    raise ValueError("ADMIN_ROLE_ID environment variable not set")
ADMIN_ROLE_ID = int(ADMIN_ROLE_ID)

# Discord client handling
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=">>", intents=intents)


# Authorization Logic
def check_admin(ctx):
    return any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles)


# Event handling
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(
            f"{ctx.author.display_name}, only admins are allowed to use this command."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"{ctx.author.display_name}, some arguments are missing.\nIn this case `{error.param}`, for the command to run properly.\nPlease type `!help` for more information."  # noqa: E501
        )
    else:
        print(f"Unhandled error: {type(error).__name__}: {error}")


# Command handling
@bot.command()
async def ping(ctx):
    """
    Check if the bot responds.

    Check if the bot responds.
    Usage: !ping
    """
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")


@bot.group(name="jujusgames", invoke_without_command=True)
async def jujusgames(ctx):
    """
    Show a list of all the games that Juju plays! Also contains sub commands, see `!help` for more info.

    Show a list of all the games that Juju plays!
    Usage: !jujusgames

    Subcommands: `add` and `remove`
    """  # noqa: E501
    game_names = [game_item["name"] for game_item in read_from_game_list_file()]
    await ctx.send("\n".join(game_names))


@jujusgames.command(name="add")
@commands.check(check_admin)
async def add_to_game_list(ctx, game):
    """
    Add a game to the game list. (Admins only)

    Add a game to the game list. (Admins only)
    The game must be written in double quotes, see usage and/or example for more information.
    Usage: !jujusgames add "<game_title>"
    Example: !jujusgames add "GTA V"
    """  # noqa: E501
    if game in [game_item["name"] for game_item in read_from_game_list_file()]:
        await ctx.send(f"{game} is already in game list. It cannot be added.")
    else:
        game_list = read_from_game_list_file()
        game_list.append({"name": game})
        write_to_game_list_file(game_list)
        await ctx.send(f"{game} has been added to game list!")
        print(
            f"{game} has been added to game list by {ctx.author.name} - {ctx.author.id}"
        )


@jujusgames.command(name="remove")
@commands.check(check_admin)
async def remove_from_game_list(ctx, game):
    """
    Remove a game from the game list. (Admins only)

    Remove a game from the game list. (Admins only)
    The game must be written in double quotes, see usage and/or example for more information.
    Usage: !jujusgames remove "<game_title>"
    Example: !jujusgames remove "GTA V"
    """  # noqa: E501
    if game not in [game_item["name"] for game_item in read_from_game_list_file()]:
        await ctx.send(f"{game} is not in game list. It cannot be removed.")
    else:
        new_game_list = [
            game_item
            for game_item in read_from_game_list_file()
            if game_item["name"] != game
        ]
        write_to_game_list_file(new_game_list)
        await ctx.send(f"{game} has been removed from game list!")
        print(
            f"{game} has been removed from game list by {ctx.author.name} - {ctx.author.id}"  # noqa: E501
        )


bot.run(DISCORD_TOKEN)
