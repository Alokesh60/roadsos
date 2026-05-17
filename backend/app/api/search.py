from fastapi import APIRouter, Query

from app.services.supabase_service import search_services

router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(...)
):

    results = search_services(q)

    return {
        "success": True,
        "count": len(results),
        "query": q,
        "data": results
    }