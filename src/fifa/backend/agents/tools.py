"""LangChain tools for fetching FIFA World Cup 2026 data from ESPN and Serper."""
from __future__ import annotations
import json
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from langchain_core.tools import tool

CDT = ZoneInfo("America/Chicago")
_ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"


def _to_cdt(utc_str: str) -> str:
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        cdt_dt = dt.astimezone(CDT)
        return cdt_dt.strftime("%Y-%m-%d %I:%M %p CDT")
    except Exception:
        return utc_str


def _parse_event(event: dict) -> dict:
    comp = event.get("competitions", [{}])[0]
    competitors = comp.get("competitors", [{}, {}])
    home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0] if competitors else {})
    away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1] if len(competitors) > 1 else {})

    home_team = home.get("team", {})
    away_team = away.get("team", {})
    venue = comp.get("venue", {})
    address = venue.get("address", {})
    status = comp.get("status", {})

    return {
        "match_id": event.get("id", ""),
        "date": event.get("date", "")[:10],
        "time_cdt": _to_cdt(event.get("date", "")),
        "datetime_utc": event.get("date", ""),
        "home_team": home_team.get("displayName", "TBD"),
        "home_logo": home_team.get("logo", ""),
        "home_score": home.get("score", ""),
        "away_team": away_team.get("displayName", "TBD"),
        "away_logo": away_team.get("logo", ""),
        "away_score": away.get("score", ""),
        "status": status.get("type", {}).get("description", ""),
        "status_state": status.get("type", {}).get("state", ""),
        "venue": venue.get("fullName", ""),
        "city": address.get("city", ""),
        "round": event.get("name", ""),
    }


@tool
def fetch_today_scores() -> str:
    """Fetch FIFA World Cup 2026 match scores for today from ESPN."""
    try:
        resp = requests.get(f"{_ESPN_BASE}/scoreboard", timeout=15)
        resp.raise_for_status()
        events = resp.json().get("events", [])
        matches = [_parse_event(e) for e in events]
        return json.dumps(matches, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def fetch_upcoming_schedule() -> str:
    """Fetch FIFA World Cup 2026 upcoming matches for the next 7 days from ESPN."""
    utc_now = datetime.now(timezone.utc)
    matches: list[dict] = []
    for delta in range(1, 8):
        target = utc_now + timedelta(days=delta)
        date_str = target.strftime("%Y%m%d")
        try:
            resp = requests.get(f"{_ESPN_BASE}/scoreboard?dates={date_str}", timeout=15)
            if resp.status_code != 200:
                continue
            for event in resp.json().get("events", []):
                matches.append(_parse_event(event))
        except Exception:
            continue
    return json.dumps(matches, default=str)


@tool
def fetch_fifa_news() -> str:
    """Fetch the latest FIFA World Cup 2026 news articles with thumbnails."""
    articles: list[dict] = []

    # Primary: ESPN news API
    try:
        resp = requests.get(f"{_ESPN_BASE}/news?limit=15", timeout=15)
        if resp.status_code == 200:
            for item in resp.json().get("articles", []):
                images = item.get("images", [])
                thumbnail = images[0].get("url", "") if images else ""
                articles.append({
                    "title": item.get("headline", ""),
                    "summary": item.get("description", ""),
                    "thumbnail_url": thumbnail,
                    "article_url": item.get("links", {}).get("web", {}).get("href", ""),
                    "published_date": (item.get("published", "") or "")[:10],
                    "source": "ESPN",
                })
    except Exception:
        pass

    # Fallback: DuckDuckGo News (free, no key required)
    if len(articles) < 5:
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                for item in ddgs.news("FIFA World Cup 2026", max_results=12):
                    articles.append({
                        "title": item.get("title", ""),
                        "summary": item.get("body", ""),
                        "thumbnail_url": item.get("image", ""),
                        "article_url": item.get("url", ""),
                        "published_date": (item.get("date") or "")[:10],
                        "source": item.get("source", ""),
                    })
        except Exception:
            pass

    return json.dumps(articles, default=str)
