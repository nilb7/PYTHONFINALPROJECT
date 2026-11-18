import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "safe_city.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

DEMO_REPORTS = [
    ("Overflowing trash containers", "trash",
     "The containers have not been emptied for days and garbage is spreading onto the sidewalk.",
     42.6602, 21.1631, "open", "2026-11-03 09:15:00"),
    ("Large pothole on the boulevard", "road",
     "A deep pothole in the right lane that is dangerous for cars and motorcycles.",
     42.6617, 21.1583, "open", "2026-11-05 14:40:00"),
    ("Streetlight not working", "light",
     "The whole street is dark in the evening, pedestrians cannot see the road.",
     42.6489, 21.1538, "open", "2026-11-06 18:20:00"),
    ("Illegal dump near the park", "trash",
     "Construction waste and old furniture have been thrown next to the walking path.",
     42.6711, 21.1985, "open", "2026-11-08 11:05:00"),
    ("Broken sidewalk tiles", "road",
     "Many tiles are broken and loose, people with strollers cannot pass.",
     42.6478, 21.1702, "resolved", "2026-10-28 08:30:00"),
    ("Sewage water on the street", "water",
     "Dirty water is coming out of a manhole and smells very bad.",
     42.6431, 21.1769, "open", "2026-11-10 16:10:00"),
    ("Cars parked on the pedestrian crossing", "traffic",
     "Every morning cars block the crossing in front of the school.",
     42.6559, 21.1412, "open", "2026-11-12 07:50:00"),
    ("Streetlight flickering all night", "light",
     "The light flickers constantly and is probably about to break completely.",
     42.6643, 21.1692, "resolved", "2026-10-30 20:00:00"),
]


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema = schema_file.read()
    connection = connect()
    connection.executescript(schema)
    user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        seed(connection)
    connection.commit()
    connection.close()


def seed(connection):
    cursor = connection.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        ("demo", "demo@safecity.test", generate_password_hash("demo123")),
    )
    demo_id = cursor.lastrowid
    for title, category, description, latitude, longitude, status, created_at in DEMO_REPORTS:
        connection.execute(
            "INSERT INTO reports (user_id, title, category, description, latitude, longitude, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (demo_id, title, category, description, latitude, longitude, status, created_at),
        )


if __name__ == "__main__":
    init_db()
    print("Database ready:", DB_PATH)
