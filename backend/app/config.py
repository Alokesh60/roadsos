from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    """
    Central backend configuration.

    Current architecture:
    - Firebase authentication
    - SQLite local database
    - Separate ai_module service
    - Gemini API integration
    """

    # ================================
    # FIREBASE
    # ================================

    FIREBASE_SERVICE_ACCOUNT = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT",
        "firebase-service-account.json"
    )

    # ================================
    # SQLITE DATABASE
    # ================================

    SQLITE_DB_PATH = os.getenv(
        "SQLITE_DB_PATH",
        "roadsos.db"
    )

    OFFLINE_DB_PATH = os.getenv(
        "OFFLINE_DB_PATH",
        "roadsos_offline.db"
    )

    # ================================
    # AI MODULE
    # ================================

    AI_MODULE_URL = os.getenv(
        "AI_MODULE_URL",
        "http://127.0.0.1:8000"
    )

    # ================================
    # GEMINI
    # ================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    # ================================
    # ENVIRONMENT
    # ================================

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "true"
    ).lower() == "true"


settings = Settings()