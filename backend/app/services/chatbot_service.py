from app.services.emergency_nlp_service import (
    detect_emergency_type
)

from app.services.sqlite_service import (
    get_all_services
)

from app.services.distance_service import (
    calculate_distance
)

from app.services.chroma_service import (
    semantic_search
)


def process_emergency_chatbot(
    message: str,
    latitude: float,
    longitude: float
):

    # NLP classification

    emergency_type, priority, confidence = (
        detect_emergency_type(message)
    )

    # Fetch all services

    services = get_all_services()

    # Semantic retrieval from ChromaDB

    semantic_results = semantic_search(
        message
    )

    semantic_ids = set()

    try:

        for result_id in semantic_results["ids"][0]:

            semantic_ids.add(
                int(result_id)
            )

    except:
        pass

    filtered = []

    for service in services:

        # Facility type filtering

        if service["type"] != emergency_type:
            continue

        # Semantic filtering

        if semantic_ids and service["id"] not in semantic_ids:
            continue

        # Distance calculation

        distance = calculate_distance(

            latitude,
            longitude,

            service["latitude"],
            service["longitude"]
        )

        service["distance_km"] = round(
            distance,
            2
        )

        filtered.append(service)

    # Sort nearest first

    filtered.sort(
        key=lambda x: x["distance_km"]
    )

    # Best recommendation

    recommended = (
        filtered[0]
        if filtered
        else {}
    )

    # AI emergency guidance

    guidance = generate_guidance(
        emergency_type
    )

    return {

        "detected_type": emergency_type,

        "priority": priority,

        "confidence": confidence,

        "recommended_service": recommended,

        "guidance": guidance,

        "semantic_matches_found": len(filtered)
    }


def generate_guidance(
    emergency_type: str
):

    if emergency_type == "hospital":

        return (
            "Keep the injured person stable and avoid unnecessary movement."
        )

    elif emergency_type == "fire_station":

        return (
            "Move away from smoke and fire immediately."
        )

    elif emergency_type == "police":

        return (
            "Move to a safe location and contact authorities."
        )

    else:

        return (
            "Stay calm and wait for emergency assistance."
        )