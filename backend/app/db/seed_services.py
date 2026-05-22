from app.db.sqlite_db import get_connection

conn = get_connection()
cursor = conn.cursor()

services = [
    (
        "GNRC Hospital", "hospital",
        26.1445, 91.7362, "108",
        "Guwahati", "Guwahati", "Assam", "India",
        4.7, 8, 1, "trauma,icu,burn care", "2026-05-20"
    ),
    (
        "Apollo Ambulance", "ambulance",
        26.1470, 91.7300, "102",
        "GS Road", "Guwahati", "Assam", "India",
        4.5, 5, 1, "ambulance,oxygen,emergency transport", "2026-05-20"
    ),
    (
        "Dispur Police Station", "police",
        26.1400, 91.7900, "100",
        "Dispur", "Guwahati", "Assam", "India",
        4.2, 12, 1, "law enforcement,traffic control", "2026-05-20"
    ),
]

cursor.executemany("""
INSERT INTO emergency_services (
    name, type, latitude, longitude, phone,
    address, city, state, country,
    rating, response_time_min, is_available,
    services_offered, last_verified
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", services)

conn.commit()
conn.close()

print("Emergency services seeded.")