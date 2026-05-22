from typing import Optional

from fastapi import APIRouter, Query, Depends

from app.services.sqlite_service import get_all_services
from app.services.distance_service import calculate_distance
from app.services.maps_service import fetch_live_services
from app.schemas.nearby_schema import NearbyResponseSchema
from app.dependencies import verify_token
from app.services.ai_scoring_service import calculate_emergency_score

router = APIRouter()

@router.get("/nearby",
            response_model=NearbyResponseSchema)
async def nearby_services(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(10),
    type: Optional[str] = Query(None),
    # user=Depends(verify_token),
):

    services = get_all_services()

    nearby_results = []

    for service in services:

        # Filter by type if provided
        if type and service["type"] != type:
            continue

        distance = calculate_distance(
            lat,
            lon,
            service["latitude"],
            service["longitude"]
        )

        if distance <= radius:

            service["distance_km"] = round(distance, 2)

            # Calculate emergency score
            service["emergency_score"] = calculate_emergency_score(service)
            
            if service["emergency_score"] >= 80:

                service["ai_priority"] = "HIGH"

            elif service["emergency_score"] >= 50:

                service["ai_priority"] = "MEDIUM"

            else:

                service["ai_priority"] = "LOW"

            nearby_results.append(service)

    nearby_results.sort(key=lambda x: x["emergency_score"], reverse=True)

    return {
        "success": True,
        "count": len(nearby_results),
        "radius_km": radius,
        "filter_type": type,
        "data": nearby_results
    }

@router.get("/live-nearby")
async def live_nearby(
    lat: float,
    lon: float,
    type: str,
    radius: int = 5000
):

    services = fetch_live_services(
        lat,
        lon,
        type,
        radius
    )

    return {
        "success": True,
        "count": len(services),
        "type": type,
        "data": services
    }