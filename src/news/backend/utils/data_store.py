"""Fetch news.json from GitHub raw content with a short in-process cache.

Data-only commits (the daily agent run) are excluded from the deploy-on-push
workflow's path filter, so the running Space never rebuilds for a data update —
it just re-fetches this file on the next cache expiry.
"""
from __future__ import annotations
import os
from datetime import datetime

import requests

REPO = "bibhu2020/agenticai"
BRANCH = "main"
DATA_PATH = "src/news/data/news.json"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{DATA_PATH}"

_CACHE_TTL_SECS = 300  # 5 minutes

_cache: dict = {}
_cache_ts: datetime | None = None


def get_news_data(force: bool = False) -> dict:
    global _cache, _cache_ts
    now = datetime.now()
    if not force and _cache and _cache_ts and (now - _cache_ts).total_seconds() < _CACHE_TTL_SECS:
        return _cache

    headers = {}
    token = os.environ.get("NEWS_TRIGGER_GH_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        resp = requests.get(RAW_URL, headers=headers, timeout=10)
        if resp.status_code == 200:
            _cache = resp.json()
            _cache_ts = now
    except Exception:
        pass

    return _cache or {"generated_at": None, "categories": {}}
