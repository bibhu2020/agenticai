from typing import List, Optional
from pydantic import BaseModel, Field

# --- Models for structured outputs ---

class FlightRecommendation(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    direct_flight: bool
    recommendation_reason: str
