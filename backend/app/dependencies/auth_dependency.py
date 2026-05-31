from fastapi import (

    Header,

    HTTPException
)

import logging

from app.services.firebase_auth_service import (
    verify_firebase_token
)


log = logging.getLogger(__name__)


# =====================================
# FIREBASE AUTH DEPENDENCY
# =====================================
#
# PURPOSE:
# Verify Firebase ID token sent
# from Android frontend.
#
# ANDROID SHOULD SEND:
#
# Authorization: Bearer <firebase_id_token>
#
# =====================================


def get_current_user(

    authorization: str = Header(None)

):

    # =================================
    # CHECK HEADER
    # =================================

    if not authorization:

        raise HTTPException(

            status_code=401,

            detail="Authorization header missing"
        )

    # =================================
    # CHECK FORMAT
    # =================================

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(

            status_code=401,

            detail="Invalid authorization format"
        )

    try:

        # =================================
        # EXTRACT TOKEN
        # =================================

        token = authorization.replace(
            "Bearer ",
            ""
        )

        # =================================
        # VERIFY FIREBASE TOKEN
        # =================================

        decoded_token = (

            verify_firebase_token(
                token
            )
        )

        return {

            "uid":
                decoded_token.get("uid"),

            "email":
                decoded_token.get("email"),

            "name":
                decoded_token.get(
                    "name",
                    "RoadSOS User"
                )
        }

    except Exception as e:

        log.warning(
            "Firebase token verification failed: %s",
            e
        )

        raise HTTPException(

            status_code=401,

            detail="Invalid authentication token"
        )
