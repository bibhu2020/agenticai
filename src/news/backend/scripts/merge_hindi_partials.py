#!/usr/bin/env python3
"""Merge per-category Hindi partial JSON files into src/news/data/news.json
(GitHub Actions merge-hindi job — mirrors merge_partials.py's pattern).

Reads src/news/data/partial_hindi/<category>.json (one article list per file,
written by run_hindi_translation.py for a single category) and copies
title_hi/summary_hi/audio_hi onto the matching article (by index) in news.json's
existing categories — the English article data itself is untouched.

Stamps the top-level hindi_generated_at completion marker as long as at least
_MIN_SUCCESS_RATIO of the categories that have articles in news.json produced a
partial file that day. A category that's missing (its matrix job failed — e.g. a
transient LLM error) silently falls back to English per-article in the frontend
already, so requiring literally every category to succeed just to show the toggle
at all was too strict — one flaky category shouldn't take down Hindi for
everything else that *did* translate successfully.
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
_MIN_SUCCESS_RATIO = 0.8


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
    success_ratio = len(completed) / len(expected) if expected else 0.0
    if missing:
        print(f"[merge-hindi] categories missing Hindi translation: {sorted(missing)} "
              f"({len(completed)}/{len(expected)} succeeded, {success_ratio:.0%})")

    if success_ratio >= _MIN_SUCCESS_RATIO:
        data["hindi_generated_at"] = datetime.now(timezone.utc).isoformat()
        print(f"[merge-hindi] {success_ratio:.0%} of categories translated (>= {_MIN_SUCCESS_RATIO:.0%} threshold) "
              f"— hindi_generated_at set; missing categories fall back to English per-article")
    else:
        data.pop("hindi_generated_at", None)
        print(f"[merge-hindi] only {success_ratio:.0%} of categories translated "
              f"(< {_MIN_SUCCESS_RATIO:.0%} threshold) — hindi_generated_at NOT set")

    _NEWS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[merge-hindi] wrote {_NEWS_PATH}")

    shutil.rmtree(_PARTIAL_DIR, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
