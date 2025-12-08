from agents import function_tool, RunContextWrapper
from contexts import UserContext
from serpapi import GoogleSearch
import os
import json

SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Make sure you export your key

@function_tool
def get_weather_forecast(wrapper: RunContextWrapper[UserContext], city: str, date: str) -> str:
    """
    Get the weather forecast for a city on a specific date using SerpAPI Google Search.
    Updates the agent context with a lightweight summary.
    """

    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY environment variable not set")

    query = f"Weather forecast for {city} on {date}"
    
    search = GoogleSearch({
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_KEY,
        "gl": "us",
        "hl": "en"
    })

    result = search.get_dict()

    # Attempt to parse structured weather snippet
    weather_info = ""
    try:
        # Inline weather snippet (common field in Google SERP)
        if "weather_results" in result:
            weather_info = result["weather_results"].get("forecast_summary", "")
        elif "organic_results" in result:
            # Fallback: take snippet from first organic result
            for r in result["organic_results"]:
                snippet = r.get("snippet", "")
                if snippet:
                    weather_info = snippet
                    break
    except Exception:
        weather_info = ""

    if not weather_info:
        weather_info = f"Weather forecast for {city} on {date} is not available."

    # Persist a lightweight summary into the shared context
    try:
        if wrapper.context:
            wrapper.context.latest_weather_forecast = {
                "city": city,
                "date": date,
                "forecast": weather_info
            }
    except Exception:
        # Never fail the tool if context persistence fails
        pass

    return weather_info