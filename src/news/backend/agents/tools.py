"""LangChain tools for fetching news candidates: RSS feeds, DuckDuckGo news search, thumbnails."""
from __future__ import annotations
import feedparser
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


def _entry_image(entry: dict) -> str:
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


@tool
def fetch_rss_candidates(feed_url: str, max_items: int = 15) -> list[dict]:
    """
    Fetch and parse an RSS/Atom feed, returning candidate articles with
    title, link, summary, published, image, and source (the feed's site name).
    """
    try:
        parsed = feedparser.parse(feed_url)
        source = parsed.feed.get("title", "") if hasattr(parsed, "feed") else ""
        if parsed.bozo and not parsed.entries:
            return []
        results = []
        for entry in parsed.entries[:max_items]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "published": entry.get("published", entry.get("updated", "")),
                "image": _entry_image(entry),
                "source": source,
            })
        return results
    except Exception:
        return []


@tool
def duckduckgo_news_search(query: str, max_results: int = 15, timelimit: str = "d") -> list[dict]:
    """
    Search DuckDuckGo News for recent articles matching a query.
    Returns candidates with title, link, summary, published, image, source.
    """
    try:
        with DDGS() as ddgs:
            raw = ddgs.news(query, max_results=max_results, timelimit=timelimit, region="wt-wt")
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "summary": r.get("body", ""),
                "published": r.get("date", ""),
                "image": r.get("image", "") or "",
                "source": r.get("source", ""),
            }
            for r in raw
        ]
    except Exception:
        return []


@tool
def duckduckgo_text_search(query: str, max_results: int = 10) -> list[dict]:
    """
    Search the general web (not news-specific) via DuckDuckGo for pages matching a query.
    Returns candidates with title, link, summary — useful for content like local events
    that wouldn't show up in a news search.
    """
    try:
        with DDGS() as ddgs:
            raw = ddgs.text(query, max_results=max_results, region="wt-wt")
        return [
            {
                "title": r.get("title", ""),
                "link": r.get("href", "") or r.get("link", ""),
                "summary": r.get("body", ""),
            }
            for r in raw
        ]
    except Exception:
        return []


@tool
def extract_thumbnail(url: str, timeout: int = 5) -> str:
    """
    Fetch a web page and return its Open Graph / Twitter Card thumbnail image URL, or "" if none found.
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
    except Exception:
        return ""
