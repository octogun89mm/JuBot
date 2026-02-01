import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from config import game_list_path
from utils import write_to_game_list_file

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
bot = commands.Bot(command_prefix="!", intents=intents)

# Game list handling
with open(game_list_path, "r") as game_list_file:
    game_list = game_list_file.read().splitlines()

# Autorization Logic
def check_admin(ctx):
    return any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles)

# Logic
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    """
    Check if the bot responds.

    Check if the bot responds.
    Usage: !ping
    """
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")

@bot.command(name="jujusgames")
async def get_game_list(ctx):
    """
    Show a list of all the games that Juju plays!

    Show a list of all the games that Juju plays!
    Usage: !jujusgames
    """
    separator = "\n"
    game_list_printable_format = separator.join(game_list)
    await ctx.send(game_list_printable_format)

@bot.command(name="jujusgamesadd")
@commands.check(check_admin)
async def add_to_game_list(ctx, game):
    """
    Add a game to the game list. (Admins only)

    Add a game to the game list. (Admins only)
    The game must be written in double quotes, see usage and/or example for more information.
    Usage: !jujusgamesadd "<game_title>"
    Example: !jujusgamesadd "GTA V"
    """
    if game in game_list:
        await ctx.send(f"{game} is already in game list. It cannot be added.")
    else:
        game_list.append(game)
        write_to_game_list_file(game_list)
        await ctx.send(f"{game} has been added to game list!")
        print(f"{game} has been added to game list by {ctx.author.id}")

@bot.command(name="jujusgamesremove")
@commands.check(check_admin)
async def remove_from_game_list(ctx, game):
    """
    Remove a game from the game list. (Admins only)

    Remove a game from the game list. (Admins only)
    The game must be written in double quotes, see usage and/or example for more information.
    Usage: !jujusgamesremove "<game_title>"
    Example: !jujusgamesremove "GTA V"
    """
    if game not in game_list:
        await ctx.send(f"{game} is not in game list. It cannot be removed.")
    else:
        game_list.remove(game)
        write_to_game_list_file(game_list)
        await ctx.send(f"{game} has been removed from game list!")
        print(f"{game} has been removed from game list by {ctx.author.id}")

bot.run(DISCORD_TOKEN)
