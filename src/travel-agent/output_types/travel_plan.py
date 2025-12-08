from typing import List, Optional
from pydantic import BaseModel, Field

# --- Models for structured outputs ---

class TravelPlan(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str] = Field(description="List of recommended activities")
    notes: str = Field(description="Additional notes or recommendations")
