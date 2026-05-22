EMERGENCY_NUMBERS = {

    "India": {

        "emergency": "112",

        "ambulance": "108",

        "police": "100",

        "fire": "101"
    },

    "USA": {

        "emergency": "911",

        "ambulance": "911",

        "police": "911",

        "fire": "911"
    },

    "UK": {

        "emergency": "999",

        "ambulance": "999",

        "police": "999",

        "fire": "999"
    }
}


def get_emergency_numbers(
    country: str
):

    return EMERGENCY_NUMBERS.get(

        country,

        EMERGENCY_NUMBERS["India"]
    )