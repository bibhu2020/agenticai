#!/usr/bin/env python3
"""Entry point for the daily news digest agent (GitHub Actions)."""
from __future__ import annotations
import sys
import os

# Add backend/ (parent of this scripts/ dir) to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> int:
    required = ["OPENROUTER_API_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        return 1

    category_keys = [c.strip() for c in os.environ.get("NEWS_CATEGORIES", "").split(",") if c.strip()] or None
    log.info("Starting daily news digest agent … (categories=%s)", category_keys or "all")
    try:
        from agents.news_agent import run_agent
        result = run_agent(category_keys=category_keys)
        counts = {k: len(v) for k, v in result.get("categories", {}).items()}
        log.info("Agent completed: %s", counts)
        errors = result.get("errors", {})
        if errors:
            log.warning("Completed with warnings: %s", errors)
        # Fail the job (red X in Actions) when a category produced nothing due to
        # an error, rather than reporting success on an empty result.
        failed = [k for k, v in result.get("categories", {}).items() if not v and k in errors]
        if failed:
            log.error("Categories failed with no articles: %s", ", ".join(failed))
            return 1
        return 0
    except Exception as exc:
        log.exception("Agent run failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
