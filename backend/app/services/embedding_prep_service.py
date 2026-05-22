def build_service_text(service):

    parts = [

        service.get("name", ""),

        service.get("type", ""),

        service.get("address", ""),

        service.get("city", ""),

        service.get("state", ""),

        service.get("country", "")
    ]

    # SERVICES OFFERED

    services_offered = (
        service.get("services_offered", "")
    )

    if services_offered:

        parts.append(services_offered)

    return " ".join(
        str(part)
        for part in parts
        if part
    )