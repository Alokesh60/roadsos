from pydantic import BaseModel


class EmergencyRequest(BaseModel):

    message: str

    latitude: float

    longitude: float


class EmergencyResponse(BaseModel):

    detected_type: str

    priority: str

    confidence: float

    recommended_service: dict