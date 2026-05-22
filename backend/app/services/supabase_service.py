from app.db.client import supabase


def get_all_services():
    response = (
        supabase
        .table("emergency_services")
        .select("*")
        .execute()
    )

    return response.data


def search_services(query: str):

    response = (
        supabase
        .table("emergency_services")
        .select("*")
        .ilike("name", f"%{query}%")
        .execute()
    )

    return response.data