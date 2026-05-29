from dotenv import load_dotenv

import os


# =====================================
# LOAD ENV
# =====================================

load_dotenv()


# =====================================
# SETTINGS
# =====================================

class Settings:

    """
    RoadSOS Backend Configuration

    Backend responsibilities:
    - Firebase authentication
    - SOS orchestration
    - Twilio notifications
    - AI module communication
    """

    # =================================
    # FIREBASE
    # =================================

    FIREBASE_SERVICE_ACCOUNT = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT",
        "firebase-service-account.json"
    )

    # =================================
    # AI MODULE
    # =================================

    AI_MODULE_URL = os.getenv(
        "AI_MODULE_URL",
        "http://127.0.0.1:8000"
    )

    # =================================
    # TWILIO
    # =================================

    TWILIO_ACCOUNT_SID = os.getenv(
        "TWILIO_ACCOUNT_SID",
        ""
    )

    TWILIO_AUTH_TOKEN = os.getenv(
        "TWILIO_AUTH_TOKEN",
        ""
    )

    TWILIO_WHATSAPP_NUMBER = os.getenv(
        "TWILIO_WHATSAPP_NUMBER",
        ""
    )

    TWILIO_CALL_NUMBER = os.getenv(
        "TWILIO_CALL_NUMBER",
        ""
    )

    # =================================
    # ENVIRONMENT
    # =================================

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "true"
    ).lower() == "true"


# =====================================
# SETTINGS INSTANCE
# =====================================

settings = Settings()