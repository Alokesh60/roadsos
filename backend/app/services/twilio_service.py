import os

from dotenv import load_dotenv

from twilio.rest import Client


load_dotenv()


# =====================================
# ENV VARIABLES
# =====================================

ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID"
)

AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN"
)

TWILIO_WHATSAPP_NUMBER = os.getenv(
    "TWILIO_WHATSAPP_NUMBER"
)

TWILIO_CALL_NUMBER = os.getenv(
    "TWILIO_CALL_NUMBER"
)


# =====================================
# TWILIO CLIENT
# =====================================

client = Client(

    ACCOUNT_SID,

    AUTH_TOKEN
)


# =====================================
# SEND WHATSAPP ALERT
# =====================================

def send_whatsapp_alert(

    phone_number: str,

    message: str
):

    try:

        if not phone_number.startswith("+"):

            return {

                "success": False,

                "error":
                    "Phone number must include country code"
            }

        response = client.messages.create(

            body=message,

            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",

            to=f"whatsapp:{phone_number}"
        )

        return {

            "success": True,

            "type":
                "whatsapp",

            "sid":
                response.sid
        }

    except Exception as e:

        print(
            f"WhatsApp Error: {e}"
        )

        return {

            "success": False,

            "type":
                "whatsapp",

            "error":
                str(e)
        }


# =====================================
# EMERGENCY VOICE CALL
# =====================================

def make_emergency_call(

    phone_number: str,

    message: str
):

    try:

        if not phone_number.startswith("+"):

            return {

                "success": False,

                "error":
                    "Phone number must include country code"
            }

        twiml = f"""

<Response>

<Say voice="alice">

{message}

</Say>

</Response>

"""

        call = client.calls.create(

            twiml=twiml,

            to=phone_number,

            from_=TWILIO_CALL_NUMBER
        )

        return {

            "success": True,

            "type":
                "voice_call",

            "call_sid":
                call.sid
        }

    except Exception as e:

        print(
            f"Call Error: {e}"
        )

        return {

            "success": False,

            "type":
                "voice_call",

            "error":
                str(e)
        }