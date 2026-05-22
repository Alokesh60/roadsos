from fastapi import APIRouter

from app.services.chroma_service import (
    semantic_emergency_classification
)

router = APIRouter()


@router.get("/ai-emergency")

async def ai_emergency(
    query: str
):

    result = (
        semantic_emergency_classification(
            query
        )
    )

    return {

        "success": True,

        "query": query,

        "ai_result": result
    }