from fastapi import APIRouter, Depends
import requests

from app.services.broadcast_service import (
    find_nearby_users,
    build_sos_message,
    broadcast_sos_alert
)

from app.services.notification_service import (
    build_emergency_alert,
    trigger_emergency_notifications
)

from app.dependencies.auth_dependency import (
    get_current_user
)

from app.services.contact_service import (
    get_contacts
)

from app.services.distance_service import (
    calculate_distance
)

from app.services.ai_scoring_service import (
    calculate_emergency_score
)

from app.services.maps_service import (
    fetch_live_services
)

from app.services.emergency_nlp_service import (
    detect_emergency_type
)

router = APIRouter()


@router.get("/ai-emergency")
async def ai_emergency(

    query: str,

    lat: float,

    lon: float,

    country: str = "India",

    user=Depends(get_current_user)
):

    # =====================================
    # EMERGENCY CLASSIFICATION
    # =====================================

    service_type, priority, confidence = (
        detect_emergency_type(query)
    )

    # =====================================
    # AI RESULT
    # =====================================

    result = {

        "classification_status": "REAL",

        "detected_service_type": service_type,

        "priority": priority,

        "confidence": confidence
    }

    # =====================================
    # FETCH LIVE SERVICES
    # =====================================

    live_services = fetch_live_services(

        lat,

        lon,

        service_type
    )

    enhanced_services = []

    for service in live_services:

        distance = calculate_distance(

            lat,

            lon,

            service["latitude"],

            service["longitude"]
        )

        service["distance_km"] = round(
            distance,
            2
        )

        service["availability"] = True

        service["emergency_score"] = (
            calculate_emergency_score(service)
        )

        if service["emergency_score"] >= 80:

            service["ai_priority"] = "HIGH"

        elif service["emergency_score"] >= 50:

            service["ai_priority"] = "MEDIUM"

        else:

            service["ai_priority"] = "LOW"

        enhanced_services.append(service)

    enhanced_services.sort(

        key=lambda x: (
            -x["emergency_score"],
            x["distance_km"]
        )
    )

    # =====================================
    # EMERGENCY CONTACTS
    # =====================================

    uid = user.get("uid")

    try:

        emergency_contacts = get_contacts(uid)

    except Exception as e:

        print(f"Contacts fetch failed: {e}")

        emergency_contacts = []

    severity = priority

    # =====================================
    # NEARBY RESPONDERS
    # =====================================

    nearby_users = find_nearby_users(

        latitude=lat,

        longitude=lon,

        current_uid=uid,

        radius_km=10
    )

    # =====================================
    # COMMUNITY BROADCAST
    # =====================================

    community_alert_message = (

        build_sos_message(

            user_name=(
                user.get("name")
                or user.get("email")
                or "RoadSOS User"
            ),

            emergency_type=service_type,

            latitude=lat,

            longitude=lon,

            priority=severity
        )
    )

    broadcast_results = (

        broadcast_sos_alert(

            nearby_users,

            community_alert_message
        )
    )

    # =====================================
    # EMERGENCY CONTACT ALERT
    # =====================================

    alert_message = (

        build_emergency_alert(

            user_name=(
                user.get("name")
                or user.get("email")
                or "RoadSOS User"
            ),

            emergency_description=query,

            service_type=service_type,

            latitude=lat,

            longitude=lon,

            priority=severity
        )
    )

    notification_results = (

        trigger_emergency_notifications(

            emergency_contacts,

            alert_message
        )
    )

    # =====================================
    # AI GUIDANCE (NEW AI MODULE)
    # =====================================

    try:

        ai_response = requests.post(

            "http://127.0.0.1:8000/chat",

            json={

                "user_message": query,

                "context": {

                    "lat": lat,

                    "lng": lon,

                    "state": None,

                    "district": None,

                    "nearest_hospital": (
                        enhanced_services[0]["name"]
                        if enhanced_services
                        else None
                    ),

                    "is_sos_active": True
                },

                "history": []
            },

            timeout=5
        )

        if ai_response.status_code == 200:

            ai_data = ai_response.json()

            guidance = ai_data.get(
                "reply",
                "Emergency guidance unavailable."
            )

            ai_source = ai_data.get(
                "source",
                "offline_template"
            )

            detected_intent = ai_data.get(
                "intent_detected",
                service_type
            )

        else:

            guidance = (
                "Emergency guidance unavailable."
            )

            ai_source = "offline_template"

            detected_intent = service_type

    except Exception as e:

        print(f"AI module error: {e}")

        guidance = (
            "Emergency guidance unavailable."
        )

        ai_source = "offline_template"

        detected_intent = service_type

    # =====================================
    # FINAL RESPONSE
    # =====================================

    return {

        "success": True,

        "query": query,

        "intent_detected": detected_intent,

        "ai_source": ai_source,

        "ai_result": result,

        "live_services":
            enhanced_services[:5],

        "emergency_contacts":
            emergency_contacts,

        "guidance":
            guidance,

        "notifications":
            notification_results,

        "broadcast_results":
            broadcast_results,

        "nearby_responders":
            nearby_users
    }