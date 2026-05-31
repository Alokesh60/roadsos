from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


# =====================================
# NEARBY PLACE
# =====================================

class NearbyPlace(
    BaseModel
):

    id: Optional[str] = None

    category: str

    name: str

    phone: Optional[str] = None

    latitude: float

    longitude: float

    rating: Optional[float] = None

    isOpenNow: Optional[bool] = None

    distanceMeters: Optional[float] = None

    estimatedEtaMinutes: Optional[int] = None


# =====================================
# NEARBY SERVICES
# =====================================

class NearbyServices(
    BaseModel
):

    police_phone: Optional[str] = None

    hospital_phone: Optional[str] = None

    ambulance_phone: Optional[str] = None

    towing_phone: Optional[str] = None


# =====================================
# EMERGENCY REQUEST
# =====================================

class EmergencyRequest(
    BaseModel
):

    message: str

    latitude: float

    longitude: float

    country: str = "India"

    nearby_services: NearbyServices = (
        NearbyServices()
    )

    nearby_places: list[NearbyPlace] = Field(
        default_factory=list
    )

    source: str = "mobile_app"

    offline_mode: bool = False