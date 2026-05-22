import sqlite3
import os

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../"
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "roadsos.db"
)

def get_connection():

    return sqlite3.connect(DB_PATH)