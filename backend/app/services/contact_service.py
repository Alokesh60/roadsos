def create_contact(data: dict):

    print(
        "[INFO] create_contact called"
    )

    return data


def get_contacts(user_id: str):

    print(
        f"[INFO] get_contacts called for {user_id}"
    )

    # Temporary mock contacts
    return [

        {
            "id": 1,
            "name": "Emergency Contact",
            "phone": "+911234567890",
            "relationship": "Family"
        }
    ]


def delete_contact(contact_id: int):

    print(
        f"[INFO] delete_contact called for {contact_id}"
    )

    return {

        "success": True,

        "deleted_contact_id": contact_id
    }