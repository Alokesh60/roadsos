def detect_emergency_type(message: str):

    text = message.lower()

    # MEDICAL

    medical_keywords = [

        "accident",
        "injury",
        "bleeding",
        "ambulance",
        "crash",
        "hospital",
        "unconscious"
    ]

    # FIRE

    fire_keywords = [

        "fire",
        "burn",
        "smoke",
        "explosion"
    ]

    # POLICE

    police_keywords = [

        "theft",
        "crime",
        "fight",
        "attack",
        "police"
    ]

    # TOWING

    towing_keywords = [

        "breakdown",
        "towing",
        "flat tire",
        "vehicle stuck"
    ]

    for word in medical_keywords:

        if word in text:

            return "ambulance", "HIGH"

    for word in fire_keywords:

        if word in text:

            return "fire", "HIGH"

    for word in police_keywords:

        if word in text:

            return "police", "MEDIUM"

    for word in towing_keywords:

        if word in text:

            return "towing", "LOW"

    return "general", "LOW"