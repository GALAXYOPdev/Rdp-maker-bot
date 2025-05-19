# Discord RDP Bot

A Discord bot that creates Dockerized RDP instances for users with slash commands.

## Features

- Create RDP with `/create_rdp password: expiry_hours:`
- Delete your RDP with `/delete_rdp`
- Auto-remove expired RDP containers
- No external database needed (in-memory)

## Setup

1. Clone this repo:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

2. Replace your Discord bot token and server IP in bot.py.


3. Build the Docker image for RDP:



docker build -t ubuntu-rdp .

4. Install Python dependencies:



pip install -r requirements.txt

5. Run the bot:



python bot.py

Notes

Requires Docker installed and running.

Make sure your bot has appropriate permissions and intents.


Credits

Created and maintained by GalaxyOP.

No credits = no update of the bot.
