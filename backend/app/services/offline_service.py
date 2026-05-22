import sqlite3

from app.services.supabase_service import get_all_services


def export_sqlite_database():

    services = get_all_services()

    conn = sqlite3.connect("roadsos_offline.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_services (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        latitude REAL,
        longitude REAL,
        rating REAL,
        availability BOOLEAN,
        verified BOOLEAN,
        source TEXT
    )
    """)

    cursor.execute("DELETE FROM emergency_services")

    for service in services:

        cursor.execute("""
        INSERT INTO emergency_services (
            id,
            name,
            type,
            phone,
            address,
            city,
            state,
            country,
            latitude,
            longitude,
            rating,
            availability,
            verified,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            service["id"],
            service["name"],
            service["type"],
            service["phone"],
            service["address"],
            service["city"],
            service["state"],
            service["country"],
            service["latitude"],
            service["longitude"],
            service["rating"],
            service["availability"],
            service["verified"],
            service["source"]
        ))

    conn.commit()

    conn.close()

    return "roadsos_offline.db"