# flake8: noqa: E501
# ruff: noqa: E501
import asyncio
import os
from datetime import datetime, timezone

import discord
from discord.ext import commands
from dotenv import load_dotenv
from steam_api import get_game_by_steam_id, search_games_by_name
from utils import (
    read_from_game_list_file,
    read_from_suggestions_file,
    write_to_game_list_file,
    write_to_suggestions_file,
)

load_dotenv()

# Configuration
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set")

ADMIN_ROLE_ID = os.environ.get("ADMIN_ROLE_ID")
if not ADMIN_ROLE_ID:
    raise ValueError("ADMIN_ROLE_ID environment variable not set")
ADMIN_ROLE_ID = int(ADMIN_ROLE_ID)

ALLOWED_CHANNEL_IDS_RAW = os.environ.get("ALLOWED_CHANNEL_IDS")
if not ALLOWED_CHANNEL_IDS_RAW:
    raise ValueError("ALLOWED_CHANNEL_IDS environment variable not set")
try:
    ALLOWED_CHANNEL_IDS = {
        int(channel_id.strip())
        for channel_id in ALLOWED_CHANNEL_IDS_RAW.split(",")
        if channel_id.strip()
    }
except ValueError as error:
    raise ValueError(
        "ALLOWED_CHANNEL_IDS must be a comma-separated list of integers"
    ) from error
if not ALLOWED_CHANNEL_IDS:
    raise ValueError("ALLOWED_CHANNEL_IDS must contain at least one channel id")

# Discord client handling
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=">>", intents=intents)
pending_selections = {}


# Authorization Logic
class NotAllowedChannel(commands.CheckFailure):
    pass


def check_admin(ctx):
    return any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles)


@bot.check
async def check_allowed_channel(ctx):
    if ctx.channel.id in ALLOWED_CHANNEL_IDS:
        return True
    raise NotAllowedChannel


# Event handling
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, NotAllowedChannel):
        allowed_channel_mentions = ", ".join(
            f"<#{channel_id}>" for channel_id in ALLOWED_CHANNEL_IDS
        )
        await ctx.send(
            f"{ctx.author.display_name}, commands are only allowed in: {allowed_channel_mentions}"
        )
    elif isinstance(error, commands.CheckFailure):
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


