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
- !ping -> test if the bot responds
- !jujusgames -> show game list
- !jujusgames add "<game>" -> add a game to the game list (admin only)
- !jujusgames remove "<game>" -> remove a game from the game list (admin only)
- !help -> show available commands

## Data
- Stored as a list of dictionaries
- Backed by a JSON file

## Milestones
- [x] Bot connects and responds
- [x] Static game list
- [x] File-backed storage
- [x] Add/remove commands
- [x] Single editable message
- [x] JSON storage
- [x] Subcommands to replace jujusgamesadd and jujusgamesremove (e.g. !jujusgames add, !jujusgames remove)
- [ ] Add Wikipedia and Steam links for each game
- [ ] Game suggestion command for users to suggest games (stored in a separate file)
