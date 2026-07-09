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
    from ..tts import synthesize
    from ..utils.media_client import push_audio_bytes
except ImportError:
    from agents.sources import CATEGORIES
    from agents.tools import fetch_rss_candidates, duckduckgo_news_search, extract_thumbnail
    from llm import get_llm
    from tts import synthesize
    from utils.media_client import push_audio_bytes

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

def _fetch_one_category(cat_key: str, cfg) -> tuple[str, list[dict], str | None]:
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

    error = "no candidates found from RSS or DuckDuckGo" if not items else None
    return cat_key, items[:_MAX_CANDIDATES_PER_CATEGORY], error


def node_fetch_candidates(state: NewsState) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    candidates: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}

    # Pure network I/O (RSS + DuckDuckGo) — safe to run all 10 categories at once.
    with ThreadPoolExecutor(max_workers=len(CATEGORIES)) as executor:
        for cat_key, items, error in executor.map(lambda kv: _fetch_one_category(*kv), CATEGORIES.items()):
            candidates[cat_key] = items
            if error:
                errors[cat_key] = error

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


def _summarize_one(llm, cat_key: str, cfg, items: list[dict]) -> tuple[str, list[dict], str | None]:
    if not items:
        return cat_key, [], None

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
        return cat_key, [p.model_dump() for p in picks], None
    except Exception as exc:
        return cat_key, [], f"summarization failed: {exc}"


def node_rank_and_summarize(state: NewsState) -> dict:
    import os
    from concurrent.futures import ThreadPoolExecutor

    llm = get_llm().with_structured_output(CategoryPicks)
    categories: dict[str, list[dict]] = {}
    errors = dict(state.get("errors", {}))

    # LLM calls (network + inference latency, not CPU-bound locally) — parallelize
    # with a moderate cap rather than all 10 at once, to stay well under OpenRouter
    # rate limits.
    max_workers = min(int(os.environ.get("LLM_MAX_WORKERS", "5")), len(CATEGORIES))
    jobs = [(cat_key, cfg, state["candidates"].get(cat_key, [])) for cat_key, cfg in CATEGORIES.items()]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for cat_key, picks, error in executor.map(lambda j: _summarize_one(llm, *j), jobs):
            categories[cat_key] = picks
            if error:
                errors[cat_key] = error

    return {"categories": categories, "errors": errors}


def node_resolve_thumbnails(state: NewsState) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    categories = state["categories"]
    needs_scrape: list[dict] = []

    for cat_key, picks in categories.items():
        candidate_images = {c.get("link", ""): c.get("image", "") for c in state["candidates"].get(cat_key, [])}
        for article in picks:
            image = candidate_images.get(article["url"], "")
            if image:
                article["image"] = image
            else:
                needs_scrape.append(article)

    def _resolve(article: dict) -> None:
        print(f"[agent] resolving thumbnail for {article['url']} …")
        article["image"] = extract_thumbnail.invoke({"url": article["url"]})

    if needs_scrape:
        # Network-bound page scrapes — safe to run well beyond CPU core count.
        with ThreadPoolExecutor(max_workers=min(8, len(needs_scrape))) as executor:
            list(executor.map(_resolve, needs_scrape))

    return {"categories": categories}


def node_generate_audio(state: NewsState) -> dict:
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not os.environ.get("GH_MEDIA_TOKEN"):
        print("[agent] GH_MEDIA_TOKEN not set — skipping audio generation")
        return {}

    categories = state["categories"]
    errors = dict(state.get("errors", {}))

    def _synth_one(cat_key: str, idx: int, article: dict) -> bytes:
        text = f"{article['title']}. {article['summary']}"
        return synthesize(text)

    jobs = [
        (cat_key, idx, article)
        for cat_key, picks in categories.items()
        for idx, article in enumerate(picks)
    ]
    max_workers = int(os.environ.get("TTS_MAX_WORKERS", "4"))
    print(f"[agent] synthesizing audio for {len(jobs)} articles ({max_workers} workers in parallel) …")

    # Synthesis (CPU-bound) runs in parallel across worker threads. Pushes to the
    # media repo happen one at a time here on the main thread as results arrive —
    # GitHub's Contents API races concurrent commits to the same branch (409
    # Conflict), so the network write side must stay serialized even though
    # synthesis itself doesn't need to be.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {
            executor.submit(_synth_one, cat_key, idx, article): (cat_key, idx, article)
            for cat_key, idx, article in jobs
        }
        done = 0
        for future in as_completed(future_to_job):
            cat_key, idx, article = future_to_job[future]
            done += 1
            try:
                mp3_bytes = future.result()
                article["audio"] = push_audio_bytes(mp3_bytes, f"{cat_key}/{idx}.mp3")
            except Exception as exc:
                errors[f"{cat_key}[{idx}]_audio"] = f"audio generation failed: {exc}"
                article["audio"] = ""
            print(f"[agent] audio {done}/{len(jobs)} done ({cat_key}[{idx}])")

    return {"categories": categories, "errors": errors}


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
    g.add_node("generate_audio", node_generate_audio)
    g.add_node("save", node_save)

    g.set_entry_point("fetch_candidates")
    g.add_edge("fetch_candidates", "rank_and_summarize")
    g.add_edge("rank_and_summarize", "resolve_thumbnails")
    g.add_edge("resolve_thumbnails", "generate_audio")
    g.add_edge("generate_audio", "save")
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
