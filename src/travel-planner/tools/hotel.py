from agents import function_tool, RunContextWrapper
from contexts import UserContext
from typing import List, Optional
import json



@function_tool
async def search_hotels(wrapper: RunContextWrapper[UserContext], city: str, check_in: str, check_out: str, max_price: Optional[float] = None) -> str:
    """Search for hotels in a city for specific dates within a price range, taking user preferences into account."""
    # Mock Data
    hotel_options = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
            "recommendation_reason": "Central location"
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside District",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"],
            "recommendation_reason": "Scenic views"
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"],
            "recommendation_reason": "Top rated luxury"
        },
        {
            "name": "Grand Plaza",
            "location": "Business District",
            "price_per_night": 220.00,
            "amenities": ["WiFi", "Gym", "Business Center", "Lounge"],
            "recommendation_reason": "Business amenities"
        },
        {
            "name": "Cozy Boutique Hotel",
            "location": "Arts District",
            "price_per_night": 180.00,
            "amenities": ["WiFi", "Rooftop Bar", "Art Gallery"],
            "recommendation_reason": "Unique atmosphere"
        }
    ]
    
    # Simple filtering
    if max_price is not None:
        hotel_options = [h for h in hotel_options if h["price_per_night"] <= max_price]
    
    # Preference sorting
    if wrapper and wrapper.context and wrapper.context.hotel_amenities:
        prefs = wrapper.context.hotel_amenities
        # Sort by overlap size
        hotel_options.sort(key=lambda x: len(set(x["amenities"]) & set(prefs)), reverse=True)

    return json.dumps(hotel_options)