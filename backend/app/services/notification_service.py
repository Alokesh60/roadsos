# notification_service.py
from datetime import datetime

from app.services.twilio_service import (
    send_whatsapp_alert
)


# =====================================
# BUILD EMERGENCY ALERT
# =====================================

def build_emergency_alert(

    user_name: str,

    emergency_description, service_type: str,

    latitude: float,

    longitude: float,

    priority: str
):

    maps_link = (

        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    timestamp = datetime.now().strftime(

        "%d-%m-%Y %I:%M %p"
    )

    message = f"""

🚨 ROADSOS EMERGENCY ALERT 🚨

User:
{user_name}

Emergency:
{emergency_description}

Emergency Service Needed:
{service_type.upper()}

Priority:
{priority.upper()}

Possible emergency detected.

The user may require
immediate assistance.

📍 Live Location:
{maps_link}

Latitude:
{latitude}

Longitude:
{longitude}

🕒 Time:
{timestamp}

Please contact the user or
emergency services immediately.

RoadSOS Automated Emergency System

"""

    return message


# =====================================
# TRIGGER EMERGENCY NOTIFICATIONS
# =====================================

def trigger_emergency_notifications(

    contacts: list,

    message: str
):

    notification_results = []

    for contact in contacts:

        phone = contact.get(
            "phone"
        )

        name = contact.get(
            "name"
        )

        print(
            "\n========== ALERT =========="
        )

        print(
            "Sending emergency alert to:"
        )

        print(
            f"Name: {name}"
        )

        print(
            f"Phone: {phone}"
        )

        print(message)

        print(
            "===========================\n"
        )

        # =================================
        # WHATSAPP ALERT
        # =================================

        try:

            send_whatsapp_alert(

                phone_number=phone,

                message=message
            )

            status = "WHATSAPP_SENT"

        except Exception as e:

            print(
                f"WhatsApp failed: {e}"
            )

            status = "WHATSAPP_FAILED"

        notification_results.append({

            "name":
                name,

            "phone":
                phone,

            "status":
                status
        })

    return notification_results

