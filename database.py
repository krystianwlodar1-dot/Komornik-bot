import sqlite3
from datetime import datetime

db = sqlite3.connect("houses.db", check_same_thread=False)
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS houses (
    house_id INTEGER PRIMARY KEY,
    address TEXT,
    city TEXT,
    map_image TEXT,
    size INTEGER,
    owner TEXT,
    last_login TEXT,
    last_seen TEXT
)
""")
db.commit()

def save_house(h):
    c.execute("""
    INSERT INTO houses VALUES (?,?,?,?,?,?,?,?)
    ON CONFLICT(house_id) DO UPDATE SET
      owner=excluded.owner,
      last_login=excluded.last_login,
      last_seen=excluded.last_seen
    """, (
        h["house_id"], h["address"], h["city"], h["map_image"],
        h["size"], h["owner"], h["last_login"], h["last_seen"]
    ))
    db.commit()

def get_all():
    return c.execute("SELECT * FROM houses").fetchall()

def count_houses():
    return c.execute("SELECT COUNT(*) FROM houses").fetchone()[0]
