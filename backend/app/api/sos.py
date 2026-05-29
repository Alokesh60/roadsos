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

from app.services.contact_service import (
    get_emergency_contacts,
    get_user_details
)

from app.services.fcm_service import (
    send_contact_alert,
    send_nearby_sos_alert
)

from app.services.responder_service import (
    find_nearby_users
)

from app.services.audit_service import (
    save_emergency_log
)

router = APIRouter()


# =====================================
# SOS ENDPOINT
# =====================================

@router.post("/sos")
async def trigger_sos(

    request: EmergencyRequest,

    user=Depends(get_current_user)

):

    # =================================
    # USER DETAILS
    # =================================

    user_id = user.get(
        "uid",
        "unknown_user"
    )

    user_name = (

        user.get("name")

        or

        user.get("email")

        or

        "RoadSOS User"
    )

    # =================================
    # AI GUIDANCE
    # =================================

    ai_result = await get_ai_guidance(

        message=request.message,

        latitude=request.latitude,

        longitude=request.longitude,

        nearby_services=request.nearby_services
    )

    detected_type = ai_result.get(
        "detected_type",
        "emergency"
    )

    # =================================
    # EMERGENCY CONTACT ALERTS
    # =================================

    emergency_notifications = []

    try:

        contacts = await get_emergency_contacts(
            user_id
        )

        for contact in contacts:

            contact_uid = contact.get(
                "uid"
            )

            if not contact_uid:

                continue

            contact_data = (

                await get_user_details(
                    contact_uid
                )
            )

            if not contact_data:

                continue

            token = contact_data.get(
                "fcm_token"
            )

            if not token:

                continue

            result = send_contact_alert(

                token=token,

                sender_uid=user_id,

                sender_name=user_name,

                latitude=request.latitude,

                longitude=request.longitude
            )

            emergency_notifications.append({

                "uid":
                    contact_uid,

                "type":
                    "emergency_contact",

                "result":
                    result
            })

    except Exception as e:

        print(
            f"[SOS_CONTACT_ALERT] {e}"
        )

    # =================================
    # NEARBY RESPONDER ALERTS
    # =================================

    responder_notifications = []

    try:

        nearby_users = (

            await find_nearby_users(

                latitude=request.latitude,

                longitude=request.longitude
            )
        )

        for responder in nearby_users:

            responder_uid = responder.get(
                "uid"
            )

            if responder_uid == user_id:

                continue

            token = responder.get(
                "fcm_token"
            )

            if not token:

                continue

            result = send_nearby_sos_alert(

                token=token,

                sender_uid=user_id,

                emergency_type=detected_type,

                latitude=request.latitude,

                longitude=request.longitude
            )

            responder_notifications.append({

                "uid":
                    responder_uid,

                "distance_km":
                    responder.get(
                        "distance_km"
                    ),

                "type":
                    "nearby_responder",

                "result":
                    result
            })

    except Exception as e:

        print(
            f"[SOS_RESPONDER_ALERT] {e}"
        )

    # =================================
    # AUDIT LOG
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

            "guidance":
                ai_result.get(
                    "guidance"
                ),

            "source":
                ai_result.get(
                    "source"
                ),

            "emergency_notifications":
                len(
                    emergency_notifications
                ),

            "responder_notifications":
                len(
                    responder_notifications
                ),

            "timestamp":
                datetime.utcnow().isoformat()
        })

    except Exception as e:

        print(
            f"[SOS_AUDIT_LOG] {e}"
        )

    # =================================
    # RESPONSE
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

        "emergency_contact_notifications":
            emergency_notifications,

        "nearby_responder_notifications":
            responder_notifications
    }