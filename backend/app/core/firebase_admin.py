import os

from dotenv import load_dotenv

import firebase_admin

from firebase_admin import credentials


# =====================================
# LOAD ENV
# =====================================

load_dotenv()


# =====================================
# FIREBASE ADMIN INITIALIZATION
# =====================================
#
# PURPOSE:
# Initialize Firebase Admin SDK
# for backend authentication.
#
# REQUIRED ENV VARIABLE:
#
# FIREBASE_SERVICE_ACCOUNT
#
# Example:
# FIREBASE_SERVICE_ACCOUNT=./firebase-service-account.json
#
# =====================================

def initialize_firebase():

    try:

        # =============================
        # PREVENT REINITIALIZATION
        # =============================

        if firebase_admin._apps:

            return firebase_admin.get_app()

        # =============================
        # GET SERVICE ACCOUNT PATH
        # =============================

        firebase_cred_path = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT"
        )

        if not firebase_cred_path:

            raise Exception(
                "FIREBASE_SERVICE_ACCOUNT env variable missing"
            )

        # =============================
        # VALIDATE FILE
        # =============================

        if not os.path.exists(
            firebase_cred_path
        ):

            raise Exception(
                f"Firebase credential file not found: "
                f"{firebase_cred_path}"
            )

        # =============================
        # INITIALIZE FIREBASE
        # =============================

        cred = credentials.Certificate(
            firebase_cred_path
        )

        firebase_admin.initialize_app(
            cred
        )

        print(
            "[Firebase] Firebase Admin initialized."
        )

        return firebase_admin.get_app()

    except Exception as e:

        print(
            f"[Firebase Init Error] {e}"
        )

        raise