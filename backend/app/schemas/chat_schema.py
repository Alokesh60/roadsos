from typing import Optional, List
from pydantic import BaseModel, Field

class HistoryMessage(BaseModel):
    role: str
    content: str

class ChatContext(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None
    nearest_highway: Optional[str] = None
    nearest_hospital: Optional[str] = None
    nearest_hospital_phone: Optional[str] = None
    nearest_police_phone: Optional[str] = None
    nearest_ambulance_phone: Optional[str] = None
    nearest_towing_phone: Optional[str] = None
    is_sos_active: bool = False
    nearby_places: List[dict] = Field(default_factory=list)

class ChatRequest(BaseModel):
    session_id: str
    user_message: str
    context: ChatContext = Field(default_factory=ChatContext)
    history: List[HistoryMessage] = Field(default_factory=list)
