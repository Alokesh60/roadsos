from firebase_admin import (
    messaging,
    firestore
)

# =====================================
# FIRESTORE
# =====================================

def _db():
    return firestore.client()


# =====================================
# SEND PUSH NOTIFICATION
# =====================================

def send_push_notification(

    token: str,

    title: str,

    body: str,

    data: dict = None
):

    try:

        payload = {

            "title": title,

            "body": body
        }

        if data:

            payload.update(data)

        message = messaging.Message(

            token=token,

            data=payload,

            android=messaging.AndroidConfig(

                priority="high",
                ttl = 86400
            )
        )

        response = messaging.send(
            message
        )

        print(

            "\n========== "
            "FCM SENT =========="
        )

        print(
            f"Message ID: {response}"
        )

        print(
            "========================\n"
        )

        return {

            "success": True,

            "message_id": response
        }

    except Exception as e:

        print(

            "\n========== "
            "FCM FAILED =========="
        )

        print(
            str(e)
        )

        print(
            "========================\n"
        )

        return {

            "success": False,

            "error": str(e)
        }


# =====================================
# GET USER FCM TOKEN
# =====================================

def get_user_fcm_token(
    uid: str
):

    try:

        user_doc = (

            _db().collection("users")
            .document(uid)
            .get()
        )

        if not user_doc.exists:

            return None

        data = user_doc.to_dict()

        return data.get(
            "fcm_token"
        )

    except Exception as e:

        print(
            f"[FCM_TOKEN_ERROR] {e}"
        )

        return None


# =====================================
# EMERGENCY CONTACT ALERT
# =====================================

def send_contact_alert(

    token: str,

    sender_uid: str,

    sender_name: str,

    sender_phone: str,

    latitude: float,

    longitude: float
):

    maps_link = (

        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    return send_push_notification(

        token=token,

        title="🚨 Emergency Alert",

        body=(
            f"{sender_name} ({sender_phone}) requires "
            f"immediate assistance."
        ),

        data={

            "type":
                "sos_alert",

            "sender_uid":
                sender_uid,

            "sender_name":
                sender_name,

            "sender_phone":
                sender_phone,

            "emergency_type":
                "Emergency",

            "latitude":
                str(latitude),

            "longitude":
                str(longitude),

            "maps_link":
                maps_link
        }
    )


# =====================================
# NEARBY SOS ALERT
# =====================================

def send_nearby_sos_alert(

    token: str,

    sender_uid: str,

    sender_name: str,

    sender_phone: str,

    emergency_type: str,

    latitude: float,

    longitude: float
):

    maps_link = (

        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    return send_push_notification(

        token=token,

        title="🚨 Emergency Alert",

        body=(
            f"{sender_name} ({sender_phone}) requires immediate assistance."
        ),

        data={

            "type":
                "sos_alert",

            "sender_uid":
                sender_uid,

            "sender_name":
                sender_name,

            "sender_phone":
                sender_phone,

            "emergency_type":
                emergency_type,

            "latitude":
                str(latitude),

            "longitude":
                str(longitude),

            "maps_link":
                maps_link
        }
    )