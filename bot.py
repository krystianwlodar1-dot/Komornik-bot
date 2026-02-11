import discord
from discord.ext import commands, tasks
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_HOURS = 13 * 24 + 20
alerted = set()

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

def hours_offline(date):
    return (datetime.utcnow() - date).total_seconds() / 3600

@bot.event
async def on_ready():
    print("Komornik online")
    scrape()
    ch = bot.get_channel(CHANNEL)
    await ch.send(f"📊 Komornik wczytał **{count_houses()}** domków do cache.")
    monitor.start()

@tasks.loop(minutes=15)
async def monitor():
    scrape()
    data = get_all()
    ch = bot.get_channel(CHANNEL)

    for h in data:
        house_id = h[0]
        last_login = parse_date(h[6])

        if not last_login:
            continue

        if hours_offline(last_login) >= FAST_HOURS:
            if house_id not in alerted:
                alerted.add(house_id)
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ **{h[1]} ({h[2]})**\n"
                    f"📐 {h[4]} sqm\n"
                    f"👤 {h[5]}\n"
