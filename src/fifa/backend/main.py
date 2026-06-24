"""FastAPI backend for FIFA World Cup 2026 dashboard."""
from __future__ import annotations
import os
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

try:
    from utils.excel_handler import read_excel
    from utils.github_client import download_excel
except ImportError:
    from .utils.excel_handler import read_excel
    from .utils.github_client import download_excel

app = FastAPI(title="FIFA World Cup 2026 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-process cache
_cache: dict = {}
_cache_ts: datetime | None = None
_CACHE_TTL_SECS = 300  # 5 minutes


def _get_data() -> dict:
    global _cache, _cache_ts
    now = datetime.now()
    if _cache and _cache_ts and (now - _cache_ts).total_seconds() < _CACHE_TTL_SECS:
        return _cache
    raw = download_excel()
    if raw:
        _cache = read_excel(raw)
        _cache_ts = now
    return _cache or {}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/scores")
async def get_scores():
    data = _get_data()
    return JSONResponse(data.get("scores", []))


@app.get("/api/schedule")
async def get_schedule():
    data = _get_data()
    return JSONResponse(data.get("schedule", []))


@app.get("/api/news")
async def get_news():
    data = _get_data()
    return JSONResponse(data.get("news", []))


@app.get("/api/summary")
async def get_summary():
    data = _get_data()
    scores = data.get("scores", [])
    schedule = data.get("schedule", [])
    news = data.get("news", [])
    return {
        "matches_today": len(scores),
        "live": sum(1 for m in scores if "live" in str(m.get("status", "")).lower() or "progress" in str(m.get("status", "")).lower()),
        "final": sum(1 for m in scores if "final" in str(m.get("status", "")).lower() or "ft" in str(m.get("status", "")).lower()),
        "upcoming_today": sum(1 for m in scores if "scheduled" in str(m.get("status", "")).lower()),
        "upcoming_7days": len(schedule),
        "news_count": len(news),
        "last_updated": _cache_ts.isoformat() if _cache_ts else None,
    }


_ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
_ESPN_STANDINGS = "https://site.api.espn.com/apis/v2/sports/soccer/fifa.world/standings"

_KNOCKOUT_ROUNDS = {
    "r32":   ["round of 32"],
    "r16":   ["round of 16"],
    "qf":    ["quarterfinal", "quarter-final", "quarter final"],
    "sf":    ["semifinal", "semi-final", "semi final"],
    "final": ["final"],
    "third": ["third place", "3rd place"],
}


def _classify_round(round_name: str) -> str | None:
    rn = round_name.lower()
    for key, patterns in _KNOCKOUT_ROUNDS.items():
        if any(p in rn for p in patterns):
            return key
    return None


def _fetch_standings() -> list[dict]:
    try:
        resp = requests.get(_ESPN_STANDINGS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    groups = []
    for group in data.get("children", []):
        group_name = group.get("name", "")
        entries = group.get("standings", {}).get("entries", [])
        rows = []
        for entry in entries:
            team = entry.get("team", {})
            logos = team.get("logos", [])
            stats_raw = {s["abbreviation"]: s["displayValue"] for s in entry.get("stats", [])}
            note = entry.get("note", {})
            rows.append({
                "pos":       int(stats_raw.get("R", 0) or 0),
                "team":      team.get("displayName", ""),
                "logo":      logos[0].get("href", "") if logos else "",
                "gp":        stats_raw.get("GP", "0"),
                "w":         stats_raw.get("W", "0"),
                "d":         stats_raw.get("D", "0"),
                "l":         stats_raw.get("L", "0"),
                "gf":        stats_raw.get("F", "0"),
                "ga":        stats_raw.get("A", "0"),
                "gd":        stats_raw.get("GD", "0"),
                "pts":       stats_raw.get("P", "0"),
                "advanced":  int(stats_raw.get("ADV", 0) or 0),
                "note":      note.get("description", ""),
                "note_color": note.get("color", ""),
            })
        rows.sort(key=lambda r: r["pos"])
        groups.append({"group": group_name, "rows": rows})
    return groups


def _fetch_knockout() -> dict:
    data = _get_data()
    all_matches = data.get("scores", []) + data.get("schedule", [])
    buckets: dict[str, list] = {k: [] for k in _KNOCKOUT_ROUNDS}
    seen: set = set()
    for m in all_matches:
        mid = m.get("match_id", "")
        if mid in seen:
            continue
        seen.add(mid)
        key = _classify_round(m.get("round", ""))
        if key:
            buckets[key].append(m)
    return buckets


_ESPN_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
_HL_CACHE: list = []
_HL_CACHE_TS: datetime | None = None
_HL_TTL_SECS = 1800  # 30 min — YouTube search is slow, don't hammer it


def _get_recent_completed(days_back: int = 7, limit: int = 4) -> list[dict]:
    from datetime import timedelta, timezone
    utc_now = datetime.now(timezone.utc)
    matches: list[dict] = []
    for delta in range(0, days_back + 1):
        target = utc_now - timedelta(days=delta)
        date_str = target.strftime("%Y%m%d")
        try:
            resp = requests.get(f"{_ESPN_BASE_URL}/scoreboard?dates={date_str}", timeout=15)
            if resp.status_code != 200:
                continue
            for ev in resp.json().get("events", []):
                comp = ev.get("competitions", [{}])[0]
                status = comp.get("status", {}).get("type", {}).get("description", "").lower()
                if not any(s in status for s in ["final", "ft", "ended", "full time"]):
                    continue
                competitors = comp.get("competitors", [{}, {}])
                home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
                away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[-1])
                home_team = home.get("team", {})
                away_team = away.get("team", {})
                matches.append({
                    "home_team": home_team.get("displayName", ""),
                    "home_logo": (home_team.get("logos") or [{}])[0].get("href", ""),
                    "home_score": home.get("score", ""),
                    "away_team": away_team.get("displayName", ""),
                    "away_logo": (away_team.get("logos") or [{}])[0].get("href", ""),
                    "away_score": away.get("score", ""),
                    "date": ev.get("date", "")[:10],
                    "round": ev.get("name", ""),
                })
                if len(matches) >= limit:
                    return matches
        except Exception:
            continue
    return matches


def _yt_search(home: str, away: str) -> tuple[str | None, str | None]:
    """Return (youtube_url, video_id) via DDGS, None if not found."""
    import re
    query = f"FIFA World Cup 2026 {home} vs {away} highlights"
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=8):
                url = r.get("href", "")
                m = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
                if m:
                    return url, m.group(1)
    except Exception:
        pass
    return None, None


