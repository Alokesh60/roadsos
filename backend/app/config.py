from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    FIREBASE_SERVICE_ACCOUNT = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT",
        "firebase-service-account.json"
    )

    AI_MODULE_URL = os.getenv(
        "AI_MODULE_URL",
        "http://127.0.0.1:8000"
    )

    AI_MODULE_API_KEY = os.getenv(
        "AI_MODULE_API_KEY",
        ""
    )


settings = Settings()