from firebase_admin import auth


def verify_firebase_token(
    token: str
):

    decoded_token = (
        auth.verify_id_token(token)
    )

    return decoded_token