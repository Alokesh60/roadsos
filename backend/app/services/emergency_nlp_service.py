# emergency_nlp_service.py
def detect_emergency_type(message: str):

    message = message.lower()

    if any(word in message for word in [
        "fire",
        "burn",
        "smoke"
    ]):
        return "fire_station", "high", 0.95

    elif any(word in message for word in [
        "accident",
        "injured",
        "ambulance",
        "hospital"
    ]):
        return "hospital", "high", 0.93

    elif any(word in message for word in [
        "robbery",
        "theft",
        "attack",
        "assault",
        "police"
    ]):
        return "police_station", "high", 0.92

    elif any(word in message for word in [
        "flood",
        "landslide"
    ]):
        return "disaster_response", "high", 0.90

    return "hospital", "medium", 0.70