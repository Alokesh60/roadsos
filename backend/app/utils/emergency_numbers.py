# =====================================
# GLOBAL EMERGENCY NUMBERS
# =====================================

EMERGENCY_NUMBERS = {

    "India": {

        "hospital": "108",

        "police": "100",

        "fire_station": "101",

        "towing": "1033",

        "fuel": "1906",

        "emergency": "112"
    },

    "USA": {

        "hospital": "911",

        "police": "911",

        "fire_station": "911",

        "towing": "911",

        "fuel": "911",

        "emergency": "911"
    },

    "UK": {

        "hospital": "999",

        "police": "999",

        "fire_station": "999",

        "towing": "999",

        "fuel": "999",

        "emergency": "999"
    }
}


# =====================================
# GET COUNTRY NUMBERS
# =====================================

def get_emergency_numbers(
    country: str
):

    return EMERGENCY_NUMBERS.get(

        country,

        EMERGENCY_NUMBERS["India"]
    )


# =====================================
# GET SPECIFIC SERVICE NUMBER
# =====================================

def get_service_emergency_number(

    country: str,

    service_type: str
):

    country_data = (

        EMERGENCY_NUMBERS.get(

            country,

            EMERGENCY_NUMBERS["India"]
        )
    )

    return country_data.get(

        service_type,

        country_data["emergency"]
    )


# =====================================
# EXPORT ALL NUMBERS
# =====================================

def get_all_emergency_numbers():

    result = []

    for country, services in (
        EMERGENCY_NUMBERS.items()
    ):

        for service_type, number in (
            services.items()
        ):

            result.append({

                "country":
                    country,

                "service_type":
                    service_type,

                "emergency_number":
                    number
            })

    return result