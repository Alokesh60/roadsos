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

from app.services.distance_service import (
    calculate_distance
)

from app.services.logging_service import (
    save_emergency_log
)

from app.utils.response_formatter import (
    format_service
)

from app.utils.emergency_numbers import (
    get_emergency_numbers
)

from ai.chatbot.chain import (
    get_chat_response
)

from ai.utils.classifier import (
    classify_emergency
)

from ai.ranking.scorer import (
    score_facilities,
    to_api_response
)

from app.services.emergency_nlp_service import (
    detect_emergency_type
)

from app.services.sqlite_service import (
    get_all_services
)

from ai.embeddings.chroma_setup import (
    semantic_search 
)

def process_emergency_chatbot(
    message: str,
    latitude: float,
    longitude: float,
    country: str = "India",
):
    
    classification = classify_emergency(
        message
    )

    emergency_numbers = get_emergency_numbers(country)

    if not classification["proceed"]:

      return {

          "classification_status": classification["status"],

          "classification_reason": classification["reason"],

          "proceed": False,

          "message": (
              "Test or non-emergency message detected."
          )
      }

    # fallback NLP

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

    for result in semantic_results:

        if "id" in result:

            semantic_ids.add(
                int(result["id"])
            )

    filtered = []

    for service in services:

        if service.get("country") != country:
            continue

        distance = calculate_distance(

            latitude,

            longitude,

            service["latitude"],

            service["longitude"]
        )

        # Ignore very far cached services
        if distance > 50:
            continue

        # Facility type filtering

        if service["type"] != emergency_type:
            continue

        # Semantic filtering

        if semantic_ids and service["id"] not in semantic_ids:
            continue

        service["facility_type"] = service["type"]

        filtered.append(service)

    scored = score_facilities(
        filtered,
        latitude,
        longitude
    )

    ranked = to_api_response(
        scored
    )

    recommended = format_service(
        ranked[0]
        if ranked
        else {}
    )

    
    severity_map = {

        "high": "serious",

        "medium": "default",

        "low": "minor"
    }

    severity = severity_map.get(
        priority,
        "default"
    )

    guidance = get_chat_response(

        message=message,

        lat=latitude,

        lon=longitude,

        nearby_facilities=ranked,

        severity=severity
    )

    save_emergency_log(
        message=message,
        detected_type=emergency_type,
        priority=priority,
        confidence=confidence,
        country=country,
        classification_status=classification["status"],
        recommended_service=recommended
    )

    return {
        "classification_status": classification["status"],

        "classification_reason": classification["reason"],

        "proceed": classification["proceed"],

        "detected_type": emergency_type,

        "priority": priority,

        "confidence": confidence,

        "recommended_service": recommended,

        "guidance": guidance,

        "semantic_matches_found": len(filtered),

        "emergency_numbers": emergency_numbers
    }
