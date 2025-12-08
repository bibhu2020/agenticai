import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from logger.decorators import log_entry
from utils.place_info_search import GooglePlaceSearchTool, TavilyPlaceSearchTool

class PlaceSearchTool:
    """
    A wrapper class that provides LangChain-compatible tools to search for
    attractions, restaurants, activities, and transportation options in a given place.

    It uses Google Places API primarily and falls back to Tavily search if needed.
    """

    def __init__(self):
        """
        Initialize the PlaceSearchTool with required API keys and setup tool functions.
        """
        load_dotenv()
        self.google_api_key = os.environ.get("GPLACES_API_KEY")
        self.google_places_search = GooglePlaceSearchTool(self.google_api_key)
        self.tavily_search = TavilyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """
        Setup and register all LangChain-compatible place search tools.

        Returns:
            List: A list of tool functions that can be invoked via LangChain agents.
        """

        @tool
        @log_entry
        def search_attractions(place: str) -> str:
            """
            Search for popular attractions in a given place.

            Args:
                place (str): The name of the place (e.g., "New York").

            Returns:
                str: A list of suggested attractions retrieved from Google or Tavily.
            """
            print('Entered into search_attractions().')
            try:
                attraction_result = self.google_places_search.google_search_attractions(place)
                if attraction_result:
                    return f"Following are the attractions of {place} as suggested by Google: {attraction_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_attractions(place)
                return f"Google cannot find the details due to {e}.\nFollowing are the attractions of {place}: {tavily_result}"

        @tool
        @log_entry
        def search_restaurants(place: str) -> str:
            """
            Search for restaurants in a given place.

            Args:
                place (str): The name of the place (e.g., "San Francisco").

            Returns:
                str: A list of suggested restaurants retrieved from Google or Tavily.
            """
            print('Entered into search_restaurants().')
            try:
                restaurants_result = self.google_places_search.google_search_restaurants(place)
                if restaurants_result:
                    return f"Following are the restaurants of {place} as suggested by Google: {restaurants_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_restaurants(place)
                return f"Google cannot find the details due to {e}.\nFollowing are the restaurants of {place}: {tavily_result}"

        @tool
        @log_entry
        def search_activities(place: str) -> str:
            """
            Search for activities available in a given place.

            Args:
                place (str): The name of the place (e.g., "Chicago").

            Returns:
                str: A list of activities retrieved from Google or Tavily.
            """
            print('Entered into search_activities().')
            try:
                activities_result = self.google_places_search.google_search_activity(place)
                if activities_result:
                    return f"Following are the activities in and around {place} as suggested by Google: {activities_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_activity(place)
                return f"Google cannot find the details due to {e}.\nFollowing are the activities of {place}: {tavily_result}"

        @tool
        @log_entry
        def search_transportation(place: str) -> str:
            """
            Search for transportation options available in a given place.

            Args:
                place (str): The name of the place (e.g., "Los Angeles").

            Returns:
                str: A list of transportation modes retrieved from Google or Tavily.
            """
            print('Entered into search_transportation().')
            try:
                transport_result = self.google_places_search.google_search_transportation(place)
                if transport_result:
                    return f"Following are the modes of transportation available in {place} as suggested by Google: {transport_result}"
            except Exception as e:
                tavily_result = self.tavily_search.tavily_search_transportation(place)
                return f"Google cannot find the details due to {e}.\nFollowing are the modes of transportation available in {place}: {tavily_result}"

        return [search_attractions, search_restaurants, search_activities, search_transportation]
