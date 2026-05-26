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
    process_emergency_chatbot
)

from app.services.notification_service import (
    build_emergency_alert,
    trigger_emergency_notifications
)

from app.services.broadcast_service import (

    find_nearby_users,

    build_sos_message,

    broadcast_sos_alert
)

from app.db.sqlite_db import (
    get_connection
)


router = APIRouter()


# =====================================
# STORE SOS EVENT
# =====================================

def save_sos_event(

    user_id: str,

    emergency_type: str,

    latitude: float,

    longitude: float,

    message: str,

    source: str
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO sos_events (

            user_id,

            emergency_type,

            latitude,

            longitude,

            message,

            source

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (

            user_id,

            emergency_type,

            latitude,

            longitude,

            message,

            source
        )
    )

    conn.commit()

    conn.close()


# =====================================
# OFFLINE ALERT QUEUE
# =====================================

def queue_offline_alert(

    phone: str,

    message: str
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO offline_alert_queue (

            phone,

            message,

            status

        )

        VALUES (?, ?, ?)
        """,

        (

            phone,

            message,

            "PENDING"
        )
    )

    conn.commit()

    conn.close()


# =====================================
# SOS ENDPOINT
# =====================================

@router.post("/sos")

async def trigger_sos(

    request: EmergencyRequest,

    user=Depends(get_current_user)
):

    # =================================
    # PROCESS EMERGENCY
    # =================================

    result = process_emergency_chatbot(

        message=request.message,

        latitude=request.latitude,

        longitude=request.longitude,

        country=request.country
    )

    detected_type = result.get(
        "detected_type",
        "hospital"
    )

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
    # EMERGENCY MESSAGE
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
                result.get(
                    "priority",
                    "high"
                )
            )
        )
    )

    # =================================
    # CONTACTS
    # =================================

    emergency_contacts = request.contacts

    notification_results = []

    # =================================
    # SEND WHATSAPP ALERTS
    # =================================

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
                f"Notification failed: {e}"
            )

            # =========================
            # OFFLINE QUEUE
            # =========================

            for contact in emergency_contacts:

                phone = contact.get(
                    "phone"
                )

                if phone:

                    queue_offline_alert(

                        phone,

                        alert_message
                    )

    # =================================
    # NEARBY RESPONDER BROADCAST
    # =================================

    nearby_users = find_nearby_users(

        latitude=request.latitude,

        longitude=request.longitude,

        current_uid=user_id,

        radius_km=10
    )

    community_message = (

        build_sos_message(

            user_name=user_name,

            emergency_type=detected_type,

            latitude=request.latitude,

            longitude=request.longitude,

            priority=result.get(
                "priority",
                "high"
            )
        )
    )

    broadcast_results = (

        broadcast_sos_alert(

            nearby_users,

            community_message
        )
    )

    # =================================
    # STORE SOS EVENT
    # =================================

    save_sos_event(

        user_id=user_id,

        emergency_type=detected_type,

        latitude=request.latitude,

        longitude=request.longitude,

        message=request.message,

        source=result.get(
            "source",
            "unknown"
        )
    )

    # =================================
    # FINAL RESPONSE
    # =================================

    return {

        "success": True,

        "sos_triggered": True,

        "detected_type":
            detected_type,

        "priority":
            result.get(
                "priority"
            ),

        "guidance":
            result.get(
                "guidance"
            ),

        "recommended_service":
            result.get(
                "recommended_service"
            ),

        "notifications":
            notification_results,

        "nearby_responders":
            nearby_users,

        "broadcast_results":
            broadcast_results,

        "offline_support":
            True,

        "data":
            result
    }