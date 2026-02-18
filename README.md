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

## Commands
- `>>ping` -> test if the bot responds
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
- [ ] Game suggestion command for users to suggest games (stored in a separate file)
