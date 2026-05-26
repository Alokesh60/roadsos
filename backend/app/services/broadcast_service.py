from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2
)

from datetime import datetime

from app.db.sqlite_db import (
    get_connection
)

from app.services.fcm_service import (
    send_push_notification
)


# =====================================
# DISTANCE CALCULATION
# =====================================

def calculate_distance(

    lat1,

    lon1,

    lat2,

    lon2
):

    R = 6371

    dlat = radians(
        lat2 - lat1
    )

    dlon = radians(
        lon2 - lon1
    )

    a = (

        sin(dlat / 2) ** 2

        +

        cos(radians(lat1))

        *

        cos(radians(lat2))

        *

        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(

        sqrt(a),

        sqrt(1 - a)
    )

    return R * c


# =====================================
# CACHE RESPONDER LOCATION
# =====================================

def cache_responder_location(

    user_id: str,

    latitude: float,

    longitude: float
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO responder_cache (

            user_id,

            latitude,

            longitude

        )

        VALUES (?, ?, ?)
        """,

        (

            user_id,

            latitude,

            longitude
        )
    )

    conn.commit()

    conn.close()


# =====================================
# FIND NEARBY USERS
# =====================================

def find_nearby_users(

    latitude,

    longitude,

    current_uid,

    radius_km=5
):

    conn = get_connection()

    conn.row_factory = dict_factory

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM responder_cache"
    )

    users = cursor.fetchall()

    conn.close()

    nearby_users = []

    for user in users:

        if user.get("user_id") == current_uid:
            continue

        user_lat = user.get(
            "latitude"
        )

        user_lon = user.get(
            "longitude"
        )

        if (

            user_lat is None

            or

            user_lon is None
        ):

            continue

        distance = calculate_distance(

            latitude,

            longitude,

            user_lat,

            user_lon
        )

        if distance <= radius_km:

            user["distance_km"] = round(
                distance,
                2
            )

            nearby_users.append(user)

    nearby_users.sort(

        key=lambda x: (
            x["distance_km"]
        )
    )

    return nearby_users


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
# COMMUNITY SOS MESSAGE
# =====================================

def build_sos_message(

    user_name,

    emergency_type,

    latitude,

    longitude,

    priority
):

    maps_link = (

        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    timestamp = datetime.now().strftime(

        "%d-%m-%Y %I:%M %p"
    )

    return f"""

🚨 RoadSOS COMMUNITY ALERT 🚨

User:
{user_name}

Emergency Type:
{emergency_type.upper()}

Priority:
{priority.upper()}

A nearby RoadSOS user may require
immediate assistance.

📍 Live Location:
{maps_link}

Latitude:
{latitude}

Longitude:
{longitude}

🕒 Time:
{timestamp}

Open RoadSOS immediately
to respond.

"""


# =====================================
# BROADCAST ALERT
# =====================================

def broadcast_sos_alert(

    nearby_users,

    message
):

    broadcast_results = []

    for user in nearby_users:

        user_id = user.get(
            "user_id"
        )

        fcm_token = user.get(
            "fcm_token"
        )

        print(

            "\n========== "
            "SOS BROADCAST =========="
        )

        print(
            f"User ID: {user_id}"
        )

        print(
            f"FCM Token: {fcm_token}"
        )

        print(message)

        print(
            "===========================\n"
        )

        status = "NOT_SENT"

        # =============================
        # SEND PUSH NOTIFICATION
        # =============================

        if fcm_token:

            try:

                send_push_notification(

                    token=fcm_token,

                    title=(
                        "🚨 Nearby Emergency"
                    ),

                    body=(
                        "A nearby RoadSOS "
                        "user needs help."
                    )
                )

                status = "PUSH_SENT"

            except Exception as e:

                print(
                    f"Push failed: {e}"
                )

                status = "PUSH_FAILED"

        broadcast_results.append({

            "user_id":
                user_id,

            "distance_km":
                user.get(
                    "distance_km"
                ),

            "status":
                status
        })

    return broadcast_results