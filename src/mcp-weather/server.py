
import sys
import os
import requests
from typing import List, Dict, Any, Optional

# Add src to pythonpath so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from mcp.server.fastmcp import FastMCP
from core.mcp_telemetry import log_usage, log_trace, log_metric
import uuid
import time
from datetime import datetime

# Initialize FastMCP Server
mcp = FastMCP("Weather MCP", host="0.0.0.0")

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
GPLACES_API_KEY = os.environ.get("GPLACES_API_KEY")

def format_temp(temp: float, unit: str = "metric") -> str:
    if unit == "metric":
        return f"{temp}°C"
    return f"{temp}°F"

@mcp.tool()
def get_current_weather(location: str, units: str = "metric") -> Dict[str, Any]:
    """
    Get current weather for a specific city or location.
    Units can be 'metric' (Celsius) or 'imperial' (Fahrenheit).
    """
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    
    log_usage("mcp-weather", "get_current_weather")
    if not OPENWEATHER_API_KEY:
        log_trace("mcp-weather", trace_id, span_id, "get_current_weather", 0, "error")
        return {"error": "OPENWEATHER_API_KEY not set"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units={units}"
    try:
        response = requests.get(url, timeout=10)
        duration = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            log_trace("mcp-weather", trace_id, span_id, "get_current_weather", duration, "error")
            return {"error": f"Failed to fetch weather: {response.text}"}
        
        data = response.json()
        temp = data["main"]["temp"]
        
        # Log Metrics
        log_metric("mcp-weather", "weather_temperature", temp, {"location": location, "unit": units})
        log_metric("mcp-weather", "api_latency", duration, {"endpoint": "weather"})
        
        # Log Trace
        log_trace("mcp-weather", trace_id, span_id, "get_current_weather", duration, "ok")
        
        return {
            "location": data.get("name"),
            "condition": data["weather"][0]["description"],
            "temperature": format_temp(temp, units),
            "feels_like": format_temp(data["main"]["feels_like"], units),
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "timestamp": data.get("dt")
        }
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_trace("mcp-weather", trace_id, span_id, "get_current_weather", duration, "error")
        return {"error": str(e)}

@mcp.tool()
def get_forecast(location: str, units: str = "metric") -> List[Dict[str, Any]]:
    """
    Get 5-day weather forecast (3-hour intervals) for a location.
    """
    log_usage("mcp-weather", "get_forecast")
    if not OPENWEATHER_API_KEY:
        return [{"error": "OPENWEATHER_API_KEY not set"}]
    
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units={units}"
    response = requests.get(url)
    if response.status_code != 200:
        return [{"error": f"Failed to fetch forecast: {response.text}"}]
    
    data = response.json()
    forecasts = []
    for item in data.get("list", [])[:8]:  # Return first 24 hours (8 * 3h)
        forecasts.append({
            "time": item.get("dt_txt"),
            "condition": item["weather"][0]["description"],
            "temp": format_temp(item["main"]["temp"], units),
            "rain_prob": f"{int(item.get('pop', 0) * 100)}%"
        })
    return forecasts

@mcp.tool()
def get_air_quality(location: str) -> Dict[str, Any]:
    """
    Get current Air Quality Index (AQI) for a location.
    Requires first resolving the location to coordinates.
    """
    log_usage("mcp-weather", "get_air_quality")
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set"}
    
    # 1. Geocode location
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
    geo_res = requests.get(geo_url)
    if geo_res.status_code != 200 or not geo_res.json():
        return {"error": "Could not locate the specified area"}
    
    lat = geo_res.json()[0]["lat"]
    lon = geo_res.json()[0]["lon"]
    
    # 2. Get AQI
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    aqi_res = requests.get(aqi_url)
    if aqi_res.status_code != 200:
        return {"error": "Failed to fetch air quality data"}
    
    aqi_data = aqi_res.json()["list"][0]
    aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    
    return {
        "aqi": aqi_data["main"]["aqi"],
        "quality": aqi_levels.get(aqi_data["main"]["aqi"], "Unknown"),
        "components": aqi_data["components"] # Includes CO, NO, NO2, O3, etc.
    }

@mcp.tool()
def search_places(query: str) -> List[Dict[str, Any]]:
    """
    Search for places, cities, or addresses using Google Places.
    Useful for getting correct place names or location IDs.
    """
    log_usage("mcp-weather", "search_places")
    if not GPLACES_API_KEY:
        return [{"error": "GPLACES_API_KEY not set"}]
    
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GPLACES_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return [{"error": f"Places search failed: {response.text}"}]
    
    results = []
    for place in response.json().get("results", [])[:5]:
        results.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "place_id": place.get("place_id"),
            "rating": place.get("rating")
        })
    return results

@mcp.tool()
def get_place_details(place_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a place using its Google Place ID.
    Includes coordinates, phone number, and website.
    """
    log_usage("mcp-weather", "get_place_details")
    if not GPLACES_API_KEY:
        return {"error": "GPLACES_API_KEY not set"}
    
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={GPLACES_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to get place details"}
    
    details = response.json().get("result", {})
    return {
        "name": details.get("name"),
        "coordinates": details.get("geometry", {}).get("location"),
        "formatted_address": details.get("formatted_address"),
        "phone": details.get("formatted_phone_number"),
        "website": details.get("website")
    }

if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "sse":
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)
    else:
        mcp.run()
