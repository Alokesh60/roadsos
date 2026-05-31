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

        message = messaging.Message(

            notification=messaging.Notification(

                title=title,

                body=body
            ),

            data=(
                data
                if data
                else {}
            ),

            android=messaging.AndroidConfig(

                priority="high",

                notification=(
                    messaging.AndroidNotification(

                        sound="default",

                        channel_id="roadsos_emergency",

                        priority="high"
                    )
                )
            ),

            token=token
        )

        response = messaging.send(
            message
        )

        print(

            "\n========== "
            "FCM SENT =========="
        )

        print(
            f"Token: {token}"
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

    latitude: float,

    longitude: float
):

    maps_link = (

        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    return send_push_notification(

        token=token,

        title="🚨 Emergency Contact Alert",

        body=(
            f"{sender_name} may "
            f"need immediate assistance."
        ),

        data={

            "type":
                "emergency_contact",

            "sender_uid":
                sender_uid,

            "sender_name":
                sender_name,

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

        title="🚨 SOS Nearby",

        body=(
            "A RoadSOS user nearby "
            "may require assistance."
        ),

        data={

            "type":
                "nearby_sos",

            "sender_uid":
                sender_uid,

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
