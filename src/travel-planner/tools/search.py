from agents import function_tool, RunContextWrapper
from contexts import UserContext



@function_tool
def get_weather_forecast(wrapper: RunContextWrapper[UserContext], city: str, date: str) -> str:
    """Get the weather forecast for a city on a specific date."""
    # Mock Weather Data
    return f"The weather in {city} is expected to be clear and sunny with highs of 75°F (24°C) and lows of 60°F (15°C). Perfect for outdoor activities!"