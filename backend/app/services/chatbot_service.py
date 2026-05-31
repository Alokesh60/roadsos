from dotenv import load_dotenv
load_dotenv()

import os

import httpx


# =====================================
# AI GUIDANCE SERVICE
# =====================================

AI_MODULE_URL = os.getenv(
    "AI_MODULE_URL",
    "http://127.0.0.1:8000"
)

AI_MODULE_API_KEY = os.getenv(
    "AI_MODULE_API_KEY"
)

if not AI_MODULE_API_KEY:

    raise RuntimeError(

        "AI_MODULE_API_KEY "
        "environment variable is required."
    )


# =====================================
# AI GUIDANCE FETCHER
# =====================================

async def get_ai_guidance(

    message: str,

    latitude: float,

    longitude: float,

    nearby_places: list | None = None,

    nearby_services=None
):

    try:

        async with httpx.AsyncClient(

            timeout=8.0

        ) as client:

            response = await client.post(

                f"{AI_MODULE_URL}/chat",

                headers={

                    "Authorization":
                        f"Bearer {AI_MODULE_API_KEY}"
                },

                json={

                    "user_message":
                        message,

                    "context": {

                        "lat":
                            latitude,

                        "lng":
                            longitude,

                        "nearest_police_phone":
                            (
                                nearby_services.police_phone
                                if nearby_services
                                else None
                            ),

                        "nearest_hospital_phone":
                            (
                                nearby_services.hospital_phone
                                if nearby_services
                                else None
                            ),

                        "nearest_ambulance_phone":
                            (
                                nearby_services.ambulance_phone
                                if nearby_services
                                else None
                            ),

                        "nearest_towing_phone":
                            (
                                nearby_services.towing_phone
                                if nearby_services
                                else None
                            ),

                        "is_sos_active":
                            True,

                        "nearby_places":
                            nearby_places or []
                    },

                    "history":
                        []
                }
            )

            response.raise_for_status()

            data = response.json()

            return {

                "guidance":
                    data.get(
                        "reply",
                        "Emergency guidance unavailable."
                    ),

                "source":
                    data.get(
                        "source",
                        "ai_module"
                    ),

                "detected_type":
                    data.get(
                        "intent_detected",
                        "emergency"
                    ),

                "priority":
                    data.get(
                        "priority",
                        "high"
                    ),

                "suggested_actions":
                    data.get(
                        "suggested_actions",
                        []
                    )
            }

    except httpx.TimeoutException:

        print(
            "[AI_MODULE] Request timeout."
        )

    except httpx.HTTPStatusError as e:

        print(
            f"[AI_MODULE] HTTP error: "
            f"{e.response.status_code}"
        )

    except Exception as e:

        print(
            f"[AI_MODULE] Unexpected error: {e}"
        )

    # =================================
    # FALLBACK RESPONSE
    # =================================

    return {

        "guidance":
            (
                "Emergency detected. "
                "Please stay calm and "
                "contact emergency services "
                "immediately."
            ),

        "source":
            "fallback",

        "detected_type":
            "emergency",

        "priority":
            "high",

        "suggested_actions": [

            {

                "label":
                    "Call Emergency Services",

                "number":
                    "112"
            },

            {

                "label":
                    "Call Ambulance",

                "number":
                    (
                        nearby_services.ambulance_phone
                        if (
                            nearby_services
                            and
                            nearby_services.ambulance_phone
                        )
                        else "108"
                    )
            },

            {

                "label":
                    "Call Police",

                "number":
                    (
                        nearby_services.police_phone
                        if (
                            nearby_services
                            and
                            nearby_services.police_phone
                        )
                        else "100"
                    )
            }
        ]
    }