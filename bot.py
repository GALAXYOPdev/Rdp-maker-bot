import discord, time
from discord import app_commands
from discord.ext import commands, tasks
import docker

# === Config ===
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
SERVER_IP = "YOUR_SERVER_PUBLIC_IP"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

client = docker.from_env()

# In-memory DB: user_id -> {docker, password, expiry}
rdp_db = {}

# --- Docker functions ---

def create_rdp_container(docker_name, password):
    try:
        # Remove existing container if exists
        try:
            old = client.containers.get(docker_name)
            old.stop()
            old.remove()
        except:
            pass
        
        container = client.containers.run(
            image="ubuntu-rdp",
            name=docker_name,
            detach=True,
            ports={'3389/tcp': None},
            tty=True
        )
        return container
    except Exception as e:
        return str(e)

def stop_rdp_container(docker_name):
    try:
        container = client.containers.get(docker_name)
        container.stop()
        container.remove()
    except:
        pass

def check_expired_rdps():
    current_time = int(time.time())
    to_delete = []
    for user_id, info in rdp_db.items():
        if info['expiry'] == 0:
            continue
        if current_time > info['expiry']:
            stop_rdp_container(info['docker'])
            to_delete.append(user_id)
    for uid in to_delete:
        del rdp_db[uid]

# --- Bot events & commands ---

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")
    expiry_loop.start()

@tasks.loop(minutes=1)
async def expiry_loop():
    check_expired_rdps()

@tree.command(name="create_rdp", description="Create your own RDP")
@app_commands.describe(password="Your desired RDP password", expiry_hours="Set 0 for unlimited")
async def create_rdp(interaction: discord.Interaction, password: str, expiry_hours: int = 24):
    user_id = interaction.user.id
    if user_id in rdp_db:
        await interaction.response.send_message("You already have an active RDP!", ephemeral=True)
        return

    docker_name = f"rdp_{user_id}"
    expiry_time = 0 if expiry_hours == 0 else int(time.time()) + expiry_hours * 3600

    container = create_rdp_container(docker_name, password)
    if isinstance(container, str):
        await interaction.response.send_message(f"Failed to create RDP: `{container}`", ephemeral=True)
        return

    rdp_db[user_id] = {"docker": docker_name, "password": password, "expiry": expiry_time}

    await interaction.user.send(f"""**[RDP CREATED SUCCESSFULLY]**
IP: `{SERVER_IP}`
PORT: `3389`
Username: `user`
Password: `{password}`
Expiry: {"Unlimited" if expiry_time == 0 else f"{expiry_hours} Hours"}""")
    await interaction.response.send_message("RDP created! Check your DMs.", ephemeral=True)

@tree.command(name="delete_rdp", description="Delete your active RDP")
async def delete_rdp(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in rdp_db:
        await interaction.response.send_message("You have no active RDP.", ephemeral=True)
        return

    stop_rdp_container(rdp_db[user_id]['docker'])
    del rdp_db[user_id]
    await interaction.response.send_message("Your RDP has been deleted.", ephemeral=True)

bot.run(TOKEN)
