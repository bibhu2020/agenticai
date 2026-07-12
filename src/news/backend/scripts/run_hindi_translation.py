#!/usr/bin/env python3
"""Entry point for the daily Hindi translation + narration pass for ONE category
(GitHub Actions matrix job — mirrors run_agent.py's per-category matrix pattern,
so all categories translate in parallel instead of one job doing all of them).

Runs after the English digest has been merged into news.json — reads it, translates
+ narrates just NEWS_HINDI_CATEGORY's articles, and writes
data/partial_hindi/<category>.json (that category's article list, augmented with
title_hi/summary_hi/audio_hi) for merge_hindi_partials.py to fold back into
news.json in a later job. Only writes the partial if the category's translation
call succeeded — a missing partial file is exactly the signal
merge_hindi_partials.py uses to withhold the hindi_generated_at completion marker
for the whole day.
"""
from __future__ import annotations
import sys
import os
import json
from pathlib import Path

# Add backend/ (parent of this scripts/ dir) to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_NEWS_PATH = Path(__file__).resolve().parents[2] / "data" / "news.json"
_OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "partial_hindi"


def main() -> int:
    required = ["OPENROUTER_API_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        return 1

    cat_key = os.environ.get("NEWS_HINDI_CATEGORY", "").strip()
    if not cat_key:
        log.error("NEWS_HINDI_CATEGORY is not set")
        return 1

    if not _NEWS_PATH.exists():
        log.error("No news.json found at %s — nothing to translate", _NEWS_PATH)
        return 1

    try:
        data = json.loads(_NEWS_PATH.read_text())
    except json.JSONDecodeError as exc:
        log.error("Could not parse %s: %s", _NEWS_PATH, exc)
        return 1

    categories_in_news = data.get("categories", {})
    if cat_key not in categories_in_news:
        log.error("Unknown category %s — not present in news.json", cat_key)
        return 1

    articles = categories_in_news[cat_key]
    if not articles:
        # A category can legitimately have zero articles that day (e.g. no local
        # events found) — that's not an error, just nothing to translate. No
        # partial is written, but merge_hindi_partials.py already excludes empty
        # categories from what it expects a partial for, so this doesn't block
        # the hindi_generated_at completion marker.
        log.info("Category %s has no articles today — nothing to translate", cat_key)
        return 0

    log.info("Translating %s (%d articles) …", cat_key, len(articles))
    try:
        from agents.hindi import translate_all, generate_audio_all

        categories = {cat_key: articles}
        fatal = translate_all(categories)
        generate_audio_all(categories)

        if fatal:
            log.error("Translation failed for %s — not writing a partial", cat_key)
            return 1

        _OUT_DIR.mkdir(parents=True, exist_ok=True)
        (_OUT_DIR / f"{cat_key}.json").write_text(json.dumps(articles, indent=2, ensure_ascii=False))
        log.info("Wrote partial_hindi/%s.json", cat_key)
        return 0
    except Exception as exc:
        log.exception("Hindi translation failed for %s: %s", cat_key, exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
