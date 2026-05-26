from firebase_admin import messaging


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
# EMERGENCY ALERT
# =====================================

def send_emergency_alert(

    token: str,

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

        title="🚨 Emergency Nearby",

        body=(
            f"{emergency_type.upper()} "
            f"reported nearby."
        ),

        data={

            "type":
                "emergency_alert",

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


# =====================================
# DISASTER ALERT
# =====================================

def send_disaster_alert(

    token: str,

    disaster_type: str,

    location: str
):

    return send_push_notification(

        token=token,

        title="⚠ Disaster Warning",

        body=(
            f"{disaster_type} "
            f"alert in {location}"
        ),

        data={

            "type":
                "disaster_alert",

            "disaster_type":
                disaster_type,

            "location":
                location
        }
    )