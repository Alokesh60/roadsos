from fastapi import APIRouter

from app.services.history_service import (
    get_emergency_history
)

from app.schemas.emergency_schema import (
    EmergencyRequest
)

from app.services.chatbot_service import (
    process_emergency_chatbot
)

router = APIRouter()

@router.get("/history")

def get_history():

    return {

        "history": get_emergency_history()
    }

@router.post("/chatbot")

async def chatbot_handler(
    request: EmergencyRequest
):

    result = process_emergency_chatbot(

        request.message,
        request.latitude,
        request.longitude,
        request.country
    )

    return {

        "success": True,

        "response": result
    }