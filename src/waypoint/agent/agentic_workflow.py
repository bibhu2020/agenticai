"""Trip Planner Agent — Phidata Agent with weather, places, expense and currency tools."""
import os
from phi.agent import Agent
from llm import get_llm

from utils.weather_info import WeatherForecastTool
from utils.place_info_search import GooglePlaceSearchTool, TavilyPlaceSearchTool
from utils.expense_calculator import Calculator
from utils.currency_converter import CurrencyConverter

_INSTRUCTIONS = [
    "You are an intelligent AI Travel Agent and Expense Planner.",
    "Always use the provided tools to gather real-time data before generating the plan.",
    "If a tool fails, fall back to your knowledge only as a last resort.",
    "Your response must be in clean Markdown and include:",
    "- 📅 Day-by-day itinerary",
    "- 🏨 Recommended hotels with approximate cost per night",
    "- 🗺️ Attractions with descriptions",
    "- 🍽️ Recommended restaurants and pricing",
    "- 🛶 Activities with timing and pricing",
    "- 🚗 Transportation options",
    "- 🌤️ Weather summary",
    "- 💰 Per-day and total cost breakdown",
    "If the question is unrelated to travel, politely decline.",
]


# ── Tool functions ─────────────────────────────────────────────────────────────

def get_current_weather(city: str) -> str:
    """Get the current weather for a city."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
    svc = WeatherForecastTool(api_key)
    data = svc.get_current_weather(city)
    if data:
        temp = data.get("main", {}).get("temp", "N/A")
        desc = data.get("weather", [{}])[0].get("description", "N/A")
        return f"Current weather in {city}: {temp}°C, {desc}"
    return f"Could not fetch weather for {city}."


def get_weather_forecast(city: str) -> str:
    """Get the multi-day weather forecast for a city."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
    svc = WeatherForecastTool(api_key)
    data = svc.get_forecast_weather(city)
    if data and "list" in data:
        lines = []
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            lines.append(f"{date}: {temp}°C, {desc}")
        return f"Weather forecast for {city}:\n" + "\n".join(lines)
    return f"Could not fetch forecast for {city}."


def search_attractions(place: str) -> str:
    """Search for popular tourist attractions in a place."""
    try:
        google_key = os.environ.get("GPLACES_API_KEY", "")
        result = GooglePlaceSearchTool(google_key).google_search_attractions(place)
        return f"Attractions in {place}: {result}"
    except Exception as e:
        result = TavilyPlaceSearchTool().tavily_search_attractions(place)
        return f"Attractions in {place}: {result}"


def search_restaurants(place: str) -> str:
    """Search for restaurants in a place."""
    try:
        google_key = os.environ.get("GPLACES_API_KEY", "")
        result = GooglePlaceSearchTool(google_key).google_search_restaurants(place)
        return f"Restaurants in {place}: {result}"
    except Exception as e:
        result = TavilyPlaceSearchTool().tavily_search_restaurants(place)
        return f"Restaurants in {place}: {result}"


def search_activities(place: str) -> str:
    """Search for activities available in a place."""
    try:
        google_key = os.environ.get("GPLACES_API_KEY", "")
        result = GooglePlaceSearchTool(google_key).google_search_activity(place)
        return f"Activities in {place}: {result}"
    except Exception as e:
        result = TavilyPlaceSearchTool().tavily_search_activity(place)
        return f"Activities in {place}: {result}"


def search_transportation(place: str) -> str:
    """Search for transportation options in a place."""
    try:
        google_key = os.environ.get("GPLACES_API_KEY", "")
        result = GooglePlaceSearchTool(google_key).google_search_transportation(place)
        return f"Transportation in {place}: {result}"
    except Exception as e:
        result = TavilyPlaceSearchTool().tavily_search_transportation(place)
        return f"Transportation in {place}: {result}"


def calculate_total_cost(*amounts: float) -> float:
    """Calculate the total cost from a list of individual costs."""
    return Calculator.calculate_total(*amounts)


def calculate_daily_budget(total: float, days: int) -> float:
    """Calculate the daily budget given a total cost and number of days."""
    return Calculator.calculate_daily_budget(total, days)


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another using live exchange rates."""
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")
    try:
        converter = CurrencyConverter(api_key)
        converted = converter.convert(amount, from_currency.upper(), to_currency.upper())
        return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
    except Exception as e:
        return f"Currency conversion failed: {e}"


# ── Agent factory ──────────────────────────────────────────────────────────────

def create_trip_agent(model_provider: str = "openai") -> Agent:
    return Agent(
        name="Waypoint",
        model=get_llm(provider=model_provider, model="gpt-4o-mini"),
        tools=[
            get_current_weather,
            get_weather_forecast,
            search_attractions,
            search_restaurants,
            search_activities,
            search_transportation,
            calculate_total_cost,
            calculate_daily_budget,
            convert_currency,
        ],
        instructions=_INSTRUCTIONS,
        markdown=True,
        show_tool_calls=True,
    )
