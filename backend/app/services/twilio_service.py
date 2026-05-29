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
# VALIDATE CONFIG
# =====================================

if not ACCOUNT_SID or not AUTH_TOKEN:

    raise Exception(
        "Twilio credentials missing in .env"
    )


# =====================================
# TWILIO CLIENT
# =====================================

client = Client(

    ACCOUNT_SID,

    AUTH_TOKEN
)


# =====================================
# PHONE VALIDATION
# =====================================

def is_valid_phone_number(
    phone_number: str
):

    if not phone_number:

        return False

    phone_number = (
        phone_number.strip()
    )

    return (
        phone_number.startswith("+")
        and len(phone_number) >= 10
    )


# =====================================
# SEND WHATSAPP ALERT
# =====================================

def send_whatsapp_alert(

    phone_number: str,

    message: str
):

    try:

        # =============================
        # VALIDATE PHONE
        # =============================

        if not is_valid_phone_number(
            phone_number
        ):

            return {

                "success": False,

                "type": "whatsapp",

                "error":
                    "Invalid phone number"
            }

        # =============================
        # SEND MESSAGE
        # =============================

        response = client.messages.create(

            body=message,

            from_=(
                f"whatsapp:"
                f"{TWILIO_WHATSAPP_NUMBER}"
            ),

            to=(
                f"whatsapp:"
                f"{phone_number}"
            )
        )

        return {

            "success": True,

            "type": "whatsapp",

            "sid": response.sid
        }

    except Exception as e:

        print(
            f"[Twilio WhatsApp Error] {e}"
        )

        return {

            "success": False,

            "type": "whatsapp",

            "error": str(e)
        }


# =====================================
# MAKE EMERGENCY VOICE CALL
# =====================================

def make_emergency_call(

    phone_number: str,

    message: str
):

    try:

        # =============================
        # VALIDATE PHONE
        # =============================

        if not is_valid_phone_number(
            phone_number
        ):

            return {

                "success": False,

                "type": "voice_call",

                "error":
                    "Invalid phone number"
            }

        # =============================
        # TWIML RESPONSE
        # =============================

        twiml = f"""
<Response>
<Say voice="alice">
{message}
</Say>
</Response>
"""

        # =============================
        # CREATE CALL
        # =============================

        call = client.calls.create(

            twiml=twiml,

            to=phone_number,

            from_=TWILIO_CALL_NUMBER
        )

        return {

            "success": True,

            "type": "voice_call",

            "call_sid": call.sid
        }

    except Exception as e:

        print(
            f"[Twilio Call Error] {e}"
        )

        return {

            "success": False,

            "type": "voice_call",

            "error": str(e)
        }