@bot.command(name="suggest")
async def suggest_game(ctx, *, game_name):
    """
    Suggest a game for Juju to play.

    Usage: >>suggest "<game_name>"
    """
    cleaned_name = game_name.strip()
    if not cleaned_name:
        await ctx.send("Please provide a game name.")
        return

    if cleaned_name.isdigit():
        steam_id = int(cleaned_name)
        game_info = await get_game_by_steam_id(steam_id)
        if not game_info:
            await ctx.send(
                f"Could not find game info for Steam app id {steam_id}. Please check the id and try again."
            )
            return
        selected_game = {
            "steam_id": steam_id,
            "name": game_info["name"],
            "steam_link": game_info["steam_link"],
        }
    else:
        results = await search_games_by_name(cleaned_name, limit=5)
        if not results:
            await ctx.send(
                f"No Steam results found for '{cleaned_name}'. Try a different name."
            )
            return

        if len(results) == 1:
            selected_game = results[0]
        else:
            pending_key = (
                "suggest",
                ctx.guild.id if ctx.guild else 0,
                ctx.channel.id,
                ctx.author.id,
            )
            if pending_key in pending_selections:
                await ctx.send(
                    "You already have a pending suggestion selection in this channel. Reply with a number or 'cancel'."
                )
                return

            lines = [
                f"Multiple games found for '{cleaned_name}'. Reply with a number (1-{len(results)}) or 'cancel' within 30 seconds:"
            ]
            for index, item in enumerate(results, start=1):
                lines.append(f"{index}. {item['name']} (App ID: {item['steam_id']})")
            await ctx.send("\n".join(lines))

            pending_selections[pending_key] = True

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
                await ctx.send(
                    "Suggestion selection timed out after 30 seconds. Run the command again."
                )
                return
            finally:
                pending_selections.pop(pending_key, None)

            content = reply.content.strip().lower()
            if content == "cancel":
                await ctx.send("Suggestion selection canceled.")
                return

            selected_game = results[int(content) - 1]

    suggestions = read_from_suggestions_file()
    already_suggested = any(
        str(item.get("steam_id")) == str(selected_game["steam_id"])
        for item in suggestions
    )
    if already_suggested:
        await ctx.send(f"'{selected_game['name']}' was already suggested.")
        return

    suggestion = {
        "game_name": selected_game["name"],
        "steam_id": selected_game["steam_id"],
        "steam_link": selected_game["steam_link"],
        "suggested_by_id": ctx.author.id,
        "suggested_by_name": ctx.author.display_name,
        "suggested_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    suggestions.append(suggestion)
    write_to_suggestions_file(suggestions)
    await ctx.send(
        f"Suggestion received: {selected_game['name']}\n{selected_game['steam_link']}"
    )


@bot.group(name="suggestions", invoke_without_command=True)
@commands.check(check_admin)
async def list_suggestions(ctx):
    """
    Show suggested games. (Admins only)

    Usage: >>suggestions
    """
    suggestions = read_from_suggestions_file()
    if not suggestions:
        await ctx.send("No suggestions yet.")
        return

    lines = ["Suggested games:"]
    for index, item in enumerate(suggestions[:25], start=1):
        lines.append(
            f"{index}. {item.get('game_name', 'Unknown')} (App ID: {item.get('steam_id', 'Unknown')}) (by {item.get('suggested_by_name', 'Unknown')})"
        )
        lines.append(f"   {item.get('steam_link', 'No link available')}")

    if len(suggestions) > 25:
        lines.append(f"...and {len(suggestions) - 25} more")

    await ctx.send("\n".join(lines))


@list_suggestions.command(name="remove")
@commands.check(check_admin)
async def remove_suggestion(ctx, number: int):
    """
    Remove one suggestion by its list number. (Admins only)

    Usage: >>suggestions remove <number>
    """
    suggestions = read_from_suggestions_file()
    if not suggestions:
        await ctx.send("No suggestions to remove.")
        return

    if number < 1 or number > len(suggestions):
        await ctx.send(
            f"Invalid suggestion number. Use a value between 1 and {len(suggestions)}."
        )
        return

    removed = suggestions.pop(number - 1)
    write_to_suggestions_file(suggestions)
    await ctx.send(
        f"Removed suggestion: {removed.get('game_name', 'Unknown')} (App ID: {removed.get('steam_id', 'Unknown')})"
    )


@list_suggestions.command(name="clear")
@commands.check(check_admin)
async def clear_suggestions(ctx):
    """
    Clear all suggestions. (Admins only)

    Usage: >>suggestions clear
    """
    write_to_suggestions_file([])
    await ctx.send("All suggestions have been cleared.")


@bot.group(name="jujusgames", invoke_without_command=True)
async def jujusgames(ctx):
    """
    Show a list of all the games that Juju plays! Also contains sub commands, see `>>help` for more info.

    Show a list of all the games that Juju plays!
    Usage: >>jujusgames

    Subcommands: `add` and `remove`
    """  # noqa: E501
    game_data = read_from_game_list_file()
    if not game_data:
        await ctx.send("No games in the list yet.")
        return
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

    game_info = await get_game_by_steam_id(steam_id)
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

    results = await search_games_by_name(cleaned_query, limit=5)
    if not results:
        await ctx.send(
            f"No Steam results found for '{cleaned_query}'. Try a different name or use a Steam app id."
        )
        return

    if len(results) == 1:
        await add_game_by_steam_id(ctx, results[0]["steam_id"])
        return

    pending_key = ("add", ctx.guild.id if ctx.guild else 0, ctx.channel.id, ctx.author.id)
    if pending_key in pending_selections:
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

    pending_selections[pending_key] = True

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
        pending_selections.pop(pending_key, None)

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
