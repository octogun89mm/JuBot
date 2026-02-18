# flake8: noqa: E501
# ruff: noqa: E501
import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from steam_api import get_game_by_steam_id, search_games_by_name
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
pending_add_selections = {}


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
            f"{ctx.author.display_name}, some arguments are missing.\nIn this case `{error.param}`, for the command to run properly.\nPlease type `>>help` for more information."  # noqa: E501
        )
    else:
        print(f"Unhandled error: {type(error).__name__}: {error}")


# Command handling
@bot.command()
async def ping(ctx):
    """
    Check if the bot responds.

    Check if the bot responds.
    Usage: >>ping
    """
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")


@bot.group(name="jujusgames", invoke_without_command=True)
async def jujusgames(ctx):
    """
    Show a list of all the games that Juju plays! Also contains sub commands, see `>>help` for more info.

    Show a list of all the games that Juju plays!
    Usage: >>jujusgames

    Subcommands: `add` and `remove`
    """  # noqa: E501
    game_data = read_from_game_list_file()
    formatted_games = []
    for _, details in game_data.items():
        game_info = f"{details['name']}\n{details['steam_link']}"
        formatted_games.append(game_info)
    await ctx.send("\n\n".join(formatted_games))


async def add_game_by_steam_id(ctx, steam_id):
    game_data = read_from_game_list_file()
    steam_key = str(steam_id)
    if steam_key in game_data:
        await ctx.send(
            f"Steam app id {steam_id} is already in the game list. It cannot be added."
        )
        return

    game_info = get_game_by_steam_id(steam_id)
    if not game_info:
        await ctx.send(
            f"Could not find game info for Steam app id {steam_id}. Please check the id and try again."
        )
        return

    game_data[steam_key] = game_info
    write_to_game_list_file(game_data)
    await ctx.send(f"{game_info['name']} has been added to game list!")
    print(
        f"{game_info['name']} ({steam_id}) has been added to game list by {ctx.author.name} - {ctx.author.id}"
    )


@jujusgames.command(name="add")
@commands.check(check_admin)
async def add_to_game_list(ctx, *, game_query):
    """
    Add a game to the game list. (Admins only)

    Add a game to the game list. (Admins only)
    Add by Steam app id or search by name.
    Usage: >>jujusgames add <steam_id>
    Usage: >>jujusgames add "<game_name>"
    Example: >>jujusgames add 233860
    Example: >>jujusgames add "Kenshi"
    """  # noqa: E501
    cleaned_query = game_query.strip()
    if not cleaned_query:
        await ctx.send("Please provide a Steam app id or game name.")
        return

    if cleaned_query.isdigit():
        await add_game_by_steam_id(ctx, int(cleaned_query))
        return

    results = search_games_by_name(cleaned_query, limit=5)
    if not results:
        await ctx.send(
            f"No Steam results found for '{cleaned_query}'. Try a different name or use a Steam app id."
        )
        return

    if len(results) == 1:
        await add_game_by_steam_id(ctx, results[0]["steam_id"])
        return

    pending_key = (ctx.guild.id if ctx.guild else 0, ctx.channel.id, ctx.author.id)
    if pending_key in pending_add_selections:
        await ctx.send(
            "You already have a pending game selection in this channel. Reply with a number or 'cancel'."
        )
        return

    lines = [
        f"Multiple games found for '{cleaned_query}'. Reply with a number (1-{len(results)}) or 'cancel' within 30 seconds:"
    ]
    for index, item in enumerate(results, start=1):
        lines.append(f"{index}. {item['name']} (App ID: {item['steam_id']})")
    await ctx.send("\n".join(lines))

    pending_add_selections[pending_key] = True

    def selection_check(message):
        if message.author.id != ctx.author.id:
            return False
        if message.channel.id != ctx.channel.id:
            return False
        content = message.content.strip().lower()
        if content == "cancel":
            return True
        if content.isdigit():
            selected_index = int(content)
            return 1 <= selected_index <= len(results)
        return False

    try:
        reply = await bot.wait_for("message", check=selection_check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Selection timed out after 30 seconds. Run the command again.")
        return
    finally:
        pending_add_selections.pop(pending_key, None)

    content = reply.content.strip().lower()
    if content == "cancel":
        await ctx.send("Game selection canceled.")
        return

    selected_result = results[int(content) - 1]
    await add_game_by_steam_id(ctx, selected_result["steam_id"])

    print(
        f"Search selection completed for query '{cleaned_query}' by {ctx.author.name} - {ctx.author.id}"
    )


@jujusgames.command(name="remove")
@commands.check(check_admin)
async def remove_from_game_list(ctx, steam_id: int):
    """
    Remove a game from the game list. (Admins only)

    Remove a game from the game list. (Admins only)
    Remove by Steam app id.
    Usage: >>jujusgames remove <steam_id>
    Example: >>jujusgames remove 233860
    """  # noqa: E501
    game_data = read_from_game_list_file()
    steam_key = str(steam_id)
    if steam_key not in game_data:
        await ctx.send(
            f"Steam app id {steam_id} is not in game list. It cannot be removed."
        )
        return

    removed_game_name = game_data[steam_key]["name"]
    del game_data[steam_key]
    write_to_game_list_file(game_data)
    await ctx.send(f"{removed_game_name} has been removed from game list!")
    print(
        f"{removed_game_name} ({steam_id}) has been removed from game list by {ctx.author.name} - {ctx.author.id}"  # noqa: E501
    )


bot.run(DISCORD_TOKEN)
