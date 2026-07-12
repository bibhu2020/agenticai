#!/usr/bin/env python3
"""Merge per-category Hindi partial JSON files into src/news/data/news.json
(GitHub Actions merge-hindi job — mirrors merge_partials.py's pattern).

Reads src/news/data/partial_hindi/<category>.json (one article list per file,
written by run_hindi_translation.py for a single category) and copies
title_hi/summary_hi/audio_hi onto the matching article (by index) in news.json's
existing categories — the English article data itself is untouched.

Only stamps the top-level hindi_generated_at completion marker if EVERY category
that has articles in news.json also produced a partial file that day — a missing
category (its matrix job failed) means the whole day is English-only for the
toggle, not just that category.
"""
from __future__ import annotations
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_NEWS_PATH = _DATA_DIR / "news.json"
_PARTIAL_DIR = _DATA_DIR / "partial_hindi"


def main() -> int:
    if not _NEWS_PATH.exists():
        print(f"[merge-hindi] no news.json at {_NEWS_PATH}, nothing to merge into")
        return 1

    try:
        data = json.loads(_NEWS_PATH.read_text())
    except json.JSONDecodeError as exc:
        print(f"[merge-hindi] could not parse {_NEWS_PATH}: {exc}")
        return 1

    categories: dict = data.get("categories", {})
    expected = {cat_key for cat_key, articles in categories.items() if articles}
    completed = set()

    if _PARTIAL_DIR.is_dir():
        for partial_file in sorted(_PARTIAL_DIR.glob("*.json")):
            cat_key = partial_file.stem
            if cat_key not in categories:
                print(f"[merge-hindi] skipping partial for unknown category {cat_key}")
                continue
            try:
                translated_articles = json.loads(partial_file.read_text())
            except json.JSONDecodeError as exc:
                print(f"[merge-hindi] skipping unreadable partial {partial_file.name}: {exc}")
                continue

            for i, translated in enumerate(translated_articles):
                if i >= len(categories[cat_key]):
                    continue
                for field in ("title_hi", "summary_hi", "audio_hi"):
                    if field in translated:
                        categories[cat_key][i][field] = translated[field]

            completed.add(cat_key)
            print(f"[merge-hindi] merged {cat_key} ({len(translated_articles)} articles)")
    else:
        print(f"[merge-hindi] no partial_hindi directory at {_PARTIAL_DIR}")

    missing = expected - completed
    if missing:
        print(f"[merge-hindi] categories missing Hindi translation: {sorted(missing)} — hindi_generated_at NOT set")
        data.pop("hindi_generated_at", None)
    else:
        data["hindi_generated_at"] = datetime.now(timezone.utc).isoformat()
        print("[merge-hindi] all categories translated successfully — hindi_generated_at set")

    _NEWS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[merge-hindi] wrote {_NEWS_PATH}")

    shutil.rmtree(_PARTIAL_DIR, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
