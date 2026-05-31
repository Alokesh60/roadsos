from typing import Optional
from pydantic import BaseModel


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

    source: str = "mobile_app"

    offline_mode: bool = False