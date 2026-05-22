from pydantic import BaseModel


class EmergencyRequest(BaseModel):

    message: str

    latitude: float

    longitude: float

    country: str = "India"


class EmergencyResponse(BaseModel):

    classification_status: str

    classification_reason: str

    proceed: bool

    detected_type: str

    priority: str

    confidence: float

    recommended_service: dict

    guidance: str

    semantic_matches_found: int