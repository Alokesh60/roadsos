# =====================================
# STANDARDIZED FACILITY TYPE MAPPING
# =====================================

FACILITY_TYPE_MAP = {

    # =================================
    # HOSPITAL / MEDICAL
    # =================================

    "hospital":
        "hospital",

    "medical":
        "hospital",

    "clinic":
        "hospital",

    "medical_center":
        "hospital",

    "healthcare":
        "hospital",

    "ambulance":
        "hospital",

    "ambulance_service":
        "hospital",

    "ems":
        "hospital",

    # =================================
    # POLICE
    # =================================

    "police":
        "police_station",

    "police_station":
        "police_station",

    "law_enforcement":
        "police_station",

    "crime":
        "police_station",

    # =================================
    # FIRE
    # =================================

    "fire":
        "fire_station",

    "fire_station":
        "fire_station",

    # =================================
    # VEHICLE SUPPORT
    # =================================

    "mechanic":
        "car_repair",

    "car_repair":
        "car_repair",

    "garage":
        "car_repair",

    "vehicle_repair":
        "car_repair",

    "tow_service":
        "car_repair",

    "towing":
        "car_repair",

    "puncture":
        "car_repair",

    "tyre_shop":
        "tyre_shop"
}


# =====================================
# NORMALIZATION FUNCTION
# =====================================

def normalize_facility_type(
    facility_type: str
):

    normalized = FACILITY_TYPE_MAP.get(

        facility_type.lower(),

        facility_type.lower()
    )

    return normalized