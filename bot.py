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

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

def hours_offline(date):
    if not date:
        return 0
    return (datetime.utcnow() - date).total_seconds() / 3600

@bot.event
async def on_ready():
    print("Komornik online")
    scrape()
    channel = bot.get_channel(CHANNEL)
    await channel.send(f"📊 Komornik wczytał **{count_houses()}** domków do cache.")
    monitor.start()

@tasks.loop(minutes=15)
async def monitor():
    scrape()

@bot.command()
async def info(ctx):
    await ctx.send(
        "**Komendy Komornika:**\n"
        "`!status` → ile domków jest w cache\n"
        "`!10dni` → domki gdzie właściciel offline ≥10 dni\n"
        "`!fast` → domki gdzie offline ≥13 dni 20h\n"
    )

@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest **{count_houses()}** domków.")

@bot.command(name="10dni")
async def tendays(ctx):
    data = get_all()
    for h in data:
        dt = parse_date(h[6])
        if not dt:
            continue
        if hours_offline(dt) >= 240:
            await ctx.send(
                f"🏚️ **{h[1]} ({h[2]})**\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

@bot.command()
async def fast(ctx):
    data = get_all()
    for h in data:
        dt = parse_date(h[6])
        if not dt:
            continue
        if hours_offline(dt) >= (13*24 + 20):
            await ctx.send(
                f"🔥 **FAST CLAIM**\n"
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

bot.run(TOKEN)
