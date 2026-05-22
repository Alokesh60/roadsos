from app.db.sqlite_db import get_connection


def get_all_services():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM emergency_services"
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def search_services(query: str):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM emergency_services
        WHERE name LIKE ?
        """,
        (f"%{query}%",)
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]