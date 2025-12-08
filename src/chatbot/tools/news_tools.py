import os
import requests
from dotenv import load_dotenv
from agents import function_tool
from core.logger import log_call
import datetime

# Load environment variables once
load_dotenv()


# ============================================================
# 🔹 NEWS TOOLSET (NewsAPI.org)
# ============================================================
class NewsTools:
    """
    NewsTools provides function tools to fetch recent news headlines or
    topic-specific articles from NewsAPI.org. Always returns recent data.
    """

    @staticmethod
    @function_tool
    @log_call
    def top_headlines(country: str = "us", num_results: int = 5) -> str:
        """
        Fetch the latest top headlines for a country.

        Parameters:
        -----------
        country : str, optional (default="us")
            Two-letter country code.
        num_results : int, optional (default=5)
            Number of articles to fetch.

        Returns:
        --------
        str
            Formatted headlines with title, source, and URL.
        """
        return NewsTools._fetch_news(query="", country=country, num_results=num_results)

    @staticmethod
    @function_tool
    @log_call
    def search_news(query: str, num_results: int = 5) -> str:
        """
        Search for recent news articles about a specific topic.

        Parameters:
        -----------
        query : str
            Keyword or topic to search (e.g., "Tesla earnings").
        num_results : int, optional (default=5)
            Number of articles to fetch.

        Returns:
        --------
        str
            Formatted news articles with title, source, and URL.
        """
        return NewsTools._fetch_news(query=query, country="", num_results=num_results)

    @staticmethod
    @log_call
    def _fetch_news(query: str, country: str, num_results: int) -> str:
        """
        Internal helper to fetch news from NewsAPI.org.

        Ensures always recent news (last 7 days).

        Parameters:
        -----------
        query : str
            Search query (leave empty for top headlines).
        country : str
            Two-letter country code (ignored if query provided).
        num_results : int
            Max articles to return.

        Returns:
        --------
        str
            Formatted articles or error message.
        """
        try:
            api_key = os.getenv("NEWS_API_KEY")
            if not api_key:
                return "Missing NEWS_API_KEY in environment variables."

            today = datetime.datetime.utcnow()
            from_date = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

            if query:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "pageSize": num_results,
                    "apiKey": api_key,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "from": from_date
                }
            else:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    "country": country or "us",
                    "pageSize": num_results,
                    "apiKey": api_key
                }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("articles"):
                return f"No news found for '{query or country}'."

            formatted = [
                f"📰 {a.get('title')}\n"
                f"   Source: {a.get('source', {}).get('name')}\n"
                f"   URL: {a.get('url')}\n"
                for a in data["articles"][:num_results]
            ]
            return "\n".join(formatted)

        except requests.exceptions.RequestException as e:
            return f"Network error while calling News API: {e}"
        except Exception as e:
            return f"Unexpected error fetching news: {e}"