import sqlite3
import json

from app.services.sqlite_service import (
    get_all_services
)

from app.utils.emergency_numbers import (
    get_all_emergency_numbers
)


# =====================================
# EXPORT OFFLINE SQLITE DATABASE
# =====================================

def export_sqlite_database():

    services = get_all_services()

    conn = sqlite3.connect(
        "roadsos_offline.db"
    )

    cursor = conn.cursor()

    # =================================
    # SERVICE POINTS
    # =================================

    cursor.execute(

        """
        CREATE TABLE IF NOT EXISTS service_points (

            id INTEGER PRIMARY KEY,

            name TEXT,

            service_type TEXT,

            phone TEXT,

            phone_source TEXT,

            address TEXT,

            district TEXT,

            state TEXT,

            country TEXT,

            postcode TEXT,

            latitude REAL,

            longitude REAL,

            operator TEXT,

            source TEXT,

            last_verified TEXT
        )
        """
    )

    # =================================
    # EMERGENCY NUMBERS
    # =================================

    cursor.execute(

        """
        CREATE TABLE IF NOT EXISTS emergency_numbers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            country TEXT,

            service_type TEXT,

            emergency_number TEXT
        )
        """
    )

    # =================================
    # CLEAN OLD DATA
    # =================================

    cursor.execute(
        "DELETE FROM service_points"
    )

    cursor.execute(
        "DELETE FROM emergency_numbers"
    )

    # =================================
    # INSERT SERVICE POINTS
    # =================================

    for service in services:

        cursor.execute(

            """
            INSERT INTO service_points (

                id,

                name,

                service_type,

                phone,

                phone_source,

                address,

                district,

                state,

                country,

                postcode,

                latitude,

                longitude,

                operator,

                source,

                last_verified

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (

                service.get("id"),

                service.get("name"),

                service.get(
                    "service_type"
                ),

                service.get("phone"),

                service.get(
                    "phone_source"
                ),

                service.get("address"),

                service.get("district"),

                service.get("state"),

                service.get("country"),

                service.get("postcode"),

                service.get("latitude"),

                service.get("longitude"),

                service.get("operator"),

                service.get("source"),

                service.get(
                    "last_verified"
                )
            )
        )

    # =================================
    # INSERT EMERGENCY NUMBERS
    # =================================

    emergency_numbers = (
        get_all_emergency_numbers()
    )

    for item in emergency_numbers:

        cursor.execute(

            """
            INSERT INTO emergency_numbers (

                country,

                service_type,

                emergency_number

            )

            VALUES (?, ?, ?)
            """,

            (

                item["country"],

                item["service_type"],

                item["emergency_number"]
            )
        )

    conn.commit()

    conn.close()

    return {

        "success": True,

        "database":
            "roadsos_offline.db",

        "service_points":
            len(services),

        "emergency_numbers":
            len(emergency_numbers)
    }


# =====================================
# EXPORT EMERGENCY SEED JSON
# =====================================

def export_emergency_seed():

    services = get_all_services()

    emergency_numbers = (
        get_all_emergency_numbers()
    )

    seed_data = {

        "service_points":
            services,

        "emergency_numbers":
            emergency_numbers,

        "chatbot_intents":
            [],

        "nh_corridors":
            []
    }

    with open(

        "emergency_seed.json",

        "w",

        encoding="utf-8"
    ) as file:

        json.dump(

            seed_data,

            file,

            indent=4,

            ensure_ascii=False
        )

    return {

        "success": True,

        "file":
            "emergency_seed.json"
    }