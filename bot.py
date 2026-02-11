import discord
from discord.ext import commands
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_THRESHOLD = timedelta(days=13, hours=20)

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

@bot.event
async def on_ready():
    print("Komornik online")
    ch = bot.get_channel(CHANNEL)
    progress_msg = await ch.send("⏳ Wczytywanie domków: 0/0")

    def progress_callback(done, total):
        # edytuje wiadomość co kilka sekund
        bot.loop.create_task(progress_msg.edit(content=f"⏳ Wczytywanie domków: {done}/{total}"))

    scrape(progress_callback)

    await progress_msg.edit(content=f"✅ Wczytano {count_houses()} domków")

    # wyświetlamy domki offline ≥ 13d20h
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            await ch.send(
                f"🔥 **Domek offline ≥13d20h**\n"
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

bot.run(TOKEN)
