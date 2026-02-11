import requests
from bs4 import BeautifulSoup
from database import save_house
from datetime import datetime

BASE = "https://cyleria.pl"

def get_last_login(name):
    url = f"{BASE}/?subtopic=characters&name={name}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    li = soup.find("li", class_="list-group-item")
    if li:
        strong = li.find("strong")
        return strong.text.strip()
    return "Unknown"

def scrape():
    html = requests.get(f"{BASE}/?subtopic=houses").text
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("table tr")[1:]

    for r in rows:
        tds = r.find_all("td")
        if len(tds) < 4:
            continue

        address = tds[0].text.strip()
        pop = tds[0].find("span")

        map_img = None
        city = None
        house_id = None

        if pop:
            sub = BeautifulSoup(pop["data-bs-content"], "lxml")
            img = sub.find("img")
            div = sub.find("div", class_="mt-2")

            map_img = img["src"]
            city = div.text
            house_id = int(map_img.split("/")[-1].replace(".png",""))

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
