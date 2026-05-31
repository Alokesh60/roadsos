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

    source: str = "mobile_app"

    offline_mode: bool = False