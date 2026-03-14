# JuBot VPS Installation Guide

## Prerequisites

- A Linux VPS (Ubuntu 22.04+ or Debian 12+ recommended)
- Python 3.11+
- Git
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- Server Members Intent enabled in the bot's Discord Developer Portal settings

## 1. Create a dedicated user

```bash
sudo useradd -r -m -d /opt/jubot -s /bin/bash jubot
```

## 2. Clone the repository

```bash
sudo -u jubot git clone https://github.com/octogun89mm/JuBot.git /opt/jubot
```

## 3. Set up the Python environment

```bash
cd /opt/jubot
sudo -u jubot python3 -m venv .venv
sudo -u jubot .venv/bin/pip install -r requirements.txt
```

JuBot requires Python 3.9+ because it uses `discord.py 2.6.4`. Python 3.11+ is the recommended target for the VPS.

## 4. Configure environment variables

```bash
sudo cp .env.example /opt/jubot/.env
sudo chown jubot:jubot /opt/jubot/.env
sudo chmod 600 /opt/jubot/.env
```

Edit `/opt/jubot/.env` and fill in the real values:

```
DISCORD_TOKEN=your_token_here
ADMIN_ROLE_ID=your_role_id
ALLOWED_CHANNEL_IDS=channel_id_1,channel_id_2
WELCOME_CHANNEL_ID=1406518392541810731
```

## 5. Install the systemd service

```bash
sudo cp /opt/jubot/deploy/jubot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jubot
sudo systemctl start jubot
```

## 6. Verify it's running

```bash
sudo systemctl status jubot
sudo journalctl -u jubot -f
```

You should see `Logged in as JuBot#XXXX` in the journal output.

## Updating the bot

```bash
cd /opt/jubot
sudo -u jubot git pull
sudo -u jubot .venv/bin/pip install -r requirements.txt
sudo systemctl restart jubot
```

## Viewing logs

```bash
# Live tail
sudo journalctl -u jubot -f

# Last 100 lines
sudo journalctl -u jubot -n 100

# Since last boot
sudo journalctl -u jubot -b
```

## Troubleshooting

| Symptom | Check |
|---|---|
| Bot doesn't start | `journalctl -u jubot -e` for error output |
| Bot starts but no welcome messages | Verify Server Members Intent is ON in Developer Portal |
| `WELCOME_CHANNEL_ID not found` in logs | Bot lacks access to that channel — check role permissions |
| Bot crashes and doesn't restart | `systemctl status jubot` — systemd restarts after 10s on failure |
| Permission denied on `.env` | Ensure `jubot` user owns the file: `chown jubot:jubot /opt/jubot/.env` |
