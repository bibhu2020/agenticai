"""Zip-code-driven helpers for the "Local" tab: config, geocoding, weather, events.

Unlike the other categories (RSS + DDG news + LLM summarization of real news
articles), weather is deterministic (built directly from the OpenWeatherMap
response) and events come from general web search rather than a news feed.
Both are still emitted as article-shaped dicts (title/summary/url/source/
published_at/image) so they flow through the exact same save/merge/TTS/
frontend rendering path as every other category.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from pydantic import BaseModel, Field

try:
    from .tools import duckduckgo_text_search
    from ..llm import get_llm
except ImportError:
    from agents.tools import duckduckgo_text_search
    from llm import get_llm

DEFAULT_ZIP = "75454"
_CONFIG_PATH = Path(__file__).resolve().parents[2] / "data" / "config.json"
_MAX_EVENTS = 7


def get_configured_zip() -> str:
    try:
        data = json.loads(_CONFIG_PATH.read_text())
        zip_code = str(data.get("zip", "")).strip()
        return zip_code if zip_code else DEFAULT_ZIP
    except Exception:
        return DEFAULT_ZIP


def geocode_zip(zip_code: str) -> dict:
    """Resolve a US zip code to city/state/lat/lon via OpenWeatherMap's geocoding API."""
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    zip_resp = requests.get(
        "http://api.openweathermap.org/geo/1.0/zip",
        params={"zip": f"{zip_code},US", "appid": api_key},
        timeout=10,
    )
    zip_resp.raise_for_status()
    zdata = zip_resp.json()
    lat, lon, city = zdata["lat"], zdata["lon"], zdata.get("name", "")

    state = ""
    try:
        rev_resp = requests.get(
            "http://api.openweathermap.org/geo/1.0/reverse",
            params={"lat": lat, "lon": lon, "limit": 1, "appid": api_key},
            timeout=10,
        )
        rev_resp.raise_for_status()
        rev = rev_resp.json()
        if rev:
            state = rev[0].get("state", "")
    except Exception:
        pass

    return {"city": city, "state": state, "lat": lat, "lon": lon}


def _location_label(place: dict) -> str:
    return f"{place['city']}, {place['state']}" if place.get("state") else place["city"]


def fetch_weather(place: dict) -> dict:
    """Build a single article-shaped item summarizing current weather at `place`."""
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": place["lat"], "lon": place["lon"], "appid": api_key, "units": "imperial"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    desc = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"])
    feels_like = round(data["main"]["feels_like"])
    temp_min = round(data["main"]["temp_min"])
    temp_max = round(data["main"]["temp_max"])
    humidity = data["main"]["humidity"]
    wind = round(data.get("wind", {}).get("speed", 0))
    location = _location_label(place)

    summary = (
        f"{desc}, {temp}°F (feels like {feels_like}°F). "
        f"Today's range: {temp_min}°F to {temp_max}°F. "
        f"Humidity {humidity}%, wind {wind} mph."
    )

    return {
        "title": f"Weather in {location}",
        "summary": summary,
        "url": "",
        "source": "OpenWeatherMap",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image": "",
    }


class LocalEventPick(BaseModel):
    title: str = Field(description="Event name")
    date: str = Field(
        description="Best-effort date/time text for the event (e.g. 'Sat, Jul 18, 7:00 PM'). "
        "Use only what is stated in the source snippet — do not invent a date."
    )
    venue: str = Field(default="", description="Venue or location name if mentioned in the snippet")
    category: str = Field(default="other", description="One of: music, sports, market, festival, community, other")
    summary: str = Field(description="Short neutral description of the event, 40-70 words, based only on the snippet")
    url: str = Field(description="Source URL copied verbatim from the candidate list")


class LocalEventPicks(BaseModel):
    events: list[LocalEventPick] = Field(description="Up to 7 distinct upcoming local events happening in the next 7 days")


def _fetch_event_candidates(location: str) -> list[dict]:
    queries = [
        f"events in {location} this week",
        f"things to do in {location} next 7 days",
        f"{location} farmers market concerts festivals calendar",
    ]
    seen: set[str] = set()
    items: list[dict] = []
    for query in queries:
        for r in duckduckgo_text_search.invoke({"query": query, "max_results": 10}):
            link = r.get("link", "")
            if link and link not in seen:
                seen.add(link)
                items.append(r)
    return items[:30]


def _format_event_candidates(items: list[dict]) -> str:
    lines = []
    for i, item in enumerate(items):
        lines.append(
            f"{i + 1}. title: {item.get('title', '')}\n"
            f"   url: {item.get('link', '')}\n"
            f"   snippet: {(item.get('summary', '') or '')[:500]}"
        )
    return "\n".join(lines)


def fetch_events(place: dict) -> list[dict]:
    """Return up to _MAX_EVENTS article-shaped items for local events in the next 7 days."""
    location = _location_label(place)
    candidates = _fetch_event_candidates(location)
    if not candidates:
        return []

    llm = get_llm().with_structured_output(LocalEventPicks)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prompt = (
        f"You are curating a 'local events' section for {location}, covering the next 7 days starting {today}.\n"
        f"Below are candidate web search results about local happenings (concerts, sports, festivals, farmers "
        f"markets, community events, etc.). Pick up to {_MAX_EVENTS} distinct, real, upcoming events that are "
        f"clearly happening in or near {location} within the next 7 days. Skip anything that isn't a specific "
        f"event (generic venue pages, ticket marketplace listings with no event details, or events clearly in "
        f"the past or more than 7 days out). Use ONLY information present in the snippet — do not invent dates, "
        f"venues, or details.\n\nCandidates:\n{_format_event_candidates(candidates)}"
    )
    try:
        result: LocalEventPicks = llm.invoke(prompt)
    except Exception:
        return []

    return [
        {
            "title": e.title,
            "summary": e.summary,
            "url": e.url,
            "source": e.venue or "Local event",
            "published_at": e.date,
            "image": "",
            "category": e.category,
        }
        for e in result.events[:_MAX_EVENTS]
    ]
