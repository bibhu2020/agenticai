#!/usr/bin/env python3
"""Entry point for the daily Hindi translation + narration pass (GitHub Actions).

Runs after the English digest has been merged into news.json — reads it, adds
title_hi/summary_hi/audio_hi to as many articles as succeed, and only stamps the
top-level hindi_generated_at completion marker if every category's translation
call succeeded (individual per-article gaps don't block it, a whole category's
LLM call failing does).
"""
from __future__ import annotations
import sys
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# Add backend/ (parent of this scripts/ dir) to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_NEWS_PATH = Path(__file__).resolve().parents[2] / "data" / "news.json"


def main() -> int:
    required = ["OPENROUTER_API_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        return 1

    if not _NEWS_PATH.exists():
        log.error("No news.json found at %s — nothing to translate", _NEWS_PATH)
        return 1

    try:
        data = json.loads(_NEWS_PATH.read_text())
    except json.JSONDecodeError as exc:
        log.error("Could not parse %s: %s", _NEWS_PATH, exc)
        return 1

    categories = data.get("categories", {})
    log.info("Starting Hindi translation pass … (%d categories)", len(categories))

    try:
        from agents.hindi import translate_all, generate_audio_all

        fatal = translate_all(categories)
        generate_audio_all(categories)

        if fatal:
            log.warning("Hindi translation had fatal failures for categories: %s — hindi_generated_at NOT set", sorted(fatal))
        else:
            data["hindi_generated_at"] = datetime.now(timezone.utc).isoformat()
            log.info("All categories translated successfully — hindi_generated_at set")

        _NEWS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        log.info("Wrote %s", _NEWS_PATH)
        return 0
    except Exception as exc:
        log.exception("Hindi translation pass failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
