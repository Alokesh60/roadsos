from datetime import datetime

from fastapi import (
    APIRouter,
    Depends
)

from app.dependencies.auth_dependency import (
    get_current_user
)

from app.schemas.emergency_schema import (
    EmergencyRequest
)

from app.services.chatbot_service import (
    get_ai_guidance
)

from app.services.notification_service import (
    build_emergency_alert,
    trigger_emergency_notifications
)

from app.services.audit_service import (
    save_emergency_log
)

router = APIRouter()


# =====================================
# SOS ENDPOINT
# =====================================
#
# PURPOSE:
# Main emergency orchestration endpoint.
#
# RESPONSIBILITY:
# ✅ Receive SOS requests
# ✅ Verify Firebase user
# ✅ Fetch AI emergency guidance
# ✅ Trigger emergency notifications
# ✅ Store emergency audit logs
# ✅ Return emergency response
#
# REMOVED:
# ❌ SQLite logging
# ❌ Nearby responder broadcast
# ❌ Offline queue system
# ❌ Local NLP classification
# ❌ Duplicate AI processing
# ❌ Nearby services search
#
# WHY:
# Android already handles:
# - Google Maps
# - Nearby services
# - Directions
# - Live location
#
# AI processing now belongs to:
# ai_module/chatbot
#
# Backend should ONLY:
# - orchestrate SOS
# - trigger notifications
# - communicate with AI module
#
# =====================================


@router.post("/sos")

async def trigger_sos(

    request: EmergencyRequest,

    user=Depends(get_current_user)
):

    # =================================
    # USER DETAILS
    # =================================

    user_name = (

        user.get("name")

        or

        user.get("email")

        or

        "RoadSOS User"
    )

    user_id = user.get(
        "uid",
        "unknown_user"
    )

    # =================================
    # CONTACT VALIDATION
    # =================================

    emergency_contacts = (
        request.contacts or []
    )

    if len(emergency_contacts) > 5:

        return {

            "success": False,

            "message":
                "Maximum 5 emergency contacts allowed."
        }

    # =================================
    # AI GUIDANCE
    # =================================

    ai_result = await get_ai_guidance(

    message=request.message,

    latitude=request.latitude,

    longitude=request.longitude,

    nearby_places=[
        place.model_dump()
        for place in request.nearby_places
    ]
)

    # =================================
    # DETECTED TYPE
    # =================================

    detected_type = ai_result.get(
        "detected_type",
        "emergency"
    )

    # =================================
    # BUILD ALERT MESSAGE
    # =================================

    alert_message = (

        build_emergency_alert(

            user_name=user_name,

            emergency_description=(
                request.message
            ),

            service_type=(
                detected_type
            ),

            latitude=(
                request.latitude
            ),

            longitude=(
                request.longitude
            ),

            priority=(
                ai_result.get(
                    "priority",
                    "high"
                )
            )
        )
    )

    # =================================
    # SEND EMERGENCY ALERTS
    # =================================

    notification_results = []

    if emergency_contacts:

        try:

            notification_results = (

                trigger_emergency_notifications(

                    emergency_contacts,

                    alert_message
                )
            )

        except Exception as e:

            print(
                f"[SOS] Notification failed: {e}"
            )

    # =================================
    # SAVE AUDIT LOG
    # =================================

    try:

        await save_emergency_log({

            "user_id":
                user_id,

            "user_name":
                user_name,

            "message":
                request.message,

            "latitude":
                request.latitude,

            "longitude":
                request.longitude,

            "detected_type":
                detected_type,

            "priority":
                ai_result.get(
                    "priority",
                    "high"
                ),

            "notifications":
                notification_results,

            "timestamp":
                datetime.utcnow().isoformat(),

            "source":
                "backend_sos"
        })

    except Exception as e:

        print(
            f"[SOS] Audit logging failed: {e}"
        )

    # =================================
    # FINAL RESPONSE
    # =================================

    return {

        "success": True,

        "sos_triggered": True,

        "message":
            "Emergency SOS triggered successfully.",

        "guidance":
            ai_result.get(
                "guidance"
            ),

        "source":
            ai_result.get(
                "source"
            ),

        "detected_type":
            detected_type,

        "priority":
            ai_result.get(
                "priority",
                "high"
            ),

        "suggested_actions":
            ai_result.get(
                "suggested_actions",
                []
            ),

        "notifications":
            notification_results
    }