import os
import requests
from dotenv import load_dotenv
from agents import function_tool
from typing import Optional
import datetime

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

# ============================================================
# 🔹 NEWS TOOLSET (NewsAPI.org)
# ============================================================

def _search_news(query: str, num_results: int = 5, days_back: int = 7) -> str:
   
    print(f"[DEBUG] search_news called with query='{query}', num_results={num_results}, days_back={days_back}")
    
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "Error: NEWS_API_KEY missing in environment variables."

        # Calculate date range
        today = datetime.datetime.utcnow()
        from_date = (today - datetime.timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "pageSize": num_results,
            "apiKey": api_key,
            "sortBy": "publishedAt",
            "language": "en",
            "from": from_date
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("articles"):
            return f"No news found for query: '{query}'"

        formatted = []
        for article in data["articles"][:num_results]:
            formatted.append(
                f"📰 {article.get('title')}\n"
                f"   Source: {article.get('source', {}).get('name')}\n"
                f"   Published: {article.get('publishedAt', 'N/A')}\n"
                f"   URL: {article.get('url')}\n"
            )
        
        return f"News Search Results for '{query}' (last {days_back} days):\n\n" + "\n".join(formatted)

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error: {e}")
        return f"Network error while calling News API: {e}"
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return f"Unexpected error fetching news: {e}"

@function_tool
def get_top_headlines(country: str = "us", num_results: int = 5) -> str:
    """
    Fetch the latest top headlines for a country using NewsAPI.org.

    Parameters:
    -----------
    country : str, optional (default="us")
        Two-letter country code (e.g., "us", "gb", "in").
    num_results : int, optional (default=5)
        Number of articles to fetch.

    Returns:
    --------
    str
        Formatted headlines with title, source, published date, and URL.
        If API key is missing or no results found, returns an error message.
    """
    print(f"[DEBUG] get_top_headlines called for country={country}, num_results={num_results}")
    
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "Error: NEWS_API_KEY missing in environment variables."

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": num_results,
            "apiKey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("articles"):
            return f"No top headlines found for country: {country}"

        formatted = []
        for article in data["articles"][:num_results]:
            formatted.append(
                f"📰 {article.get('title')}\n"
                f"   Source: {article.get('source', {}).get('name')}\n"
                f"   Published: {article.get('publishedAt', 'N/A')}\n"
                f"   URL: {article.get('url')}\n"
            )
        
        return f"Top Headlines ({country.upper()}):\n\n" + "\n".join(formatted)

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error: {e}")
        return f"Network error while calling News API: {e}"
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return f"Unexpected error fetching news: {e}"


@function_tool
def search_news(query: str, num_results: int = 5, days_back: int = 7) -> str:
    """
    Search for recent news articles about a specific topic using NewsAPI.org.

    Parameters:
    -----------
    query : str
        Keyword or topic to search (e.g., "Tesla earnings", "AI healthcare").
    num_results : int, optional (default=5)
        Number of articles to fetch.
    days_back : int, optional (default=7)
        Number of days to look back for articles (1-30).

    Returns:
    --------
    str
        Formatted news articles with title, source, published date, and URL.
        If API key is missing or no results found, returns an error message.
    """
    return _search_news(query, num_results, days_back)


@function_tool
def get_news_by_category(category: str = "business", country: str = "us", num_results: int = 5) -> str:
    """
    Fetch top headlines by category using NewsAPI.org.

    Parameters:
    -----------
    category : str, optional (default="business")
        News category: "business", "entertainment", "general", "health", 
        "science", "sports", "technology".
    country : str, optional (default="us")
        Two-letter country code.
    num_results : int, optional (default=5)
        Number of articles to fetch.

    Returns:
    --------
    str
        Formatted headlines for the specified category.
    """
    print(f"[DEBUG] get_news_by_category called for category={category}, country={country}")
    
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "Error: NEWS_API_KEY missing in environment variables."

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": category,
            "country": country,
            "pageSize": num_results,
            "apiKey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("articles"):
            return f"No headlines found for category: {category}"

        formatted = []
        for article in data["articles"][:num_results]:
            formatted.append(
                f"📰 {article.get('title')}\n"
                f"   Source: {article.get('source', {}).get('name')}\n"
                f"   Published: {article.get('publishedAt', 'N/A')}\n"
                f"   URL: {article.get('url')}\n"
            )
        
        return f"Top {category.capitalize()} Headlines ({country.upper()}):\n\n" + "\n".join(formatted)

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error: {e}")
        return f"Network error while calling News API: {e}"
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return f"Unexpected error fetching news: {e}"