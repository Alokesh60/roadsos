from pydantic import BaseModel
from typing import Optional


class EmergencyServiceSchema(BaseModel):

    id: int

    name: str

    type: str

    phone: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None

    state: Optional[str] = None

    country: Optional[str] = None

    latitude: float

    longitude: float

    rating: Optional[float] = None

    availability: Optional[bool] = None

    verified: Optional[bool] = None

    source: Optional[str] = None

    distance_km: Optional[float] = None

    emergency_score: Optional[float] = None

    ai_priority: Optional[str] = None