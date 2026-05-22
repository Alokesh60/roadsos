import sqlite3
import os

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

DB_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "../ai/roadsos.db")
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn