from fastapi import (
    APIRouter
)

from app.schemas.emergency_schema import (
    EmergencyRequest,
    EmergencyResponse
)

from app.services.emergency_nlp_service import (
    detect_emergency_type
)

from app.services.sqlite_service import (
    get_nearest_services
)

router = APIRouter()


# =====================================
# EMERGENCY HANDLER
# =====================================

@router.post(

    "/emergency",

    response_model=EmergencyResponse
)

async def emergency_handler(

    request: EmergencyRequest
):

    # =================================
    # DETECT EMERGENCY
    # =================================

    detected_type, priority, confidence = (

        detect_emergency_type(
            request.message
        )
    )

    # =================================
    # FETCH NEAREST SERVICES
    # =================================

    nearby_services = (

        get_nearest_services(

            latitude=request.latitude,

            longitude=request.longitude,

            service_type=detected_type,

            radius_km=50
        )
    )

    # =================================
    # RECOMMENDED SERVICE
    # =================================

    recommended = (

        nearby_services[0]

        if nearby_services

        else {}
    )

    # =================================
    # DISASTER ALERTS
    # =================================

    disaster_alerts = []

    message = request.message.lower()

    if "flood" in message:

        disaster_alerts.append(
            "⚠ Flood warning detected."
        )

    if "landslide" in message:

        disaster_alerts.append(
            "⚠ Landslide-prone area."
        )

    if "storm" in message:

        disaster_alerts.append(
            "⚠ Thunderstorm warning."
        )

    if "heavy rain" in message:

        disaster_alerts.append(
            "⚠ Heavy rainfall alert."
        )

    # =================================
    # RESPONSE
    # =================================

    return {

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

        "recommended_service":
            recommended,

        "guidance":
            (
                "Please contact the "
                "nearest emergency service "
                "immediately."
            ),

        "source":
            (
                "offline_db"
                if request.offline_mode
                else "hybrid"
            ),

        "offline_support":
            True,

        "disaster_alerts":
            disaster_alerts
    }