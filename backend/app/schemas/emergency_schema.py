from pydantic import BaseModel


class EmergencyRequest(BaseModel):

    message: str

    latitude: float

    longitude: float


class EmergencyResponse(BaseModel):

    detected_type: str

    priority: str

    recommended_service: dict