from typing import List

from pydantic import (
    BaseModel,
    Field
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

    # =================================
    # USER MESSAGE
    # =================================

    message: str

    # =================================
    # LOCATION
    # =================================

    latitude: float

    longitude: float

    country: str = "India"

    # =================================
    # EMERGENCY CONTACTS
    # =================================

    contacts: List[
        EmergencyContact
    ] = Field(
        default_factory=list
    )

    # =================================
    # SOURCE INFO
    # =================================

    source: str = "mobile_app"

    # =================================
    # OFFLINE FLAG
    # =================================

    offline_mode: bool = False


# =====================================
# EMERGENCY RESPONSE
# =====================================

class EmergencyResponse(
    BaseModel
):

    success: bool

    sos_triggered: bool

    message: str

    guidance: str

    source: str

    suggested_actions: list = Field(
        default_factory=list
    )

    notifications: list = Field(
        default_factory=list
    )