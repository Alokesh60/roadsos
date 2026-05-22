import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../"
        )
    )
)

from typing import Optional
from fastapi import APIRouter, Query, Depends

from app.services.sqlite_service import get_all_services
from app.services.distance_service import calculate_distance
from app.services.maps_service import fetch_live_services
from app.schemas.nearby_schema import NearbyResponseSchema
from app.dependencies import verify_token
from app.services.ai_scoring_service import calculate_emergency_score
from ai.embeddings.chroma_setup import (
    semantic_search
)

from app.services.ai_scoring_service import calculate_emergency_score
from app.services.distance_service import calculate_distance
from app.services.sqlite_service import (
    save_live_services_to_sqlite,
)
from app.services.sqlite_service import (
    cleanup_far_services
)

router = APIRouter()

@router.get("/nearby",
            response_model=NearbyResponseSchema)
async def nearby_services(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(10),
    type: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    country: str = Query("India"),
    # user=Depends(verify_token),
):

    services = get_all_services()

    semantic_ids = set()

    if query:

        semantic_results = semantic_search(query)

        for result in semantic_results:

            if "id" in result:

                semantic_ids.add(
                    int(result["id"])
                )

    nearby_results = []

    for service in services:
        
        if service.get("country") != country:
            continue

        # Filter by type if provided
        if type and service["type"] != type:
            continue

        # Filter by semantic search results if query is provided
        if semantic_ids and service["id"] not in semantic_ids:
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

    nearby_results.sort(
        key=lambda x: (
            -x["emergency_score"],
            x["distance_km"], 
        )
    )

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

    cleanup_far_services(
        lat,

        lon,

        keep_radius_km=radius / 1000 + 10
    )

    save_live_services_to_sqlite(services)

    enhanced_results = []

    for service in services:

        # calculate distance
        distance = calculate_distance(

            lat,

            lon,

            service["latitude"],

            service["longitude"]
        )

        service["distance_km"] = round(distance, 2)

        # temporary AI fields for live data
        service["rating"] = 4.0
        service["availability"] = True

        # AI emergency score
        service["emergency_score"] = (
            calculate_emergency_score(service)
        )

        # AI priority
        if service["emergency_score"] >= 80:

            service["ai_priority"] = "HIGH"

        elif service["emergency_score"] >= 50:

            service["ai_priority"] = "MEDIUM"

        else:

            service["ai_priority"] = "LOW"

        enhanced_results.append(service)

    # intelligent sorting
    enhanced_results.sort(

        key=lambda x: (
            -x["emergency_score"],
            x["distance_km"]
        )
    )

    return {

        "success": True,

        "count": len(enhanced_results),

        "type": type,

        "data": enhanced_results
    }