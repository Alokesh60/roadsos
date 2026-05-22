from app.db.sqlite_db import get_connection


def get_all_services():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM facilities")
    rows = cursor.fetchall()

    conn.close()

    normalized = []

    for row in rows:
        r = dict(row)

        normalized.append({
            "id": r.get("id"),
            "name": r.get("name") or "Unknown Facility",
            "type": r.get("facility_type") or "hospital",
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
            "phone": r.get("phone") or "108",

            # AI DB has only address, not city/state
            "address": r.get("address") or "Unknown",
            "country": r.get("country") or "India",

            "rating": r.get("rating") if r.get("rating") is not None else 3.5,
            "response_time_min": r.get("response_time_min") or 15,
            "is_available": r.get("is_available") if r.get("is_available") is not None else 1,
            "services_offered": r.get("services_offered") or "Emergency Services",
            "last_verified": r.get("last_verified") or "Unknown"
        })

    return normalized


def search_services(query: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM facilities
        WHERE name LIKE ?
        """,
        (f"%{query}%",)
    )

    rows = cursor.fetchall()
    conn.close()

    normalized = []

    for row in rows:
        r = dict(row)

        normalized.append({
            "id": r.get("id"),
            "name": r.get("name") or "Unknown Facility",
            "type": r.get("facility_type") or "hospital",
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
            "phone": r.get("phone") or "108",
            "address": r.get("address") or "Unknown",
            "country": r.get("country") or "India",
            "rating": r.get("rating") if r.get("rating") is not None else 3.5,
            "response_time_min": r.get("response_time_min") or 15,
            "is_available": r.get("is_available") if r.get("is_available") is not None else 1,
            "services_offered": r.get("services_offered") or "Emergency Services",
            "last_verified": r.get("last_verified") or "Unknown"
        })

    return normalized