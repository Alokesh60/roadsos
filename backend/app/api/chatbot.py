from fastapi import APIRouter

from app.schemas.emergency_schema import (
    EmergencyRequest
)

from app.services.chatbot_service import (
    process_emergency_chatbot
)

router = APIRouter()


@router.post("/chatbot")

async def chatbot_handler(
    request: EmergencyRequest
):

    result = process_emergency_chatbot(

        request.message,
        request.latitude,
        request.longitude
    )

    return {

        "success": True,

        "response": result
    }