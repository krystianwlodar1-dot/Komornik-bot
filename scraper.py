import requests
from bs4 import BeautifulSoup
from database import save_house
from datetime import datetime

BASE = "https://cyleria.pl"

def get_last_login(owner_name):
    url = f"{BASE}/?subtopic=characters&name={owner_name}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    strong = soup.find("strong")
    return strong.text.strip() if strong else "Unknown"

def scrape(progress_callback=None):
    html = requests.get(f"{BASE}/?subtopic=houses").text
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("table tr")[1:]  # pomijamy nagłówek

    total = len(rows)
    if progress_callback:
        progress_callback(0, total)  # startowy progress

    for i, r in enumerate(rows, start=1):
        tds = r.find_all("td")
        if len(tds) < 3:
            continue

        address = tds[0].text.strip()

        # pop-up z mapą
        pop = tds[0].find("span")
        map_img = None
        city = None
        house_id = None

        if pop:
            sub = BeautifulSoup(pop["data-bs-content"], "lxml")
            img = sub.find("img")
            div = sub.find("div", class_="mt-2")
            if img and div:
                map_img = img["src"]
                city = div.text.strip()
                house_id = int(map_img.split("/")[-1].replace(".png", ""))

        size = int(tds[1].text.strip())
        owner = tds[2].text.strip()
        last_login = get_last_login(owner) if owner != "None" else "None"

        save_house({
            "house_id": house_id,
            "address": address,
            "city": city,
            "map_image": map_img,
            "size": size,
            "owner": owner,
            "last_login": last_login,
            "last_seen": datetime.utcnow().isoformat()
        })

        if progress_callback:
            progress_callback(i, total)
