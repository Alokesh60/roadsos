from app.db.sqlite_db import get_connection

conn = get_connection()

cursor = conn.cursor()

services = [

    (
        "GNRC Hospital",
        "hospital",
        26.1445,
        91.7362,
        "108",
        "Guwahati"
    ),

    (
        "Apollo Ambulance",
        "ambulance",
        26.1470,
        91.7300,
        "102",
        "GS Road"
    ),

    (
        "Dispur Police Station",
        "police",
        26.1400,
        91.7900,
        "100",
        "Dispur"
    )
]

cursor.executemany(
    """
    INSERT INTO emergency_services
    (
        name,
        type,
        latitude,
        longitude,
        phone,
        address
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    services
)

conn.commit()

conn.close()

print("Emergency services seeded.")