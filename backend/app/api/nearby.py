from typing import Optional

from fastapi import (
    APIRouter,
    Query,
    Depends
)

from app.dependencies.auth_dependency import (
    get_current_user
)

from app.schemas.nearby_schema import (
    NearbyResponseSchema
)

from app.services.sqlite_service import (

    get_all_services,

    save_live_services_to_sqlite,

    cleanup_far_services
)

from app.services.distance_service import (
    calculate_distance
)

from app.services.maps_service import (
    fetch_live_services
)

from app.services.ai_scoring_service import (
    calculate_emergency_score
)


router = APIRouter()


# =====================================
# OFFLINE / LOCAL DATABASE NEARBY
# =====================================

@router.get(

    "/nearby",

    response_model=NearbyResponseSchema
)

async def nearby_services(

    lat: float = Query(...),

    lon: float = Query(...),

    radius: float = Query(10),

    service_type: Optional[str] = Query(None),

    country: str = Query("India"),

    user=Depends(get_current_user),
):

    services = get_all_services()

    nearby_results = []

    for service in services:

        if service.get("country") != country:
            continue

        # =================================
        # FILTER BY SERVICE TYPE
        # =================================

        if (

            service_type

            and

            service.get("service_type")
            != service_type
        ):

            continue

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

        distance = calculate_distance(

            lat,

            lon,

            latitude,

            longitude
        )

        if distance <= radius:

            service["distance_km"] = round(
                distance,
                2
            )

            # =============================
            # AI SCORE
            # =============================

            service["emergency_score"] = (

                calculate_emergency_score(
                    service
                )
            )

            # =============================
            # AI PRIORITY
            # =============================

            if service["emergency_score"] >= 80:

                service["ai_priority"] = (
                    "HIGH"
                )

            elif service["emergency_score"] >= 50:

                service["ai_priority"] = (
                    "MEDIUM"
                )

            else:

                service["ai_priority"] = (
                    "LOW"
                )

            # =============================
            # OFFLINE SOURCE
            # =============================

            service["source"] = (
                "offline_db"
            )

            nearby_results.append(service)

    # =================================
    # SORTING
    # =================================

    nearby_results.sort(

        key=lambda x: (

            -x["emergency_score"],

            x["distance_km"]
        )
    )

    return {

        "success": True,

        "mode":
            "offline_fallback",

        "count":
            len(nearby_results),

        "radius_km":
            radius,

        "service_type":
            service_type,

        "data":
            nearby_results
    }


# =====================================
# LIVE ONLINE SEARCH
# =====================================

@router.get("/live-nearby")

async def live_nearby(

    lat: float,

    lon: float,

    service_type: str,

    radius: int = 5000
):

    services = fetch_live_services(

        lat,

        lon,

        service_type,

        radius
    )

    # =================================
    # CACHE CLEANUP
    # =================================

    cleanup_far_services(

        lat,

        lon,

        keep_radius_km=(
            radius / 1000 + 10
        )
    )

    # =================================
    # SAVE CACHE
    # =================================

    save_live_services_to_sqlite(
        services
    )

    enhanced_results = []

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

        distance = calculate_distance(

            lat,

            lon,

            latitude,

            longitude
        )

        service["distance_km"] = round(
            distance,
            2
        )

        # =============================
        # TEMP RATING
        # =============================

        service["rating"] = 4.0

        service["availability"] = True

        # =============================
        # AI SCORE
        # =============================

        service["emergency_score"] = (

            calculate_emergency_score(
                service
            )
        )

        # =============================
        # AI PRIORITY
        # =============================

        if service["emergency_score"] >= 80:

            service["ai_priority"] = (
                "HIGH"
            )

        elif service["emergency_score"] >= 50:

            service["ai_priority"] = (
                "MEDIUM"
            )

        else:

            service["ai_priority"] = (
                "LOW"
            )

        enhanced_results.append(service)

    # =================================
    # SORTING
    # =================================

    enhanced_results.sort(

        key=lambda x: (

            -x["emergency_score"],

            x["distance_km"]
        )
    )

    # =================================
    # DETECT ONLINE/OFFLINE MODE
    # =================================

    mode = "online"

    if (

        enhanced_results

        and

        enhanced_results[0].get(
            "source"
        ) == "offline_db"
    ):

        mode = "offline_fallback"

    return {

        "success": True,

        "mode":
            mode,

        "count":
            len(enhanced_results),

        "service_type":
            service_type,

        "data":
            enhanced_results
    }