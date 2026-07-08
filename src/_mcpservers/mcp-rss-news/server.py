"""MCP RSS News Server — free RSS feed parsing and Open Graph thumbnail extraction, no API key required."""
import logging
import sys
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] mcp-rss-news: %(message)s",
)
log = logging.getLogger("mcp-rss-news")

mcp = FastMCP("RSS News MCP", host="0.0.0.0", port=8004)

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


def _entry_image(entry: dict) -> str:
    """Pull a thumbnail URL out of an RSS/Atom entry's media/enclosure fields, if present."""
    media_content = entry.get("media_content") or []
    for m in media_content:
        if m.get("url"):
            return m["url"]
    media_thumbnail = entry.get("media_thumbnail") or []
    for m in media_thumbnail:
        if m.get("url"):
            return m["url"]
    for link in entry.get("links", []) or []:
        if str(link.get("type", "")).startswith("image/"):
            return link.get("href", "")
    return ""


@mcp.tool()
def fetch_rss_feed(feed_url: str, max_items: int = 15) -> list[dict]:
    """
    Fetch and parse an RSS/Atom feed, returning candidate articles.

    Args:
        feed_url: The RSS/Atom feed URL.
        max_items: Maximum number of entries to return (default 15).

    Returns:
        A list of dicts with keys: title, link, summary, published, image.
    """
    try:
        parsed = feedparser.parse(feed_url)
        if parsed.bozo and not parsed.entries:
            return [{"error": f"Could not parse feed {feed_url}: {parsed.bozo_exception}"}]
        results = []
        for entry in parsed.entries[:max_items]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "published": entry.get("published", entry.get("updated", "")),
                "image": _entry_image(entry),
            })
        return results
    except Exception as e:
        return [{"error": f"[ERROR] Could not fetch {feed_url}: {e}"}]


@mcp.tool()
def extract_page_thumbnail(url: str, timeout: int = 5) -> str:
    """
    Fetch a web page and return its Open Graph / Twitter Card thumbnail image URL, if any.

    Args:
        url: The article URL.
        timeout: Request timeout in seconds (default 5).

    Returns:
        The thumbnail image URL, or an empty string if none is found.
    """
    try:
        resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        for prop in ("og:image", "twitter:image", "twitter:image:src"):
            tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if tag and tag.get("content"):
                return tag["content"]
        return ""
    except Exception as e:
        log.warning("Could not extract thumbnail from %s: %s", url, e)
        return ""


if __name__ == "__main__":
    mcp.run(transport="stdio")
