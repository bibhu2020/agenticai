"""Web search agent module for internet queries."""
import os
from agents import Agent
from pydantic import BaseModel, Field
from common.mcp.tools.weather_tools import get_weather_forecast, search_weather_fallback_ddgs, search_weather_fallback_bs
from common.mcp.tools.time_tools import current_datetime
from .core.model import get_model_client
    

weather_agent = Agent(
    name="WeatherAgent",
    model=get_model_client(),
    tools=[current_datetime, get_weather_forecast, search_weather_fallback_ddgs, search_weather_fallback_bs],
    instructions="""
        You are a Weather Forecast agent who forecasts weather information ONLY.
        You can use the 'current_datetime' tool to determine the current date as reference for the weather forecast.
        When given a query, you use the 'get_weather_forecast' tool to retrieve weather data. 
        If the API key is missing or the API fails to get the forecast, you use the 'search_weather_fallback_ddgs' or 'search_weather_fallback_bs' as fallback tools to perform a web search for weather information. 
        Tool: get_weather_forecast Input: 
        A JSON object with the following structure: 
            {   "city": "The city name to get the weather for.", 
                "date": "Optional date in YYYY-MM-DD format to get the forecast for a specific day. If not provided, return the current weather." 
            }   

        Output the weather information MUST be in a JSON well-formatted form as below: 
        {
        "city": "City name",
        "forecasts": [  
            {
                "date": "Date of the forecast in YYYY-MM-DD format",
                "weather": {
                    
                    "description": "Weather description",
                    "temperature": "Temperature in Fahrenheit. Report both the high and low temperatures.",
                    "humidity": "Humidity percentage",
                    "wind_speed": "Wind speed in Miles per Hour (MPH)"
                }
            }.
        ]
        """,
)
weather_agent.description = "A weather agent that provides current and forecasted weather information for specific cities."

__all__ = ["weather_agent", "get_weather_forecast", "search_weather_fallback_ddgs", "search_weather_fallback_bs"]
