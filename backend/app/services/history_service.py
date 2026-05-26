import sqlite3

from app.db.sqlite_db import (
    get_connection
)


def get_emergency_history():

    conn = get_connection()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM emergency_logs

    ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]