def _fetch_highlights() -> list[dict]:
    global _HL_CACHE, _HL_CACHE_TS
    now = datetime.now()
    if _HL_CACHE and _HL_CACHE_TS and (now - _HL_CACHE_TS).total_seconds() < _HL_TTL_SECS:
        return _HL_CACHE

    matches = _get_recent_completed(days_back=7, limit=4)
    results = []
    for m in matches:
        _, vid_id = _yt_search(m["home_team"], m["away_team"])
        results.append({
            **m,
            "youtube_id": vid_id,
            "youtube_url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else None,
            "thumbnail": f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg" if vid_id else None,
        })

    _HL_CACHE = results
    _HL_CACHE_TS = now
    return results


@app.get("/api/highlights")
async def get_highlights():
    return JSONResponse(_fetch_highlights())


@app.get("/api/standings")
async def get_standings():
    groups = _fetch_standings()
    knockout = _fetch_knockout()
    return JSONResponse({"groups": groups, "knockout": knockout})


@app.post("/api/refresh")
async def refresh_cache():
    global _cache_ts
    _cache_ts = None
    _get_data()
    return {"status": "refreshed", "timestamp": datetime.now().isoformat()}


# ── Serve Vue.js SPA ─────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dist = os.path.abspath(os.path.join(current_dir, "../frontend/dist"))

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    icons_dir = os.path.join(frontend_dist, "icons")
    if os.path.exists(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

    @app.get("/{rest_of_path:path}")
    async def serve_spa(rest_of_path: str):
        file_path = os.path.join(frontend_dist, rest_of_path)
        if rest_of_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
