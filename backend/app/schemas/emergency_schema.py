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
class NearbyPlace(
    BaseModel
):

    id: str

    category: str

    name: str

    phone: str

    latitude: float

    longitude: float

    rating: float | None = None

    isOpenNow: bool | None = None

    distanceMeters: float

    estimatedEtaMinutes: int | None = None



class EmergencyRequest(
    BaseModel
):

    message: str

    latitude: float

    longitude: float
    nearby_places: List[NearbyPlace] = Field(
        default_factory=list
    )

    country: str = "India"

    nearby_services: NearbyServices = (
        NearbyServices()
    )

    nearby_places: list[NearbyPlace] = Field(
        default_factory=list
    )

    source: str = "mobile_app"

    offline_mode: bool = False