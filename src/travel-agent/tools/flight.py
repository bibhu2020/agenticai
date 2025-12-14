from agents import function_tool, RunContextWrapper
from contexts import UserContext
import json



@function_tool
async def search_flights(wrapper: RunContextWrapper[UserContext], origin: str, destination: str, date: str) -> str:
    """Search for flights between two cities on a specific date, taking user preferences into account."""
    # Mock Data identifying as "Real" search results for the agent
    flight_options = [
        {
            "airline": "SkyWays",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "price": 350.00,
            "direct_flight": True,
            "recommendation_reason": "Best morning value"
        },
        {
            "airline": "OceanAir",
            "departure_time": "12:45",
            "arrival_time": "15:15",
            "price": 275.50,
            "direct_flight": True,
            "recommendation_reason": "Cheapest direct flight"
        },
        {
            "airline": "MountainJet",
            "departure_time": "16:30",
            "arrival_time": "21:45",
            "price": 225.75,
            "direct_flight": False,
            "recommendation_reason": "Budget option"
        },
        {
            "airline": "Delta",
            "departure_time": "09:15",
            "arrival_time": "13:00",
            "price": 420.00,
            "direct_flight": True,
            "recommendation_reason": "Premium experience"
        },
        {
            "airline": "United",
            "departure_time": "18:00",
            "arrival_time": "20:30",
            "price": 310.00,
            "direct_flight": True,
            "recommendation_reason": "Evening departure"
        }
    ]
    
    # Simple filtering based on context if available
    if wrapper and wrapper.context and wrapper.context.preferred_airlines:
        prefs = wrapper.context.preferred_airlines
        # Sort: airlines in prefs come first
        flight_options.sort(key=lambda x: x["airline"] not in prefs)

    return json.dumps(flight_options)