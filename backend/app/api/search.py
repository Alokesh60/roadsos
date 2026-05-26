# search.py
from fastapi import APIRouter, Query

from app.services.sqlite_service import (
    get_all_services
)

router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(...)
):
    """
    Local SQLite-based emergency service search.

    Replaces old Supabase search implementation.
    """

    query = q.lower().strip()

    services = get_all_services()

    filtered = []

    for service in services:

        searchable_text = " ".join([
            str(service.get("name", "")),
            str(service.get("service_type", "")),
            str(service.get("district", "")),
            str(service.get("state", "")),
            str(service.get("address", ""))
        ]).lower()

        if query in searchable_text:
            filtered.append(service)

    return {
        "success": True,
        "count": len(filtered),
        "query": q,
        "data": filtered
    }