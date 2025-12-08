import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from logger.decorators import log_entry
from utils.weather_info import WeatherForecastTool

class WeatherInfoTool:
    """
    A wrapper class for retrieving weather information using the OpenWeatherMap API.

    This class provides LangChain-compatible tools to get current weather and weather forecasts
    for a given city.
    """

    def __init__(self):
        """
        Initialize the WeatherInfoTool with API credentials and set up weather-related tools.
        """
        load_dotenv()
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        self.weather_service = WeatherForecastTool(self.api_key)
        self.weather_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """
        Define and register weather-related LangChain tool functions.

        Returns:
            List: A list of LangChain-compatible weather tool functions.
        """

        @tool
        @log_entry
        def get_current_weather(city: str) -> str:
            """
            Get the current weather information for a specified city.

            Args:
                city (str): The name of the city to get current weather data for.

            Returns:
                str: A string describing the current temperature and weather condition.
            """
            print('Entered into get_current_weather().')
            weather_data = self.weather_service.get_current_weather(city)
            if weather_data:
                temp = weather_data.get('main', {}).get('temp', 'N/A')
                desc = weather_data.get('weather', [{}])[0].get('description', 'N/A')
                return f"Current weather in {city}: {temp}°C, {desc}"
            return f"Could not fetch weather for {city}"

        @tool
        @log_entry
        def get_weather_forecast(city: str) -> str:
            """
            Get the multi-day weather forecast for a specified city.

            Args:
                city (str): The name of the city to get the weather forecast for.

            Returns:
                str: A string listing daily temperatures and descriptions for upcoming forecasts.
            """
            print('Entered into get_weather_forecast().')
            forecast_data = self.weather_service.get_forecast_weather(city)
            if forecast_data and 'list' in forecast_data:
                forecast_summary = []
                for item in forecast_data['list']:
                    date = item['dt_txt'].split(' ')[0]
                    temp = item['main']['temp']
                    desc = item['weather'][0]['description']
                    forecast_summary.append(f"{date}: {temp}°C, {desc}")
                return f"Weather forecast for {city}:\n" + "\n".join(forecast_summary)
            return f"Could not fetch forecast for {city}"

        return [get_current_weather, get_weather_forecast]
