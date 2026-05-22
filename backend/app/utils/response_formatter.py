def format_service(service: dict):

    if not service:
        return {}

    return {

        "id": service.get("id"),

        "name": service.get("name"),

        "type": service.get("type"),

        "phone": service.get("phone"),

        "address": service.get("address"),

        "city": service.get("city"),

        "state": service.get("state"),

        "country": service.get("country"),

        "latitude": service.get("latitude"),

        "longitude": service.get("longitude"),

        "distance_km": service.get("distance_km"),

        "rating": service.get("rating"),

        "availability": service.get("is_available"),

        "score": service.get("score")
    }