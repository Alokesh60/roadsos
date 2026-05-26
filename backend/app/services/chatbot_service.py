import sys
import os
import requests

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../"
        )
    )
)

from app.services.distance_service import (
    calculate_distance
)

from app.services.logging_service import (
    save_emergency_log
)

from app.services.sqlite_service import (
    get_all_services
)

from app.utils.response_formatter import (
    format_service
)

from app.utils.emergency_numbers import (
    get_emergency_numbers
)

from app.services.emergency_nlp_service import (
    detect_emergency_type
)


# =====================================
# DISASTER ALERT DETECTION
# =====================================

def detect_disaster_alerts(
    message: str
):

    message = message.lower()

    alerts = []

    if "flood" in message:

        alerts.append(

            "⚠ Flood risk detected."
        )

    if "landslide" in message:

        alerts.append(

            "⚠ Landslide-prone area."
        )

    if "rain" in message:

        alerts.append(

            "⚠ Heavy rainfall warning."
        )

    if "storm" in message:

        alerts.append(

            "⚠ Thunderstorm alert."
        )

    return alerts


# =====================================
# AI GUIDANCE
# =====================================

def get_ai_guidance(

    message: str,

    latitude: float,

    longitude: float,

    nearest_service=None
):

    try:

        ai_response = requests.post(

            "http://127.0.0.1:8000/chat",

            json={

                "user_message": message,

                "context": {

                    "lat": latitude,

                    "lng": longitude,

                    "nearest_service": (
                        nearest_service
                    ),

                    "is_sos_active": True
                },

                "history": []
            },

            timeout=5
        )

        ai_response.raise_for_status()

        ai_data = ai_response.json()

        return {

            "guidance":
                ai_data.get(
                    "reply",
                    "Emergency guidance unavailable."
                ),

            "source":
                ai_data.get(
                    "source",
                    "ai_module"
                ),

            "suggested_actions":
                ai_data.get(
                    "suggested_actions",
                    []
                )
        }

    except Exception as e:

        print(
            f"AI module failed: {e}"
        )

        return {

            "guidance":
                (
                    "Emergency detected. "
                    "Please contact nearby "
                    "services immediately."
                ),

            "source":
                "offline_fallback",

            "suggested_actions": [

                "Call emergency services",

                "Share your live location",

                "Move to a safe area"
            ]
        }


# =====================================
# MAIN EMERGENCY PROCESSOR
# =====================================

def process_emergency_chatbot(

    message: str,

    latitude: float,

    longitude: float,

    country: str = "India"
):

    # =================================
    # OFFLINE EMERGENCY NUMBERS
    # =================================

    emergency_numbers = (

        get_emergency_numbers(
            country
        )
    )

    # =================================
    # LOCAL NLP CLASSIFIER
    # =================================

    detected_type, priority, confidence = (

        detect_emergency_type(
            message
        )
    )

    # =================================
    # FETCH SERVICES
    # =================================

    services = get_all_services()

    filtered = []

    for service in services:

        if service.get("country") != country:
            continue

        if (

            service.get("service_type")
            != detected_type
        ):

            continue

        latitude_value = service.get(
            "latitude"
        )

        longitude_value = service.get(
            "longitude"
        )

        if (

            latitude_value is None

            or

            longitude_value is None
        ):

            continue

        distance = calculate_distance(

            latitude,

            longitude,

            latitude_value,

            longitude_value
        )

        if distance > 50:
            continue

        service["distance_km"] = round(
            distance,
            2
        )

        filtered.append(service)

    # =================================
    # SORT BY DISTANCE
    # =================================

    filtered.sort(

        key=lambda x: x["distance_km"]
    )

    # =================================
    # RECOMMENDED SERVICE
    # =================================

    recommended = format_service(

        filtered[0]
        if filtered
        else {}
    )

    # =================================
    # AI GUIDANCE
    # =================================

    ai_result = get_ai_guidance(

        message=message,

        latitude=latitude,

        longitude=longitude,

        nearest_service=(
            recommended.get("name")
        )
    )

    # =================================
    # DISASTER ALERTS
    # =================================

    disaster_alerts = (
        detect_disaster_alerts(
            message
        )
    )

    # =================================
    # SAVE EMERGENCY LOG
    # =================================

    save_emergency_log(

        message=message,

        detected_type=detected_type,

        priority=priority,

        confidence=confidence,

        country=country,

        classification_status=(
            "emergency"
        ),

        recommended_service=(
            recommended
        )
    )

    # =================================
    # FINAL RESPONSE
    # =================================

    return {

        "success": True,

        "classification_status":
            "EMERGENCY",

        "classification_reason":
            "Emergency intent detected",

        "proceed":
            True,

        "detected_type":
            detected_type,

        "priority":
            priority,

        "confidence":
            confidence,

        "guidance":
            ai_result["guidance"],

        "source":
            ai_result["source"],

        "suggested_actions":
            ai_result[
                "suggested_actions"
            ],

        "recommended_service":
            recommended,

        "nearby_matches_found":
            len(filtered),

        "emergency_numbers":
            emergency_numbers,

        "offline_support":
            True,

        "disaster_alerts":
            disaster_alerts
    }