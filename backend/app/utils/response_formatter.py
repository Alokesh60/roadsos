# =====================================
# FORMAT SERVICE RESPONSE
# =====================================

def format_service(service: dict):

    if not service:

        return {}

    return {

        "id":
            service.get("id"),

        "name":
            service.get("name"),

        "service_type":
            service.get(
                "service_type"
            ),

        "phone":
            service.get("phone"),

        "phone_source":
            service.get(
                "phone_source"
            ),

        "address":
            service.get("address"),

        "district":
            service.get("district"),

        "city":
            service.get("city"),

        "state":
            service.get("state"),

        "country":
            service.get("country"),

        "postcode":
            service.get("postcode"),

        "latitude":
            service.get("latitude"),

        "longitude":
            service.get("longitude"),

        "distance_km":
            service.get(
                "distance_km"
            ),

        "rating":
            service.get("rating"),

        "availability":
            service.get(
                "availability"
            ),

        "verified":
            service.get(
                "verified"
            ),

        "operator":
            service.get("operator"),

        "source":
            service.get("source"),

        "emergency_score":
            service.get(
                "emergency_score"
            ),

        "ai_priority":
            service.get(
                "ai_priority"
            )
    }