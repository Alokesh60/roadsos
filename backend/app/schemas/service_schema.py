from pydantic import BaseModel
from typing import Optional


class EmergencyServiceSchema(BaseModel):

    id: int

    name: str

    type: str

    phone: Optional[str]

    address: Optional[str]

    city: Optional[str]

    state: Optional[str]

    country: Optional[str]

    latitude: float

    longitude: float

    rating: Optional[float]

    availability: Optional[bool]

    verified: Optional[bool]

    source: Optional[str]

    distance_km: Optional[float] = None

    emergency_score: Optional[float] = None