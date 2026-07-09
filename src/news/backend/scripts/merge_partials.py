#!/usr/bin/env python3
"""Merge per-category partial JSON files into src/news/data/news.json (GitHub Actions merge job).

Reads src/news/data/partial/<category>.json (one array of picks per file, written by
node_save in agents/news_agent.py) and merges them into the existing news.json's
categories. A category with no partial file (its matrix job failed or timed out)
keeps whatever it already had in news.json rather than being wiped to empty.
"""
from __future__ import annotations
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DATA_PATH = _DATA_DIR / "news.json"
_PARTIAL_DIR = _DATA_DIR / "partial"


def main() -> int:
    existing: dict = {}
    if _DATA_PATH.exists():
        try:
            existing = json.loads(_DATA_PATH.read_text())
        except json.JSONDecodeError:
            existing = {}

    categories: dict = dict(existing.get("categories", {}))

    if not _PARTIAL_DIR.is_dir():
        print(f"[merge] no partial directory at {_PARTIAL_DIR}, nothing to merge")
        return 0

    merged = 0
    for partial_file in sorted(_PARTIAL_DIR.glob("*.json")):
        cat_key = partial_file.stem
        try:
            picks = json.loads(partial_file.read_text())
        except json.JSONDecodeError as exc:
            print(f"[merge] skipping unreadable partial {partial_file.name}: {exc}")
            continue
        categories[cat_key] = picks
        merged += 1
        print(f"[merge] merged {cat_key} ({len(picks)} articles)")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": categories,
    }
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[merge] wrote {_DATA_PATH} with {len(categories)} categories ({merged} updated this run)")

    shutil.rmtree(_PARTIAL_DIR, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
