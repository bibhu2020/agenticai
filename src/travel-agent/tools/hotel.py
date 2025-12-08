from agents import function_tool, RunContextWrapper
from contexts import UserContext
from typing import List, Optional
import json

@function_tool
async def search_hotels(wrapper: RunContextWrapper[UserContext], city: str, check_in: str, check_out: str, max_price: Optional[float] = None) -> str:
    """Search for hotels in a city for specific dates within a price range, taking user preferences into account."""
    # In a real implementation, this would call a hotel search API
    hotel_options = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside District",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"]
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"]
        }
    ]
    
    # Filter by max price if provided
    if max_price is not None:
        filtered_hotels = [hotel for hotel in hotel_options if hotel["price_per_night"] <= max_price]
    else:
        filtered_hotels = hotel_options
    
    # Apply user preferences if available
    if wrapper and wrapper.context:
        preferred_amenities = wrapper.context.hotel_amenities
        budget_level = wrapper.context.budget_level
        
        # Sort hotels by preference match
        if preferred_amenities:
            # Calculate a score based on how many preferred amenities each hotel has
            for hotel in filtered_hotels:
                matching_amenities = [a for a in hotel["amenities"] if a in preferred_amenities]
                hotel["matching_amenities"] = matching_amenities
                hotel["preference_score"] = len(matching_amenities)
            
            # Sort by preference score (higher scores first)
            filtered_hotels.sort(key=lambda x: x["preference_score"], reverse=True)
        
        # Apply budget level preferences if available
        if budget_level:
            if budget_level == "budget":
                filtered_hotels.sort(key=lambda x: x["price_per_night"])
            elif budget_level == "luxury":
                filtered_hotels.sort(key=lambda x: x["price_per_night"], reverse=True)
            # mid-range is already handled by the max_price filter
        
    # Persist a lightweight summary into the shared context so other agents/orchestrator can use it
    try:
        if wrapper and wrapper.context and filtered_hotels:
            top = filtered_hotels[0]
            wrapper.context.latest_hotel_recommendation = {
                "name": top.get("name"),
                "location": top.get("location"),
                "price_per_night": top.get("price_per_night"),
                "amenities": top.get("amenities", []),
            }
            wrapper.context.hotel_options = filtered_hotels
    except Exception:
        # Don't let context persistence break the tool
        pass

    return json.dumps(filtered_hotels)