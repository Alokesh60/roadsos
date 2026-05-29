from datetime import datetime

from app.services.twilio_service import (
    send_whatsapp_alert
)


# =====================================
# BUILD EMERGENCY ALERT
# =====================================

def build_emergency_alert(
    user_name: str,
    emergency_description: str,
    service_type: str,
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
🚨 ROADSOS SOS ALERT 🚨

User: {user_name}

Emergency:
{emergency_description}

Service Needed:
{service_type.upper()}

Priority:
{priority.upper()}

📍 Live Location:
{maps_link}

🕒 Time:
{timestamp}

Please contact the user
or emergency services immediately.
"""

    return message.strip()


# =====================================
# PHONE VALIDATION
# =====================================

def is_valid_phone(phone: str):

    if not phone:
        return False

    phone = phone.strip()

    return (
        phone.startswith("+")
        and len(phone) >= 10
    )


# =====================================
# TRIGGER EMERGENCY NOTIFICATIONS
# =====================================

def trigger_emergency_notifications(
    contacts: list,
    message: str
):

    if not contacts:

        return []

    notification_results = []

    for contact in contacts:

        phone = (
            contact.get("phone", "")
            .strip()
        )

        name = (
            contact.get("name", "Unknown")
            .strip()
        )

        # =============================
        # INVALID PHONE
        # =============================

        if not is_valid_phone(phone):

            notification_results.append({

                "name": name,

                "phone": phone,

                "status": "INVALID_PHONE"
            })

            continue

        # =============================
        # SEND WHATSAPP ALERT
        # =============================

        try:

            send_whatsapp_alert(

                phone_number=phone,

                message=message
            )

            status = "WHATSAPP_SENT"

        except Exception as e:

            print(
                f"[Twilio Error] "
                f"{phone}: {e}"
            )

            status = "WHATSAPP_FAILED"

        notification_results.append({

            "name": name,

            "phone": phone,

            "status": status
        })

    return notification_results