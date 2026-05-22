from fastapi import APIRouter

from app.schemas.emergency_schema import (
    EmergencyRequest
)

from app.services.chatbot_service import (
    process_emergency_chatbot
)

router = APIRouter()


@router.post("/sos")

async def trigger_sos(
    request: EmergencyRequest
):

    result = process_emergency_chatbot(

        message=request.message,

        latitude=request.latitude,

        longitude=request.longitude,

        country=request.country
    )

    return {

        "success": True,

        "sos_triggered": True,

        "data": result
    }