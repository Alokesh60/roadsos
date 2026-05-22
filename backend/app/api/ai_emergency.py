from fastapi import APIRouter

from app.services.chroma_service import (
     semantic_search
)

from ai.chatbot.chain import (
    get_chat_response
)

from app.services.contact_service import (
    get_contacts
)

from app.services.chroma_service import (
    semantic_emergency_classification
)

from app.services.distance_service import (
    calculate_distance  
)

from app.services.ai_scoring_service import (
    calculate_emergency_score
)

from app.services.maps_service import (
  fetch_live_services
)

router = APIRouter()


@router.get("/ai-emergency")

async def ai_emergency(
    query: str,

    lat: float,

    lon: float,

    country: str = "India"
):

    result = (
        semantic_emergency_classification(
            query
        )
    )

    semantic_matches = semantic_search(query)

    service_type = result[
            "detected_service_type"
    ]

    live_services = fetch_live_services(

            lat,

            lon,

            service_type
        )

    enhanced_services = []

    for service in live_services:

            distance = calculate_distance(

                lat,

                lon,

                service["latitude"],

                service["longitude"]
            )

            service["distance_km"] = round(
                distance,
                2
            )

            # temporary AI fields
            service["rating"] = 4.0

            service["availability"] = True

            service["emergency_score"] = (
                calculate_emergency_score(
                    service
                )
            )

            if service["emergency_score"] >= 80:

                service["ai_priority"] = "HIGH"

            elif service["emergency_score"] >= 50:

                service["ai_priority"] = "MEDIUM"

            else:

                service["ai_priority"] = "LOW"

            enhanced_services.append(service)

    enhanced_services.sort(

            key=lambda x: (
                -x["emergency_score"],
                x["distance_km"]
            )
        )
    
    emergency_contacts = get_contacts(
         "test-user"
    )

    severity = result["priority"]

    guidance = get_chat_response(

        message=query,

        lat=lat,

        lon=lon,

        nearby_facilities=enhanced_services[:5],

        severity=severity
    )

    return {

        "success": True,

        "query": query,

        "ai_result": {
            **result, 
            "semantic_matches": semantic_matches
        },

        "live_services": enhanced_services[:5],

        "emergency_contacts": emergency_contacts,

        "guidance": guidance,

        
    }