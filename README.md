# JuBot

## Purpose
JuBot is a Discord bot that maintains and displays a manually curated
favorite game list for a Discord server using text commands.

## Scope
- Manual updates via Discord commands
- One server
- One game list
- No database
- No web UI

## Installation
1. Clone the repository and enter the project folder.
2. Create and activate a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Create a `.env` file with:
   - `DISCORD_TOKEN=<your_discord_bot_token>`
   - `ADMIN_ROLE_ID=<admin_role_id>`
   - `ALLOWED_CHANNEL_IDS=<channel_id_1>,<channel_id_2>`
5. Run the bot with `python bot/main.py`.

## Commands
- `>>ping` -> test if the bot responds
- `>>suggest "<game_name>"` -> suggest a game via Steam search (all users)
- `>>suggestions` -> list suggested games (admin only)
- `>>suggestions remove <number>` -> remove one suggestion (admin only)
- `>>suggestions clear` -> clear all suggestions (admin only)
- `>>jujusgames` -> show game list
- `>>jujusgames add <steam_id>` -> add a game by Steam app id (admin only)
- `>>jujusgames add "<game_name>"` -> search Steam by name, then add (admin only)
- `>>jujusgames remove <steam_id>` -> remove a game by Steam app id (admin only)
- `>>help` -> show available commands

## Data
- Stored as a dictionary keyed by Steam app id (string key)
- Each entry value contains:
  - `name`
  - `steam_link`
- Backed by a JSON file

## Milestones
- [x] Bot connects and responds
- [x] Static game list
- [x] File-backed storage
- [x] Add/remove commands
- [x] Single editable message
- [x] JSON storage
- [x] Subcommands to replace jujusgamesadd and jujusgamesremove (e.g. `>>jujusgames add`, `>>jujusgames remove`)
- [x] Add Steam links for each game
- [x] Game suggestion command for users to suggest games (stored in a separate file)
