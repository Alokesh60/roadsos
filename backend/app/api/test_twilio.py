from fastapi import APIRouter

from app.services.twilio_service import (
    send_whatsapp_alert
)

router = APIRouter()


@router.get("/test-whatsapp")

async def test_whatsapp():

    result = send_whatsapp_alert(

        phone_number="+916000934979",

        message="""
🚨 RoadSOS Emergency Test

This is a WhatsApp test alert.
"""
    )

    return result