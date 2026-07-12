"""Per-category source configuration: free RSS feeds + a DuckDuckGo fallback query.

RSS feeds are best-effort defaults from well-established outlets. Every category also
carries a DDG fallback query so the pipeline stays resilient if any single feed goes
stale or changes shape — `node_fetch_candidates` always queries both.
"""
from __future__ import annotations
from typing import NamedTuple


class CategorySource(NamedTuple):
    label: str
    rss_feeds: list[str]
    ddg_query: str


CATEGORIES: dict[str, CategorySource] = {
    "world": CategorySource(
        label="World News",
        rss_feeds=[
            "http://feeds.bbci.co.uk/news/world/rss.xml",
        ],
        ddg_query="world news today",
    ),
    "usa": CategorySource(
        label="USA News",
        rss_feeds=[
            "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
            "https://feeds.npr.org/1003/rss.xml",
        ],
        ddg_query="United States national news today",
    ),
    "india": CategorySource(
        label="India News",
        rss_feeds=[
            "http://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        ],
        ddg_query="India news today",
    ),
    "odisha": CategorySource(
        label="Odisha News",
        rss_feeds=[],
        ddg_query="Odisha news today",
    ),
    "sports": CategorySource(
        label="Sports",
        rss_feeds=[
            "https://www.espn.com/espn/rss/news",
            "http://feeds.bbci.co.uk/sport/rss.xml",
        ],
        ddg_query="top sports news today",
    ),
    "cricket": CategorySource(
        label="Cricket",
        rss_feeds=[
            "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
        ],
        ddg_query="cricket news today",
    ),
    "usa_stock": CategorySource(
        label="USA Stock",
        rss_feeds=[
            "http://feeds.marketwatch.com/marketwatch/topstories/",
        ],
        ddg_query="US stock market news today",
    ),
    "ai": CategorySource(
        label="AI",
        rss_feeds=[
            "https://www.technologyreview.com/feed/",
            "https://arstechnica.com/ai/feed/",
        ],
        ddg_query="artificial intelligence news today",
    ),
    "quantum": CategorySource(
        label="Quantum",
        rss_feeds=[
            "https://www.quantamagazine.org/feed/",
            "https://arstechnica.com/science/feed/",
        ],
        ddg_query="quantum computing news today",
    ),
    "trump": CategorySource(
        label="Trump",
        rss_feeds=[
            "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        ],
        ddg_query="Trump news today",
    ),
    "local": CategorySource(
        label="Local News",
        rss_feeds=[],
        # No fixed query — news_agent.py resolves this at fetch time from the
        # admin-configured zip code (see agents/local.py).
        ddg_query="local news today",
    ),
}
