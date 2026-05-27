import os

import httpx


# =====================================
# AI GUIDANCE SERVICE
# =====================================
#
# PURPOSE:
# Backend ↔ ai_module integration layer.
#
# RESPONSIBILITY:
# ✅ Send emergency context to ai_module
# ✅ Receive AI emergency guidance
# ✅ Handle AI failures safely
# ✅ Provide fallback emergency guidance
#
# ARCHITECTURE:
#
# Android:
# - Maps
# - Places
# - GPS
# - Routing
#
# Backend:
# - SOS orchestration
# - Notifications
# - Firebase auth
# - AI integration
#
# ai_module:
# - Emergency intelligence
# - AI guidance
# - Intent classification
# - Offline fallback logic
#
# =====================================


# =====================================
# ENV CONFIG
# =====================================

AI_MODULE_URL = os.getenv(
    "AI_MODULE_URL",
    "http://127.0.0.1:8000"
)

AI_MODULE_API_KEY = os.getenv(
    "AI_MODULE_API_KEY",
    ""
)


# =====================================
# AI GUIDANCE FETCHER
# =====================================

async def get_ai_guidance(

    message: str,

    latitude: float,

    longitude: float
):

    """
    Fetch AI emergency guidance
    from ai_module service.
    """

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

                        "is_sos_active":
                            True
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
                        "detected_type",
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

            "Call emergency services",

            "Share your live location",

            "Move to a safe area",

            "Contact trusted emergency contacts"
        ]
    }