from agents import function_tool, RunContextWrapper
from contexts import UserContext
from serpapi import GoogleSearch
import os
import json

SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Make sure you export your key

@function_tool
def get_weather_forecast(wrapper: RunContextWrapper[UserContext],city: str, date: str) -> str:
    """Get the weather forecast for a city on a specific date."""
    # In a real implementation, this would call a weather API
    weather_data = {
        "New York": {"sunny": 0.3, "rainy": 0.4, "cloudy": 0.3},
        "Los Angeles": {"sunny": 0.8, "rainy": 0.1, "cloudy": 0.1},
        "Chicago": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Miami": {"sunny": 0.7, "rainy": 0.2, "cloudy": 0.1},
        "London": {"sunny": 0.2, "rainy": 0.5, "cloudy": 0.3},
        "Paris": {"sunny": 0.4, "rainy": 0.3, "cloudy": 0.3},
        "Tokyo": {"sunny": 0.5, "rainy": 0.3, "cloudy": 0.2},
    }
    
    if city in weather_data:
        conditions = weather_data[city]
        # Simple simulation based on probabilities
        highest_prob = max(conditions, key=conditions.get)
        temp_range = {
            "New York": "15-25°C",
            "Los Angeles": "20-30°C",
            "Chicago": "10-20°C",
            "Miami": "25-35°C",
            "London": "10-18°C",
            "Paris": "12-22°C",
            "Tokyo": "15-25°C",
        }
        return f"The weather in {city} on {date} is forecasted to be {highest_prob} with temperatures around {temp_range.get(city, '15-25°C')}."
    else:
        return f"Weather forecast for {city} is not available."

# @function_tool
# def get_weather_forecast(wrapper: RunContextWrapper[UserContext], city: str, date: str) -> str:
#     """
#     Get the weather forecast for a city on a specific date using SerpAPI Google Search.
#     Updates the agent context with a lightweight summary.
#     """

#     if not SERPAPI_KEY:
#         raise RuntimeError("SERPAPI_KEY environment variable not set")

#     query = f"Weather forecast for {city} on {date}"
    
#     search = GoogleSearch({
#         "q": query,
#         "engine": "google",
#         "api_key": SERPAPI_KEY,
#         "gl": "us",
#         "hl": "en"
#     })

#     result = search.get_dict()

#     # Attempt to parse structured weather snippet
#     weather_info = ""
#     try:
#         # Inline weather snippet (common field in Google SERP)
#         if "weather_results" in result:
#             weather_info = result["weather_results"].get("forecast_summary", "")
#         elif "organic_results" in result:
#             # Fallback: take snippet from first organic result
#             for r in result["organic_results"]:
#                 snippet = r.get("snippet", "")
#                 if snippet:
#                     weather_info = snippet
#                     break
#     except Exception:
#         weather_info = ""

#     if not weather_info:
#         weather_info = f"Weather forecast for {city} on {date} is not available."

#     # Persist a lightweight summary into the shared context
#     try:
#         if wrapper.context:
#             wrapper.context.latest_weather_forecast = {
#                 "city": city,
#                 "date": date,
#                 "forecast": weather_info
#             }
#     except Exception:
#         # Never fail the tool if context persistence fails
#         pass

#     return weather_info