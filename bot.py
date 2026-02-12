import discord
from discord.ext import commands, tasks
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime, timedelta
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_THRESHOLD = timedelta(days=13, hours=20)
alerted_houses = set()  # domki, które już wysłały FAST alert

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

async def scrape_with_progress(ch):
    progress_msg = await ch.send("⏳ Wczytywanie domków: 0/…")

    def progress_callback(done, total):
        bot.loop.create_task(progress_msg.edit(content=f"⏳ Wczytywanie domków: {done}/{total}"))

    # uruchom scraper w osobnym wątku
    await asyncio.to_thread(scrape, progress_callback)
    await progress_msg.edit(content=f"✅ Wczytano {count_houses()} domków")

    await check_fast(ch)  # FAST alerty po starcie

async def check_fast(ch):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            if h[0] not in alerted_houses:
                alerted_houses.add(h[0])
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ {h[1]} ({h[2]})\n"
                    f"📐 {h[4]} sqm\n"
                    f"👤 {h[5]}\n"
                    f"🕒 {h[6]}\n"
                    f"🗺️ {h[3]}"
                )

# Automatyczny monitoring co 15 minut
@tasks.loop(minutes=15)
async def monitor():
    ch = bot.get_channel(CHANNEL)
    await asyncio.to_thread(scrape)  # scrapowanie w osobnym wątku
    await check_fast(ch)

@bot.event
async def on_ready():
    print("Komornik online")
    ch = bot.get_channel(CHANNEL)
    await scrape_with_progress(ch)
    monitor.start()  # start ciągłego monitoringu

@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

@bot.command()
async def listfast(ctx):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            await ctx.send(
                f"🔥 Domek offline ≥13d20h\n"
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

bot.run(TOKEN)
