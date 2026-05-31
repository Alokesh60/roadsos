from firebase_admin import firestore


def _db():
    return firestore.client()


# =====================================
# SAVE SOS EVENT
# =====================================

async def save_emergency_log(data: dict):

    _db().collection(
        "emergency_logs"
    ).add(data)


# =====================================
# GET SOS HISTORY
# =====================================

async def get_emergency_history():

    docs = (
        _db().collection("emergency_logs")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .stream()
    )

    history = []

    for doc in docs:

        item = doc.to_dict()

        item["id"] = doc.id

        history.append(item)

    return history
