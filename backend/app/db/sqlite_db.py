import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DATABASE_NAME = os.path.join(
    BASE_DIR,
    "roadsos.db"
)

def get_connection():

    conn = sqlite3.connect(DATABASE_NAME)

    conn.row_factory = sqlite3.Row

    return conn