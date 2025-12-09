from typing import List, Optional
from pydantic import BaseModel, Field

# --- Models for structured outputs ---

from .flight_recommendation import FlightRecommendation
from .hotel_recommendation import HotelRecommendation

class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    flight_options: List[FlightRecommendation] = Field(default_factory=list, description="List of recommended flight options")
    hotel_options: List[HotelRecommendation] = Field(default_factory=list, description="List of recommended hotel options")
    weather_remark: str = Field(description="Summary of weather forecast for the trip")
    activities: List[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")
