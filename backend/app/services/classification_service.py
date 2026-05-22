def classify_emergency(text: str):

    text = text.lower()

    if any(word in text for word in [
        "accident",
        "bleeding",
        "injury",
        "crash",
        "trauma"
    ]):

        return {
            "emergency_type": "trauma",
            "priority": "high",
            "recommended_service": "hospital"
        }

    elif any(word in text for word in [
        "fire",
        "burn",
        "smoke"
    ]):

        return {
            "emergency_type": "fire",
            "priority": "high",
            "recommended_service": "fire_station"
        }

    elif any(word in text for word in [
        "theft",
        "attack",
        "violence",
        "robbery"
    ]):

        return {
            "emergency_type": "crime",
            "priority": "medium",
            "recommended_service": "police"
        }

    else:

        return {
            "emergency_type": "general",
            "priority": "low",
            "recommended_service": "ambulance"
        }