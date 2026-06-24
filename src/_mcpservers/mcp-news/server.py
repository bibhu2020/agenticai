"""MCP News Server — top headlines, topic search, and category filtering via NewsAPI.org."""
import datetime
import logging
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] mcp-news: %(message)s",
)
log = logging.getLogger("mcp-news")

mcp = FastMCP("News MCP", host="0.0.0.0", port=8002)


@mcp.tool()
def current_datetime(format: str = "natural") -> str:
    """
    Return the current date and time.

    Args:
        format: 'natural' → 'Saturday, June 07, 2025 at 3:59 PM'
                'natural_short' → 'Jun 07, 2025 at 3:59 PM'
                Or any strftime format string (e.g. '%Y-%m-%d').
    """
    now = datetime.datetime.now()
    if format == "natural":
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    if format == "natural_short":
        return now.strftime("%b %d, %Y at %I:%M %p")
    return now.strftime(format)


def _call_newsapi(url: str, params: dict) -> tuple[list[dict], str | None]:
    """Returns (articles, error_message). error_message is None on success."""
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key:
        return [], "NEWS_API_KEY is not set — add it to your .env file"
    params["apiKey"] = api_key
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if response.status_code != 200:
            msg = data.get("message", response.text)
            return [], f"NewsAPI error {response.status_code}: {msg}"
        return data.get("articles", []), None
    except requests.exceptions.ConnectionError:
        log.error("NewsAPI connection failed: network unreachable")
        return [], "Could not reach NewsAPI — check your network connection"
    except Exception as exc:
        log.error("NewsAPI unexpected error: %s", exc)
        return [], f"Unexpected error: {exc}"


def _format_articles(articles: list[dict], label: str, error: str | None = None) -> str:
    if error:
        return f"Error fetching '{label}': {error}"
    if not articles:
        return f"No results found for: {label}"
    lines = [f"{label}\n"]
    for a in articles:
        lines.append(
            f"📰 {a.get('title')}\n"
            f"   Source: {a.get('source', {}).get('name')}\n"
            f"   Published: {a.get('publishedAt', 'N/A')}\n"
            f"   URL: {a.get('url')}\n"
        )
    return "\n".join(lines)


_COUNTRY_NAMES = {
    "in": "India", "gb": "United Kingdom", "au": "Australia", "ca": "Canada",
    "de": "Germany", "fr": "France", "jp": "Japan", "cn": "China",
    "br": "Brazil", "mx": "Mexico", "za": "South Africa", "ae": "UAE",
    "sg": "Singapore", "nz": "New Zealand", "ie": "Ireland",
}


@mcp.tool()
def get_top_headlines(country: str = "us", num_results: int = 5) -> str:
    """
    Fetch the latest top headlines for a country.

    Args:
        country: Two-letter country code (e.g. 'us', 'gb', 'in').
        num_results: Number of articles to return (default 5).

    Note: If top-headlines returns no results for a country (common with the free API tier),
    this tool automatically falls back to a keyword search using the country name.
    """
    articles, error = _call_newsapi(
        "https://newsapi.org/v2/top-headlines",
        {"country": country, "pageSize": num_results},
    )
    if error:
        return _format_articles([], f"Top Headlines — {country.upper()}", error=error)

    # Free-tier may not support all country codes — fall back to keyword search
    if not articles:
        country_name = _COUNTRY_NAMES.get(country.lower(), country.upper())
        from_date = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        articles, error = _call_newsapi(
            "https://newsapi.org/v2/everything",
            {
                "q": f"{country_name} news",
                "pageSize": num_results,
                "sortBy": "publishedAt",
                "language": "en",
                "from": from_date,
            },
        )
        label = f"Top Headlines — {country_name} (via keyword search)"
        return _format_articles(articles, label, error=error)

    return _format_articles(articles, f"Top Headlines — {country.upper()}")


@mcp.tool()
def search_news(query: str, num_results: int = 5, days_back: int = 7) -> str:
    """
    Search for recent news articles on a specific topic.

    Args:
        query: Keyword or topic (e.g. 'Tesla earnings', 'AI regulation').
        num_results: Number of articles to return (default 5).
        days_back: How many days back to search (default 7).
    """
    from_date = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles, error = _call_newsapi(
        "https://newsapi.org/v2/everything",
        {
            "q": query,
            "pageSize": num_results,
            "sortBy": "publishedAt",
            "language": "en",
            "from": from_date,
        },
    )
    return _format_articles(articles, f"News Search — '{query}' (last {days_back} days)", error=error)


@mcp.tool()
def get_news_by_category(
    category: str = "business", country: str = "us", num_results: int = 5
) -> str:
    """
    Fetch top headlines filtered by category.

    Args:
        category: One of 'business', 'entertainment', 'general', 'health',
                  'science', 'sports', 'technology'.
        country: Two-letter country code (default 'us').
        num_results: Number of articles to return (default 5).
    """
    articles, error = _call_newsapi(
        "https://newsapi.org/v2/top-headlines",
        {"category": category, "country": country, "pageSize": num_results},
    )
    return _format_articles(
        articles, f"Top {category.capitalize()} Headlines — {country.upper()}", error=error
    )


@mcp.tool()
def search_company_news(
    company_name: str,
    num_results: int = 5,
    days_back: int = 30,
    language: str = "en",
) -> str:
    """
    Search for news about a company by its full name rather than a ticker symbol.

    Useful when the caller knows the company name but not the exchange ticker,
    or wants broader coverage (e.g. subsidiary names, product names).

    Args:
        company_name: Company or brand name (e.g. 'Apple Inc', 'OpenAI', 'SpaceX').
        num_results: Number of articles to return (default 5).
        days_back: How many days back to search (default 30).
        language: Two-letter language code for results (default 'en').
    """
    from_date = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles, error = _call_newsapi(
        "https://newsapi.org/v2/everything",
        {
            "q": f'"{company_name}"',
            "pageSize": num_results,
            "sortBy": "publishedAt",
            "language": language,
            "from": from_date,
        },
    )
    return _format_articles(
        articles, f"News for '{company_name}' (last {days_back} days)", error=error
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
