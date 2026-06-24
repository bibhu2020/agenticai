"""MCP Web Search Server — DuckDuckGo search, page fetching, and current datetime."""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] mcp-web-search: %(message)s",
)
log = logging.getLogger("mcp-web-search")

mcp = FastMCP("Web Search MCP", host="0.0.0.0", port=8001)


# ---------------------------------------------------------------------------
# Datetime
# ---------------------------------------------------------------------------

@mcp.tool()
def current_datetime(format: str = "natural") -> str:
    """
    Return the current date and time.

    Args:
        format: 'natural' → 'Saturday, June 07, 2025 at 3:59 PM'
                'natural_short' → 'Jun 07, 2025 at 3:59 PM'
                Or any strftime format string (e.g. '%Y-%m-%d').
    """
    now = datetime.now()
    if format == "natural":
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    if format == "natural_short":
        return now.strftime("%b %d, %Y at %I:%M %p")
    return now.strftime(format)


# ---------------------------------------------------------------------------
# Web search
# ---------------------------------------------------------------------------

@mcp.tool()
def duckduckgo_search(
    query: str,
    max_results: int = 5,
    search_type: str = "text",
    timelimit: str = "d",
    region: str = "us-en",
) -> list[dict]:
    """
    Search the web via DuckDuckGo and return result snippets.

    Args:
        query: The search query.
        max_results: Number of results to return (default 5).
        search_type: 'text' for general results, 'news' to include publication dates.
        timelimit: Recency filter — 'd' day, 'w' week, 'm' month, 'y' year.
        region: Region code (default 'us-en').
    """
    results: list[dict] = []
    with DDGS() as ddgs:
        if search_type == "news":
            raw = ddgs.news(query, max_results=max_results, timelimit=timelimit, region=region)
            for r in raw:
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("url", ""),
                    "snippet": r.get("body", ""),
                    "datetime": r.get("date", ""),
                })
        else:
            raw = ddgs.text(query, max_results=max_results, timelimit=timelimit, region=region)
            for r in raw:
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    return results


# ---------------------------------------------------------------------------
# Page fetching
# ---------------------------------------------------------------------------

@mcp.tool()
def fetch_page_content(url: str, timeout: int = 3) -> str:
    """
    Download a web page and return its readable text content.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds (default 3).
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)
    except Exception as e:
        return f"[ERROR] Could not fetch {url}: {e}"


@mcp.tool()
def extract_tables_from_page(url: str, timeout: int = 5) -> str:
    """
    Extract all HTML tables from a web page and return them as readable text.

    Especially useful for financial data pages, Wikipedia articles, and
    data-heavy sites where the information lives inside <table> elements.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds (default 5).
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            return f"No tables found on {url}."

        results = [f"Found {len(tables)} table(s) on {url}\n"]
        for i, table in enumerate(tables, 1):
            rows = table.find_all("tr")
            parsed = []
            for row in rows:
                cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                if any(cells):
                    parsed.append(" | ".join(cells))
            if parsed:
                results.append(f"--- Table {i} ---")
                results.extend(parsed)
                results.append("")
        return "\n".join(results)
    except Exception as e:
        return f"[ERROR] Could not extract tables from {url}: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
