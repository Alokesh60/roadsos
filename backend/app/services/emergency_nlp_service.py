from app.utils.facility_mapper import (
    normalize_facility_type
)


def detect_emergency_type(text: str):

    text = text.lower()

    trauma_keywords = [
        "accident",
        "bleeding",
        "injury",
        "crash",
        "fracture",
        "bike accident"
    ]

    fire_keywords = [
        "fire",
        "burn",
        "smoke",
        "explosion"
    ]

    crime_keywords = [
        "attack",
        "robbery",
        "violence",
        "theft",
        "kidnap"
    ]

    if any(word in text for word in trauma_keywords):

        emergency_type = "hospital"
        priority = "high"
        confidence = 0.95

    elif any(word in text for word in fire_keywords):

        emergency_type = "fire_station"
        priority = "high"
        confidence = 0.93

    elif any(word in text for word in crime_keywords):

        emergency_type = "police"
        priority = "medium"
        confidence = 0.88

    else:

        emergency_type = "ambulance"
        priority = "low"
        confidence = 0.60

    emergency_type = normalize_facility_type(
        emergency_type
    )

    return (
        emergency_type,
        priority,
        confidence
    )