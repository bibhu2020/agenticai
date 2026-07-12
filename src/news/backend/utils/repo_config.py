"""Persist the admin-configured local zip code to src/news/data/config.json in the
main repo, so the headless daily agent (checked out via actions/checkout) and this
running backend both read the same source of truth.

Mirrors utils/media_client.py's commit-with-retry pattern, but targets the main
agenticai repo via NEWS_TRIGGER_GH_TOKEN rather than the media repo.
"""
from __future__ import annotations
import base64
import json
import os
import random
import re
import time
from datetime import datetime

import requests

REPO = "bibhu2020/agenticai"
BRANCH = "main"
CONFIG_PATH = "src/news/data/config.json"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{CONFIG_PATH}"
API_URL = f"https://api.github.com/repos/{REPO}/contents/{CONFIG_PATH}"

DEFAULT_ZIP = "75454"
_MAX_PUSH_ATTEMPTS = 5
_CACHE_TTL_SECS = 60

_cache: dict = {}
_cache_ts: datetime | None = None


def get_local_config(force: bool = False) -> dict:
    """Fetch the current local config ({"zip": "..."}) from the repo, with a short cache."""
    global _cache, _cache_ts
    now = datetime.now()
    if not force and _cache and _cache_ts and (now - _cache_ts).total_seconds() < _CACHE_TTL_SECS:
        return _cache
    try:
        resp = requests.get(RAW_URL, timeout=10)
        if resp.status_code == 200:
            _cache = resp.json()
            _cache_ts = now
    except Exception:
        pass
    return _cache or {"zip": DEFAULT_ZIP}


def update_local_zip(zip_code: str) -> None:
    """Commit an updated zip code to src/news/data/config.json on main."""
    zip_code = zip_code.strip()
    if not re.fullmatch(r"\d{5}", zip_code):
        raise ValueError("zip must be a 5-digit US zip code")

    token = os.environ.get("NEWS_TRIGGER_GH_TOKEN", "")
    if not token:
        raise RuntimeError("NEWS_TRIGGER_GH_TOKEN is not set")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }
    content_bytes = (json.dumps({"zip": zip_code}, indent=2) + "\n").encode()

    last_exc: Exception | None = None
    for attempt in range(_MAX_PUSH_ATTEMPTS):
        if attempt > 0:
            time.sleep((0.5 * 2 ** (attempt - 1)) + random.uniform(0, 0.5))

        get_resp = requests.get(API_URL, headers=headers, timeout=10)
        sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

        put_payload: dict = {
            "message": f"chore(news): update local zip to {zip_code}",
            "content": base64.b64encode(content_bytes).decode(),
            "branch": BRANCH,
        }
        if sha:
            put_payload["sha"] = sha

        put_resp = requests.put(API_URL, headers=headers, json=put_payload, timeout=20)
        if put_resp.status_code in (409, 422):
            last_exc = requests.HTTPError(
                f"{put_resp.status_code} updating {CONFIG_PATH} (attempt {attempt + 1}/{_MAX_PUSH_ATTEMPTS}): {put_resp.text}"
            )
            continue
        put_resp.raise_for_status()

        global _cache, _cache_ts
        _cache = {"zip": zip_code}
        _cache_ts = datetime.now()
        return

    raise last_exc or RuntimeError(f"failed to update {CONFIG_PATH}")
