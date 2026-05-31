from firebase_admin import firestore


def _db():
    return firestore.client()


# =====================================
# GET EMERGENCY CONTACTS
# =====================================

async def get_emergency_contacts(
    uid: str
):

    try:

        user_doc = (

            _db().collection("users")
            .document(uid)
            .get()
        )

        if not user_doc.exists:

            return []

        data = user_doc.to_dict()

        return data.get(
            "emergency_contacts",
            []
        )

    except Exception as e:

        print(
            f"[CONTACT_SERVICE] {e}"
        )

        return []


# =====================================
# GET USER DETAILS
# =====================================

async def get_user_details(
    uid: str
):

    try:

        user_doc = (

            _db().collection("users")
            .document(uid)
            .get()
        )

        if not user_doc.exists:

            return None

        return user_doc.to_dict()

    except Exception as e:

        print(
            f"[USER_DETAILS] {e}"
        )

        return None
