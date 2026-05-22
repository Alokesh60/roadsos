import sqlite3
from app.db.sqlite_db import get_connection

from app.db.sqlite_db import get_connection

from app.services.distance_service import (
    calculate_distance
)

def cleanup_far_services(

    current_lat: float,

    current_lon: float,

    keep_radius_km: float = 50

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, latitude, longitude FROM emergency_services"
    )

    services = cursor.fetchall()

    deleted_count = 0

    for service in services:

        service_id = service[0]

        lat = service[1]

        lon = service[2]

        if lat is None or lon is None:
            continue

        distance = calculate_distance(

            current_lat,

            current_lon,

            lat,

            lon
        )

        if distance > keep_radius_km:

            cursor.execute(

                """
                DELETE FROM emergency_services
                WHERE id = ?
                """,

                (service_id,)
            )

            deleted_count += 1

    conn.commit()

    conn.close()

    print(
        f"Deleted {deleted_count} far cached services"
    )

def save_live_services_to_sqlite(
    services: list
):

    conn = get_connection()

    cursor = conn.cursor()

    for service in services:

        # skip invalid coordinates
        if (
            service.get("latitude") is None
            or
            service.get("longitude") is None
        ):
            continue

        # duplicate check
        cursor.execute(

            """
            SELECT id FROM emergency_services
            WHERE
                name = ?
                AND latitude = ?
                AND longitude = ?
            """,

            (
                service.get("name"),

                service.get("latitude"),

                service.get("longitude")
            )
        )

        exists = cursor.fetchone()

        if exists:
            continue

        cursor.execute(

            """
            INSERT INTO emergency_services (

                name,
                type,
                latitude,
                longitude,
                phone,
                address,
                city,
                state,
                country,
                rating,
                response_time_min,
                is_available,
                services_offered,
                last_verified

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (

                service.get("name"),

                service.get("type"),

                service.get("latitude"),

                service.get("longitude"),

                service.get("phone", "N/A"),

                service.get("address", "Unknown"),

                service.get("city", "Unknown"),

                service.get("state", "Unknown"),

                service.get("country", "India"),

                service.get("rating", 4.0),

                service.get("response_time_min", 10),

                1,

                service.get(
                    "services_offered",
                    service.get("type")
                ),

                "2026-05-22"
            )
        )

    conn.commit()

    conn.close()

def get_all_services():

    conn = get_connection()

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM emergency_services"
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def search_services(query: str):

    conn = get_connection()

    conn.row_factory = sqlite3.Row

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