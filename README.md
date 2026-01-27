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
- !games -> show game list
- !add <game> -> add a game to the game list
- !remove <game> -> remove a game from the game list

## Data
- Stored as a simple list of strings
- Backed by a JSON file

## Milestones
- [x] Bot connects and responds
- [x] Static game list
- [x] File-backed storage
- [x] Add/remove commands
- [x] Single editable message
