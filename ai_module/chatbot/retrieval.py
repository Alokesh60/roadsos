from typing import List


def detect_category(message: str):

    msg = message.lower()

    if any(
        word in msg
        for word in [
            "hospital",
            "doctor",
            "medical",
            "injury",
            "injured",
            "ambulance",
            "accident",
        ]
    ):
        return "hospital"

    if any(
        word in msg
        for word in [
            "police",
            "crime",
            "theft",
            "robbery",
            "attack",
        ]
    ):
        return "police"

    if any(
        word in msg
        for word in [
            "garage",
            "repair",
            "mechanic",
            "breakdown",
            "puncture",
            "tow",
        ]
    ):
        return "garage"

    if any(
        word in msg
        for word in [
            "food",
            "restaurant",
            "hungry",
            "eat",
        ]
    ):
        return "food"

    return None


def is_best_query(message: str):

    msg = message.lower()

    keywords = [
        "best",
        "top",
        "highest rated",
        "highest-rated",
        "recommended",
        "good hospital",
        "good restaurant",
        "good garage",
    ]

    return any(
        keyword in msg
        for keyword in keywords
    )


def sort_by_rating(places):

    return sorted(
        places,
        key=lambda x: (
            x.get("rating") is None,
            -(x.get("rating") or 0),
            x.get("distanceMeters", 999999)
        )
    )


def retrieve_top_k(
    message: str,
    places: List[dict],
    k: int = 3,
):

    if not places:
        return []

    category = detect_category(message)

    if category:

        filtered = [

            p for p in places

            if p.get("category") == category
        ]

        if is_best_query(message):

            filtered = sort_by_rating(filtered)

        else:

            filtered = sorted(
                filtered,
                key=lambda x: x.get(
                    "distanceMeters",
                    999999
                )
            )

        return filtered[:k]

    # Generic queries
    if is_best_query(message):

        places = sort_by_rating(places)

    else:

        places = sorted(
            places,
            key=lambda x: x.get(
                "distanceMeters",
                999999
            )
        )

    return places[:k]