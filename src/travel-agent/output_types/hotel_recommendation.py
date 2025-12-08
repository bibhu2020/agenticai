from typing import List, Optional
from pydantic import BaseModel, Field

# --- Models for structured outputs ---

class HotelRecommendation(BaseModel):
    name: str
    location: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str
