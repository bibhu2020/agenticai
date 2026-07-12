#!/usr/bin/env python3
"""Entry point for the local weather + events collector (GitHub Actions, non-matrix job).

Writes data/partial/local_weather.json and data/partial/local_events.json as plain
JSON arrays of article-shaped picks, so merge_partials.py folds them into
news.json's "categories" exactly like every other category's partial — no
special-casing needed there.
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

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _attach_audio(cat_key: str, items: list[dict]) -> None:
    if not os.environ.get("GH_MEDIA_TOKEN"):
        log.info("GH_MEDIA_TOKEN not set — skipping audio generation for %s", cat_key)
        return

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tts import synthesize
    from utils.media_client import push_audio_bytes

    def _synth_one(idx: int, article: dict) -> bytes:
        text = f"{article['title']}. {article['summary']}"
        return synthesize(text)

    with ThreadPoolExecutor(max_workers=min(4, len(items))) as executor:
        future_to_idx = {executor.submit(_synth_one, idx, a): idx for idx, a in enumerate(items)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                mp3_bytes = future.result()
                items[idx]["audio"] = push_audio_bytes(mp3_bytes, f"{cat_key}/{idx}.mp3")
            except Exception as exc:
                log.warning("audio generation failed for %s[%d]: %s", cat_key, idx, exc)
                items[idx]["audio"] = ""


def main() -> int:
    required = ["OPENROUTER_API_KEY", "OPENWEATHER_API_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        return 1

    from agents.local import get_configured_zip, geocode_zip, fetch_weather, fetch_events

    zip_code = get_configured_zip()
    log.info("Collecting local weather + events for zip %s …", zip_code)
    try:
        place = geocode_zip(zip_code)
        log.info("Resolved zip %s -> %s, %s", zip_code, place.get("city"), place.get("state"))

        weather_items = [fetch_weather(place)]
        log.info("Weather: %s", weather_items[0]["summary"])

        event_items = fetch_events(place)
        log.info("Found %d local events", len(event_items))

        _attach_audio("local_weather", weather_items)
        _attach_audio("local_events", event_items)

        out_dir = _DATA_DIR / "partial"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "local_weather.json").write_text(json.dumps(weather_items, indent=2, ensure_ascii=False))
        (out_dir / "local_events.json").write_text(json.dumps(event_items, indent=2, ensure_ascii=False))
        log.info("Wrote partial/local_weather.json and partial/local_events.json")
        return 0
    except Exception as exc:
        log.exception("Local extras collection failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
