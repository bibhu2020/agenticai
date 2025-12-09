"""Web search agent module for internet queries."""
import os
from agents import Agent
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.tools.weather_tools import get_weather_forecast, search_weather_fallback_ddgs, search_weather_fallback_bs
from mcp.tools.time_tools import current_datetime
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

################################
# Learning: gemini models struggles to construct the output_type when it's a Pydantic model.
# So we use list[dict] as output_type instead of list[searchResult].
# Then in the calling code, we can convert dicts back to searchResult models if needed.
################################

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-flash-latest", openai_client=gemini_client) 

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
groq_model = OpenAIChatCompletionsModel(model="groq/compound", openai_client=groq_client)

weather_agent = Agent(
    name="WeatherAgent",
    model=gemini_model, #"gpt-4o-mini",
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
