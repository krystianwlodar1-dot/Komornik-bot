import discord
from discord.ext import tasks, commands
from scraper import scrape
from database import get_all
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@tasks.loop(minutes=10)
async def monitor():
    scrape()
    data = get_all()

    channel = bot.get_channel(CHANNEL)

    for h in data:
        owner = h[5]
        last_login = h[6]

        if owner == "None":
            await channel.send(f"🏚️ **{h[1]} ({h[2]})** jest wolny!\n{h[3]}")
        elif "2026" not in last_login:
            await channel.send(
                f"⚠️ **{h[1]} ({h[2]})**\n"
                f"👤 {owner}\n"
                f"🕒 Ostatni login: {last_login}\n"
                f"{h[3]}"
            )

@bot.event
async def on_ready():
    print("Komornik online")
    monitor.start()

bot.run(TOKEN)
