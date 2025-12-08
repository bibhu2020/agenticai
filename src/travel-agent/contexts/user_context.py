from datetime import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class UserContext:  
    user_id: str
    source_destination: str = None
    target_destination: str = None
    preferred_airlines: List[str] = None
    hotel_amenities: List[str] = None
    budget_level: str = None
    session_start: datetime = None
    latest_flight_recommendation: dict = None
    flight_options: List[dict] = None
    latest_hotel_recommendation: dict = None
    hotel_options: List[dict] = None
    
    def __post_init__(self):
        if self.preferred_airlines is None:
            self.preferred_airlines = []
        if self.hotel_amenities is None:
            self.hotel_amenities = []
        if self.session_start is None:
            self.session_start = datetime.now()