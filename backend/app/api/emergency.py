from fastapi import APIRouter

from app.schemas.emergency_schema import (
    EmergencyRequest,
    EmergencyResponse
)

from app.services.emergency_nlp_service import (
    detect_emergency_type
)

from app.services.sqlite_service import (
    get_all_services
)

from app.services.distance_service import (
    calculate_distance
)

router = APIRouter()


@router.post(
    "/emergency",
    response_model=EmergencyResponse
)

async def emergency_handler(
    request: EmergencyRequest
):

    emergency_type, priority = (
        detect_emergency_type(
            request.message
        )
    )

    services = get_all_services()

    filtered = []

    for service in services:

        if service["type"] != emergency_type:

            continue

        distance = calculate_distance(
            request.latitude,
            request.longitude,
            service["latitude"],
            service["longitude"]
        )

        service["distance_km"] = distance

        filtered.append(service)

    filtered.sort(
        key=lambda x: x["distance_km"]
    )

    recommended = (
        filtered[0]
        if filtered
        else {}
    )

    return {
        "detected_type": emergency_type,
        "priority": priority,
        "recommended_service": recommended
    }