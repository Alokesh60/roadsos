from typing import List, Optional

from pydantic import (
    BaseModel
)


# =====================================
# EMERGENCY CONTACT
# =====================================

class EmergencyContact(
    BaseModel
):

    name: str

    phone: str


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

    # =============================
    # ANDROID CONTACTS
    # =============================

    contacts: List[
        EmergencyContact
    ] = []

    # =============================
    # SOURCE TRACKING
    # =============================

    source: str = "mobile_app"

    # =============================
    # OFFLINE MODE FLAG
    # =============================

    offline_mode: bool = False


# =====================================
# EMERGENCY RESPONSE
# =====================================

class EmergencyResponse(
    BaseModel
):

    classification_status: str

    classification_reason: str

    proceed: bool

    detected_type: str

    priority: str

    confidence: float

    recommended_service: dict

    guidance: str

    # =============================
    # SOURCE INFO
    # =============================

    source: Optional[str] = None

    # =============================
    # OFFLINE SUPPORT
    # =============================

    offline_support: bool = True

    # =============================
    # DISASTER ALERTS
    # =============================

    disaster_alerts: list = []