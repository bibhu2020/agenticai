"""MCP server exposing FIFA data-fetching tools via FastMCP."""
from __future__ import annotations
import sys
import os

# Allow importing from the backend package when running as standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from agents.tools import fetch_today_scores, fetch_upcoming_schedule, fetch_fifa_news

mcp = FastMCP("FIFA World Cup 2026 Tools", version="1.0.0")


@mcp.tool()
def get_today_scores() -> str:
    """Return today's FIFA World Cup 2026 match scores as JSON."""
    return fetch_today_scores.invoke({})


@mcp.tool()
def get_upcoming_schedule() -> str:
    """Return FIFA World Cup 2026 matches scheduled for the next 7 days as JSON."""
    return fetch_upcoming_schedule.invoke({})


@mcp.tool()
def get_latest_news() -> str:
    """Return the latest FIFA World Cup 2026 news articles with thumbnails as JSON."""
    return fetch_fifa_news.invoke({})


if __name__ == "__main__":
    mcp.run()
