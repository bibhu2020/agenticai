"""LangGraph sequential workflow: fetch candidates -> rank+summarize -> resolve thumbnails -> save."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

try:
    from .sources import CATEGORIES
    from .tools import fetch_rss_candidates, duckduckgo_news_search, extract_thumbnail
    from ..llm import get_llm
except ImportError:
    from agents.sources import CATEGORIES
    from agents.tools import fetch_rss_candidates, duckduckgo_news_search, extract_thumbnail
    from llm import get_llm

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "news.json"
_MAX_CANDIDATES_PER_CATEGORY = 30
_PICKS_PER_CATEGORY = 5


class NewsState(TypedDict):
    run_date: str
    candidates: dict[str, list[dict]]
    categories: dict[str, list[dict]]
    errors: dict[str, str]


class ArticlePick(BaseModel):
    title: str = Field(description="Headline of the selected article")
    summary: str = Field(description="Neutral, factual summary of the article, about 100 words")
    url: str = Field(description="The exact source URL copied verbatim from the candidate list")
    source: str = Field(description="Name of the publication/outlet")
    published_at: str = Field(default="", description="Publication date/time if known, else empty string")


class CategoryPicks(BaseModel):
    articles: list[ArticlePick] = Field(description="The most-discussed, distinct articles for this category")


# ── nodes ────────────────────────────────────────────────────────────────────

def node_fetch_candidates(state: NewsState) -> dict:
    candidates: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}

    for cat_key, cfg in CATEGORIES.items():
        print(f"[agent] fetching candidates for {cat_key} …")
        seen_urls: set[str] = set()
        items: list[dict] = []

        for feed_url in cfg.rss_feeds:
            for article in fetch_rss_candidates.invoke({"feed_url": feed_url, "max_items": 15}):
                link = article.get("link", "")
                if link and link not in seen_urls:
                    seen_urls.add(link)
                    items.append(article)

        for article in duckduckgo_news_search.invoke({"query": cfg.ddg_query, "max_results": 15, "timelimit": "d"}):
            link = article.get("link", "")
            if link and link not in seen_urls:
                seen_urls.add(link)
                items.append(article)

        if not items:
            errors[cat_key] = "no candidates found from RSS or DuckDuckGo"

        candidates[cat_key] = items[:_MAX_CANDIDATES_PER_CATEGORY]

    return {"candidates": candidates, "errors": errors}


def _format_candidates_for_prompt(items: list[dict]) -> str:
    lines = []
    for i, item in enumerate(items):
        lines.append(
            f"{i + 1}. title: {item.get('title', '')}\n"
            f"   source: {item.get('source', '')}\n"
            f"   url: {item.get('link', '')}\n"
            f"   published: {item.get('published', '')}\n"
            f"   snippet: {(item.get('summary', '') or '')[:800]}"
        )
    return "\n".join(lines)


def node_rank_and_summarize(state: NewsState) -> dict:
    llm = get_llm().with_structured_output(CategoryPicks)
    categories: dict[str, list[dict]] = {}
    errors = dict(state.get("errors", {}))

    for cat_key, cfg in CATEGORIES.items():
        items = state["candidates"].get(cat_key, [])
        if not items:
            categories[cat_key] = []
            continue

        print(f"[agent] ranking + summarizing {cat_key} …")
        prompt = (
            f"You are curating the '{cfg.label}' section of a news digest.\n"
            f"Below are candidate articles gathered from RSS feeds and news search. "
            f"Pick the {_PICKS_PER_CATEGORY} most significant, most-widely-covered, and mutually distinct "
            f"stories (avoid near-duplicate stories about the same event from different outlets — prefer "
            f"variety of stories over variety of sources for the same story).\n\n"
            f"For each pick, write a neutral, factual summary that is CLOSE TO 100 WORDS (target 90-110 "
            f"words — this is a firm length requirement, not a cap; expand with relevant context, "
            f"background, and implications from the snippet if the core facts alone fall short) based "
            f"ONLY on the information in the snippet below — do not invent facts. Copy the 'url' field "
            f"exactly as given; do not alter or invent URLs.\n\n"
            f"Candidates:\n{_format_candidates_for_prompt(items)}"
        )
        try:
            result: CategoryPicks = llm.invoke(prompt)
            picks = result.articles[:_PICKS_PER_CATEGORY]
            categories[cat_key] = [p.model_dump() for p in picks]
        except Exception as exc:
            errors[cat_key] = f"summarization failed: {exc}"
            categories[cat_key] = []

    return {"categories": categories, "errors": errors}


def node_resolve_thumbnails(state: NewsState) -> dict:
    categories = state["categories"]
    for cat_key, picks in categories.items():
        candidate_images = {c.get("link", ""): c.get("image", "") for c in state["candidates"].get(cat_key, [])}
        for article in picks:
            image = candidate_images.get(article["url"], "")
            if not image:
                print(f"[agent] resolving thumbnail for {article['url']} …")
                image = extract_thumbnail.invoke({"url": article["url"]})
            article["image"] = image
    return {"categories": categories}


def node_save(state: NewsState) -> dict:
    print("[agent] saving news.json …")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": state["categories"],
    }
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return {}


# ── graph ────────────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(NewsState)
    g.add_node("fetch_candidates", node_fetch_candidates)
    g.add_node("rank_and_summarize", node_rank_and_summarize)
    g.add_node("resolve_thumbnails", node_resolve_thumbnails)
    g.add_node("save", node_save)

    g.set_entry_point("fetch_candidates")
    g.add_edge("fetch_candidates", "rank_and_summarize")
    g.add_edge("rank_and_summarize", "resolve_thumbnails")
    g.add_edge("resolve_thumbnails", "save")
    g.add_edge("save", END)

    return g.compile()


def run_agent() -> NewsState:
    graph = build_graph()
    result = graph.invoke({
        "run_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "candidates": {},
        "categories": {},
        "errors": {},
    })
    if result.get("errors"):
        print(f"[agent] completed with warnings: {result['errors']}")
    return result
