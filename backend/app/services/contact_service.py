from app.db.client import supabase


def create_contact(data: dict):

    response = supabase.table(
        "emergency_contacts"
    ).insert(data).execute()

    return response.data


def get_contacts(user_id: str):

    response = supabase.table(
        "emergency_contacts"
    ).select("*").eq(
        "user_id",
        user_id
    ).execute()

    return response.data


def delete_contact(contact_id: int):

    response = supabase.table(
        "emergency_contacts"
    ).delete().eq(
        "id",
        contact_id
    ).execute()

    return response.data