from firebase_admin import firestore
from math import radians, sin, cos, sqrt, atan2


def _db():
    return firestore.client()


# =====================================
# DISTANCE CALCULATION (KM)
# =====================================

def calculate_distance(

    lat1: float,

    lon1: float,

    lat2: float,

    lon2: float
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

    c = (

        2

        *

        atan2(
            sqrt(a),
            sqrt(1 - a)
        )
    )

    return R * c


# =====================================
# FIND NEARBY USERS
# =====================================

async def find_nearby_users(

    latitude: float,

    longitude: float,

    radius_km: float = 5.0
):

    nearby_users = []

    try:

        users = (

            _db().collection(
                "users"
            ).stream()
        )

        for user in users:

            data = user.to_dict()

            location = data.get(
                "location",
                {}
            )

            user_lat = location.get(
                "latitude"
            )

            user_lng = location.get(
                "longitude"
            )

            if (

                user_lat is None

                or

                user_lng is None
            ):

                continue

            distance = (

                calculate_distance(

                    latitude,

                    longitude,

                    user_lat,

                    user_lng
                )
            )

            if distance <= radius_km:

                nearby_users.append({

                    "uid":
                        data.get(
                            "uid"
                        ),

                    "name":
                        data.get(
                            "name"
                        ),

                    "fcm_token":
                        data.get(
                            "fcm_token"
                        ),

                    "distance_km":
                        round(
                            distance,
                            2
                        )
                })

    except Exception as e:

        print(
            f"[RESPONDER_SERVICE] {e}"
        )

    return nearby_users
