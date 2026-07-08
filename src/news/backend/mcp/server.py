"""MCP server exposing news data-fetching tools via FastMCP."""
from __future__ import annotations
import sys
import os

# Allow importing from the backend package when running as standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from agents.tools import fetch_rss_candidates, duckduckgo_news_search, extract_thumbnail

mcp = FastMCP("News PWA Tools", version="1.0.0")


@mcp.tool()
def get_rss_candidates(feed_url: str, max_items: int = 15) -> str:
    """Fetch and parse an RSS/Atom feed, returning candidate news articles as JSON."""
    return fetch_rss_candidates.invoke({"feed_url": feed_url, "max_items": max_items})


@mcp.tool()
def search_recent_news(query: str, max_results: int = 15) -> str:
    """Search DuckDuckGo News for recent articles matching a query, returned as JSON."""
    return duckduckgo_news_search.invoke({"query": query, "max_results": max_results, "timelimit": "d"})


@mcp.tool()
def get_article_thumbnail(url: str) -> str:
    """Return the Open Graph / Twitter Card thumbnail image URL for an article page."""
    return extract_thumbnail.invoke({"url": url})


if __name__ == "__main__":
    mcp.run()
