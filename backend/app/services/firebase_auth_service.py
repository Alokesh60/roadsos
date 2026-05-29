from firebase_admin import auth


# =====================================
# VERIFY FIREBASE TOKEN
# =====================================
#
# PURPOSE:
# Verify Firebase ID tokens sent
# from Android frontend.
#
# RETURNS:
# Decoded Firebase user payload.
#
# =====================================


def verify_firebase_token(
    token: str
):

    try:

        decoded_token = (
            auth.verify_id_token(token)
        )

        return decoded_token

    except Exception as e:

        raise Exception(
            f"Firebase token verification failed: {e}"
        )