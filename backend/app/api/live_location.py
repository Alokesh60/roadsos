from fastapi import (

    APIRouter,

    Depends
)

from app.dependencies.auth_dependency import (
    get_current_user
)

from app.services.broadcast_service import (
    cache_responder_location
)

router = APIRouter()


# =====================================
# UPDATE LIVE LOCATION
# =====================================

@router.post("/update-location")

async def update_location(

    latitude: float,

    longitude: float,

    fcm_token: str,

    is_online: bool = True,

    user=Depends(
        get_current_user
    )
):

    user_id = user["uid"]

    # =============================
    # CACHE LOCATION
    # =============================

    cache_responder_location(

        user_id=user_id,

        latitude=latitude,

        longitude=longitude
    )

    print(

        "\n========== "
        "LOCATION UPDATED =========="
    )

    print(
        f"User ID: {user_id}"
    )

    print(
        f"Latitude: {latitude}"
    )

    print(
        f"Longitude: {longitude}"
    )

    print(
        f"Online: {is_online}"
    )

    print(
        "==============================\n"
    )

    return {

        "success": True,

        "message":
            "Responder location cached",

        "data": {

            "user_id":
                user_id,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "fcm_token":
                fcm_token,

            "is_online":
                is_online
        }
    }