import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


TYPE_MAPPING = {
    "hospital": '"amenity"="hospital"',
    "police_station": '"amenity"="police"',
    "fire_station": '"amenity"="fire_station"',
    "blood_bank": '"healthcare"="blood_bank"',
}


def fetch_live_services(lat, lon, service_type, radius=5000):

    osm_filter = TYPE_MAPPING.get(service_type)

    if not osm_filter:
        return []

    query = f"""
    [out:json];

    (
      node[{osm_filter}](around:{radius},{lat},{lon});
      way[{osm_filter}](around:{radius},{lat},{lon});
      relation[{osm_filter}](around:{radius},{lat},{lon});
    );

    out center;
    """

    try:

        response = requests.get(
            OVERPASS_URL,
            params={"data": query},
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        services = []

        for element in data.get("elements", []):

            tags = element.get("tags", {})

            lat_value = element.get("lat")

            lon_value = element.get("lon")

            # ways/relations use center coordinates
            if not lat_value and "center" in element:
                lat_value = element["center"]["lat"]

            if not lon_value and "center" in element:
                lon_value = element["center"]["lon"]

            services.append({
                "name": tags.get("name", "Unknown Service"),
                "latitude": lat_value,
                "longitude": lon_value,
                "type": service_type,
                "source": "openstreetmap"
            })

        return services

    except Exception as e:

        print("OSM ERROR:", str(e))

        return []