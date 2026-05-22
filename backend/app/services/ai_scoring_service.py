def calculate_emergency_score(service):

    score = 0

    # VERIFIED BONUS

    if service.get("verified"):

        score += 30

    # AVAILABILITY BONUS

    if service.get("availability"):

        score += 25

    # RATING BONUS

    rating = service.get("rating", 0)

    score += rating * 10

    # DISTANCE BONUS

    distance = service.get("distance_km", 100)

    if distance <= 1:
        score += 30

    elif distance <= 3:
        score += 20

    elif distance <= 5:
        score += 10

    return round(score, 2)