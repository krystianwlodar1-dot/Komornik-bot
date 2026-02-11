import discord
from discord.ext import commands
from scraper import scrape, get_all
from database import count_houses
from datetime import datetime, timedelta
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_THRESHOLD = timedelta(days=13, hours=20)
alerted_houses = set()  # pamięta które domki już wysłały alert

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

async def scrape_with_progress(ch):
    progress_msg = await ch.send("⏳ Wczytywanie domków: 0/0"_
