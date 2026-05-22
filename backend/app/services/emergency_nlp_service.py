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

        return (
            "hospital",
            "high"
        )

    elif any(word in text for word in fire_keywords):

        return (
            "fire_station",
            "high"
        )

    elif any(word in text for word in crime_keywords):

        return (
            "police",
            "medium"
        )

    else:

        return (
            "ambulance",
            "low"
        )