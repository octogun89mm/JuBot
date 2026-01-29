import discord
from discord.ext import commands
from config import game_list_path, token_path, commands_dict
from utils import isUserAdmin, isValidGameName, write_to_game_list_file, getHelpCommand

# Discord client handling
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Game list handling
with open (game_list_path, "r") as game_list_file:
    game_list = game_list_file.read().splitlines()

# Token handling
with open(token_path, "r") as token:
    token = token.readline()
    token = token.strip()

# Autorization Logic
def check_admin(ctx):
    return isUserAdmin(ctx.author.id)

# Logic
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# TODO: Add an help description for each command, see https://discordpy-reborn.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Bot.description

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="jujusgames")
async def getGameList(ctx):
    separator = "\n"
    game_list_printable_format = separator.join(game_list)
    await ctx.send(game_list_printable_format)

@bot.command(name="jujusgamesadd")
@commands.check(check_admin)
async def addToGameList(ctx, game):
    if game in game_list:
        await ctx.send(f"{game} is already in game list. It cannot be added.")
    else:
        game_list.append(game)
        write_to_game_list_file(game_list)
        await ctx.send(f"{game} has been added to game list!")
        print(f"{game} has been added to game list by {ctx.author.id}")

@bot.command(name="jujusgamesremove")
@commands.check(check_admin)
async def removeFromGameList(ctx, game):
    if game not in game_list:
        await ctx.send(f"{game} is not in game list. It cannot be removed.")
    else:
        game_list.remove(game)
        write_to_game_list_file(game_list)
        await ctx.send(f"{game} has been removed from game list!")
        print(f"{game} has been removed from game list by {ctx.author.id}")

bot.run(token)
