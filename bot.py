import os
import discord
import requests
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL = int(os.getenv("ALERT_CHANNEL_ID"))

intents = discord.Intents.default()
class Komornik(discord.Client):
    async def setup_hook(self):
        self.loop.create_task(alert_loop())

bot = Komornik(intents=intents)


URL = "https://cyleria.pl/?subtopic=houses"
BASE = "https://cyleria.pl/"

TIMEZONE = pytz.timezone("Europe/Warsaw")

# -------------------------
# SCRAPER
# -------------------------

def fetch_houses():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"class": "TableContent"})

    houses = []

    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")

        owner = tds[1].text.strip()
        city = tds[2].text.strip()

        link_tag = tds[3].find("a")
        house_link = BASE + link_tag["href"]

        img_tag = tds[3].find("img")
        img = BASE + img_tag["src"]

        address = tds[3].text.strip()
        sqm = tds[4].text.strip()
        last_login = tds[5].text.strip()

        try:
            last = datetime.strptime(last_login, "%d %b %Y, %H:%M")
            last = TIMEZONE.localize(last)
        except:
            continue

        houses.append({
            "owner": owner,
            "city": city,
            "address": address,
            "sqm": sqm,
            "last": last,
            "img": img,
            "link": house_link
        })

    return houses

# -------------------------
# SORT
# -------------------------

def get_oldest(houses, city=None):
    if city:
        houses = [h for h in houses if h["city"].lower() == city.lower()]

    houses.sort(key=lambda x: x["last"])
    return houses[:5]

# -------------------------
# EMBED
# -------------------------

def make_embed(h):
    days = (datetime.now(TIMEZONE) - h["last"]).days

    e = discord.Embed(
        title=h["owner"],
        description=f"**Miasto:** {h['city']}\n**Adres:** {h['address']}\n**SQM:** {h['sqm']}\n**Offline:** {days} dni",
        url=h["link"],
        color=0x8B0000
    )
    e.set_thumbnail(url=h["img"])
    return e

# -------------------------
# COMMANDS
# -------------------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    cmd = message.content.lower()

    houses = fetch_houses()

    if cmd == "!info":
        await message.channel.send(
            "**Komornik — komendy:**\n"
            "`!sprawdz` – 5 najdłużej offline z każdego miasta\n"
            "`!Cyleria` `!Celestial` `!Volcano` `!Ankardia` `!Dekane` `!Olimpus`"
        )

    elif cmd == "!sprawdz":
        cities = set(h["city"] for h in houses)
        for city in cities:
            await message.channel.send(f"🏠 **{city}**")
            for h in get_oldest(houses, city):
                await message.channel.send(embed=make_embed(h))

    else:
        for city in ["cyleria", "celestial", "volcano", "ankardia", "dekane", "olimpus"]:
            if cmd == f"!{city}":
                await message.channel.send(f"🏠 **{city.capitalize()}**")
                for h in get_oldest(houses, city):
                    await message.channel.send(embed=make_embed(h))

# -------------------------
# ALERT SYSTEM
# -------------------------

async def alert_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(ALERT_CHANNEL)

    while True:
        houses = fetch_houses()
        now = datetime.now(TIMEZONE)

        for h in houses:
            days = (now - h["last"]).days
            if days >= 10:
                embed = make_embed(h)
                embed.title = "⚠️ DŁUGO OFFLINE"
                await channel.send(embed=embed)

        await asyncio.sleep(3600)  # co 1 godzinę

bot.run(TOKEN)
