from pydantic import BaseModel
from typing import List, Optional

from app.schemas.service_schema import EmergencyServiceSchema


class NearbyResponseSchema(BaseModel):

    success: bool

    count: int

    radius_km: float

    filter_type: Optional[str]

    data: List[EmergencyServiceSchema]