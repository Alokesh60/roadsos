import sqlite3

from datetime import datetime

from app.db.sqlite_db import (
    get_connection
)

from app.services.distance_service import (
    calculate_distance
)


# =====================================
# SQLITE ROW FACTORY
# =====================================

def dict_factory(
    cursor,
    row
):

    return {

        col[0]: row[idx]

        for idx, col in enumerate(
            cursor.description
        )
    }


# =====================================
# FETCH ALL SERVICE POINTS
# =====================================

def get_all_services():

    conn = get_connection()

    conn.row_factory = dict_factory

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM service_points"
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================
# SEARCH SERVICES
# =====================================

def search_services(query: str):

    conn = get_connection()

    conn.row_factory = dict_factory

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT * FROM service_points

        WHERE

            name LIKE ?

            OR address LIKE ?

            OR district LIKE ?

            OR state LIKE ?

            OR country LIKE ?
        """,

        (

            f"%{query}%",

            f"%{query}%",

            f"%{query}%",

            f"%{query}%",

            f"%{query}%"
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================
# FILTER SERVICES
# =====================================

def get_services_by_type(
    service_type: str
):

    conn = get_connection()

    conn.row_factory = dict_factory

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT * FROM service_points

        WHERE service_type = ?
        """,

        (service_type,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================
# NEAREST SERVICES
# =====================================

def get_nearest_services(

    latitude: float,

    longitude: float,

    service_type: str,

    radius_km: float = 20
):

    services = get_services_by_type(
        service_type
    )

    nearby = []

    for service in services:

        lat = service.get(
            "latitude"
        )

        lon = service.get(
            "longitude"
        )

        if (

            lat is None

            or

            lon is None
        ):

            continue

        distance = calculate_distance(

            latitude,

            longitude,

            lat,

            lon
        )

        if distance <= radius_km:

            service["distance_km"] = round(
                distance,
                2
            )

            nearby.append(service)

    nearby.sort(

        key=lambda x: (
            x["distance_km"]
        )
    )

    return nearby


# =====================================
# CACHE LIVE SERVICES
# =====================================

def save_live_services_to_sqlite(
    services: list
):

    conn = get_connection()

    cursor = conn.cursor()

    for service in services:

        latitude = service.get(
            "latitude"
        )

        longitude = service.get(
            "longitude"
        )

        if (

            latitude is None

            or

            longitude is None
        ):

            continue

        # =============================
        # DUPLICATE CHECK
        # =============================

        cursor.execute(

            """
            SELECT id

            FROM cached_services

            WHERE

                name = ?

                AND latitude = ?

                AND longitude = ?
            """,

            (

                service.get("name"),

                latitude,

                longitude
            )
        )

        exists = cursor.fetchone()

        if exists:
            continue

        # =============================
        # INSERT CACHE
        # =============================

        cursor.execute(

            """
            INSERT INTO cached_services (

                name,

                service_type,

                latitude,

                longitude,

                source,

                cached_at

            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (

                service.get("name"),

                service.get(
                    "service_type",

                    service.get("service_type")
                ),

                latitude,

                longitude,

                service.get(
                    "source",
                    "google_places"
                ),

                datetime.now().isoformat()
            )
        )

    conn.commit()

    conn.close()


# =====================================
# CLEANUP FAR CACHE
# =====================================

def cleanup_far_services(

    current_lat: float,

    current_lon: float,

    keep_radius_km: float = 50
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT

            id,

            latitude,

            longitude

        FROM cached_services
        """
    )

    services = cursor.fetchall()

    deleted_count = 0

    for service in services:

        service_id = service[0]

        lat = service[1]

        lon = service[2]

        if (

            lat is None

            or

            lon is None
        ):

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
                DELETE FROM cached_services

                WHERE id = ?
                """,

                (service_id,)
            )

            deleted_count += 1

    conn.commit()

    conn.close()

    print(

        f"Deleted "
        f"{deleted_count} "
        f"cached services"
    )


# =====================================
# SAVE SOS EVENT
# =====================================

def save_sos_event(

    user_id: str,

    message: str,

    detected_type: str,

    latitude: float,

    longitude: float,

    priority: str
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO sos_events (

            user_id,

            message,

            detected_type,

            latitude,

            longitude,

            priority,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        (

            user_id,

            message,

            detected_type,

            latitude,

            longitude,

            priority,

            datetime.now().isoformat()
        )
    )

    conn.commit()

    conn.close()