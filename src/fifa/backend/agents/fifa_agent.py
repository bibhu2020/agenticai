"""LangGraph sequential workflow: fetch scores → schedule → news → save → push GitHub."""
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime
from typing import TypedDict

from langgraph.graph import StateGraph, END

try:
    from .tools import fetch_today_scores, fetch_upcoming_schedule, fetch_fifa_news
    from ..utils.excel_handler import create_excel
    from ..utils.github_client import push_excel
except ImportError:
    from agents.tools import fetch_today_scores, fetch_upcoming_schedule, fetch_fifa_news
    from utils.excel_handler import create_excel
    from utils.github_client import push_excel


class FIFAState(TypedDict):
    run_date: str
    scores_data: list[dict]
    schedule_data: list[dict]
    news_data: list[dict]
    status: str
    error: str


# ── nodes ──────────────────────────────────────────────────────────────────────

def node_fetch_scores(state: FIFAState) -> dict:
    print("[agent] fetching today's scores …")
    raw = fetch_today_scores.invoke({})
    data = json.loads(raw) if isinstance(raw, str) else raw
    if isinstance(data, dict) and "error" in data:
        return {"scores_data": [], "error": data["error"]}
    return {"scores_data": data or []}


def node_fetch_schedule(state: FIFAState) -> dict:
    print("[agent] fetching upcoming schedule …")
    raw = fetch_upcoming_schedule.invoke({})
    data = json.loads(raw) if isinstance(raw, str) else raw
    return {"schedule_data": data or []}


def node_fetch_and_summarize_news(state: FIFAState) -> dict:
    print("[agent] fetching news …")
    raw = fetch_fifa_news.invoke({})
    articles = json.loads(raw) if isinstance(raw, str) else raw
    articles = articles or []

    # Gemini summarization for articles that lack a summary
    try:
        try:
            from ..llm import get_llm
        except ImportError:
            from llm import get_llm
        llm = get_llm()
        for article in articles[:10]:
            if article.get("title") and not (article.get("summary") or "").strip():
                prompt = (
                    "Write a concise 2-sentence summary of this FIFA World Cup 2026 news headline: "
                    f"{article['title']}"
                )
                resp = llm.invoke(prompt)
                article["summary"] = resp.content.strip()
    except Exception as exc:
        print(f"[agent] summarization skipped: {exc}")

    return {"news_data": articles}


def node_save_and_push(state: FIFAState) -> dict:
    print("[agent] saving Excel and pushing to GitHub …")
    excel_bytes = create_excel(state["scores_data"], state["schedule_data"], state["news_data"])

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(excel_bytes)
        tmp_path = tmp.name

    try:
        success = push_excel(tmp_path)
        return {"status": "success" if success else "push_failed"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    finally:
        os.unlink(tmp_path)


# ── graph ──────────────────────────────────────────────────────────────────────

def build_graph() -> "CompiledGraph":
    g = StateGraph(FIFAState)
    g.add_node("fetch_scores", node_fetch_scores)
    g.add_node("fetch_schedule", node_fetch_schedule)
    g.add_node("fetch_news", node_fetch_and_summarize_news)
    g.add_node("save_push", node_save_and_push)

    g.set_entry_point("fetch_scores")
    g.add_edge("fetch_scores", "fetch_schedule")
    g.add_edge("fetch_schedule", "fetch_news")
    g.add_edge("fetch_news", "save_push")
    g.add_edge("save_push", END)

    return g.compile()


def run_agent() -> FIFAState:
    graph = build_graph()
    result = graph.invoke({
        "run_date": datetime.now().strftime("%Y-%m-%d"),
        "scores_data": [],
        "schedule_data": [],
        "news_data": [],
        "status": "running",
        "error": "",
    })
    return result
