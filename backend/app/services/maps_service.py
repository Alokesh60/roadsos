import requests

from app.services.sqlite_service import (
    get_nearest_services
)


# =====================================
# OVERPASS API
# =====================================

OVERPASS_URL = (
    "https://overpass-api.de/api/interpreter"
)


# =====================================
# SERVICE TYPE MAPPING
# =====================================

TYPE_MAPPING = {

    "hospital":
        '"amenity"="hospital"',

    "police_station":
        '"amenity"="police"',

    "fire_station":
        '"amenity"="fire_station"',

    "fuel":
        '"amenity"="fuel"',

    "car_repair":
        '"shop"="car_repair"',

    "towing":
        '"shop"="car_repair"'
}


# =====================================
# FETCH LIVE SERVICES
# PRIMARY ONLINE LAYER
# =====================================

def fetch_live_services(

    lat,

    lon,

    service_type,

    radius=None
):

    # =================================
    # DYNAMIC RADIUS
    # =================================

    if radius is None:

        if service_type == "hospital":

            radius = 5000

        elif service_type == "police_station":

            radius = 10000

        elif service_type == "fire_station":

            radius = 15000

        else:

            radius = 8000

    print(

        f"\n[ONLINE] Searching "
        f"{service_type} "
        f"within {radius}m\n"
    )

    osm_filter = TYPE_MAPPING.get(
        service_type
    )

    if not osm_filter:

        print(
            f"Unsupported service type: "
            f"{service_type}"
        )

        return []

    query = f"""

    [out:json];

    (
      node[{osm_filter}]
      (around:{radius},{lat},{lon});

      way[{osm_filter}]
      (around:{radius},{lat},{lon});

      relation[{osm_filter}]
      (around:{radius},{lat},{lon});
    );

    out center;

    """

    try:

        response = requests.get(

            OVERPASS_URL,

            params={
                "data": query
            },

            headers={

                "User-Agent":
                    "RoadSOS Emergency App"
            },

            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        services = []

        existing_names = set()

        for element in data.get(
            "elements",
            []
        ):

            tags = element.get(
                "tags",
                {}
            )

            lat_value = element.get(
                "lat"
            )

            lon_value = element.get(
                "lon"
            )

            # =================================
            # WAY / RELATION CENTER
            # =================================

            if (

                lat_value is None

                and

                "center" in element
            ):

                lat_value = (
                    element["center"]["lat"]
                )

            if (

                lon_value is None

                and

                "center" in element
            ):

                lon_value = (
                    element["center"]["lon"]
                )

            if (

                lat_value is None

                or

                lon_value is None
            ):

                continue

            service_name = tags.get(
                "name",
                "Unknown Service"
            )

            if service_name.lower() in existing_names:
                continue

            existing_names.add(
                service_name.lower()
            )

            services.append({

                "name":
                    service_name,

                "service_type":
                    service_type,

                "latitude":
                    lat_value,

                "longitude":
                    lon_value,

                "phone":
                    (
                        tags.get("phone")
                        or
                        tags.get("contact:phone")
                        or
                        "N/A"
                    ),

                "address":
                    tags.get(
                        "addr:full",
                        "Unknown"
                    ),

                "city":
                    tags.get(
                        "addr:city",
                        "Unknown"
                    ),

                "state":
                    tags.get(
                        "addr:state",
                        "Unknown"
                    ),

                "country":
                    tags.get(
                        "addr:country",
                        "Unknown"
                    ),

                "source":
                    "openstreetmap"
            })

        print(

            f"[ONLINE] Found "
            f"{len(services)} "
            f"{service_type} services\n"
        )

        return services

    # =================================
    # OFFLINE FALLBACK
    # =================================

    except Exception as e:

        print(

            f"\n[OFFLINE FALLBACK] "
            f"Live fetch failed: {e}"
        )

        offline_services = (

            get_nearest_services(

                latitude=lat,

                longitude=lon,

                service_type=service_type,

                radius_km=radius / 1000
            )
        )

        for service in offline_services:

            service["source"] = (
                "offline_db"
            )

        print(

            f"[OFFLINE] Loaded "
            f"{len(offline_services)} "
            f"cached services\n"
        )

        return offline_services