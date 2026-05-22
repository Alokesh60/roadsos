FACILITY_TYPE_MAP = {
    "hospital": "hospital",
    "medical": "hospital",
    "clinic": "hospital",
    "medical_center": "hospital",

    "ambulance": "ambulance",
    "ambulance_service": "ambulance",
    "ems": "ambulance",

    "police": "police",
    "police_station": "police",
    "law_enforcement": "police",

    "fire_station": "fire_station",
    "fire": "fire_station",
}


def normalize_facility_type(
    facility_type: str
):

    return FACILITY_TYPE_MAP.get(
        facility_type.lower(),
        facility_type.lower()
    )