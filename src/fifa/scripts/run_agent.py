#!/usr/bin/env python3
"""Entry point for the daily FIFA World Cup 2026 data-fetch agent (GitHub Actions)."""
from __future__ import annotations
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> int:
    required = ["GOOGLE_API_KEY", "GH_MEDIA_TOKEN"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        return 1

    log.info("Starting FIFA World Cup 2026 data agent …")
    try:
        from agents.fifa_agent import run_agent
        result = run_agent()
        status = result.get("status", "unknown")
        scores = len(result.get("scores_data", []))
        schedule = len(result.get("schedule_data", []))
        news = len(result.get("news_data", []))
        log.info("Agent completed: status=%s scores=%d schedule=%d news=%d", status, scores, schedule, news)
        if status == "error":
            log.error("Agent error: %s", result.get("error", ""))
            return 1
        return 0
    except Exception as exc:
        log.exception("Agent run failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
