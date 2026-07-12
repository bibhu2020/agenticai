"""Hindi translation + narration pass, run after the day's English digest is merged.

Operates on an already-built `categories` dict (category key -> list of article
dicts) in place, adding `title_hi`/`summary_hi`/`audio_hi` fields where translation
and TTS succeed. Mirrors news_agent.py's node style (structured LLM output,
ThreadPoolExecutor, try/except-per-item tolerance) but works off the merged
news.json rather than the per-category NewsState/graph.
"""
from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydantic import BaseModel, Field

try:
    from ..llm import get_llm
    from ..tts import synthesize
    from ..utils.media_client import push_audio_bytes
except ImportError:
    from llm import get_llm
    from tts import synthesize
    from utils.media_client import push_audio_bytes

KOKORO_VOICE_HI = os.environ.get("KOKORO_VOICE_HI", "hf_alpha")


class TranslatedArticle(BaseModel):
    index: int = Field(description="Zero-based index of this article in the input list, copied exactly")
    title_hi: str = Field(description="Hindi (Devanagari script) translation of the title")
    summary_hi: str = Field(description="Hindi (Devanagari script) translation of the summary, preserving all facts and meaning")


class CategoryTranslations(BaseModel):
    articles: list[TranslatedArticle] = Field(description="One entry per input article, matched back by index")


def _format_articles_for_prompt(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles):
        lines.append(f"{i}. title: {a.get('title', '')}\n   summary: {a.get('summary', '')}")
    return "\n".join(lines)


_TRANSLATE_ATTEMPTS = 2


def _translate_one_category(llm, cat_key: str, articles: list[dict]) -> tuple[str, bool]:
    """Translates articles for one category in place. Returns (cat_key, is_fatal)."""
    if not articles:
        return cat_key, False

    print(f"[hindi] translating {cat_key} ({len(articles)} articles) …")
    prompt = (
        f"Translate the following news article titles and summaries into natural, fluent Hindi "
        f"(Devanagari script). Preserve all facts and meaning — this is a translation, not a "
        f"rewrite. Keep proper nouns (people, places, organizations) transliterated naturally as "
        f"a Hindi reader would expect. Copy the 'index' field for each article exactly as given.\n\n"
        f"Articles:\n{_format_articles_for_prompt(articles)}"
    )

    for attempt in range(1, _TRANSLATE_ATTEMPTS + 1):
        try:
            result: CategoryTranslations = llm.invoke(prompt)
            break
        except Exception as exc:
            print(f"[hindi] translation attempt {attempt}/{_TRANSLATE_ATTEMPTS} failed for {cat_key}: {exc}")
    else:
        return cat_key, True

    for item in result.articles:
        if 0 <= item.index < len(articles):
            articles[item.index]["title_hi"] = item.title_hi
            articles[item.index]["summary_hi"] = item.summary_hi
    return cat_key, False


def translate_all(categories: dict[str, list[dict]]) -> set[str]:
    """Translates every category's articles in place. Returns the set of category
    keys whose LLM call itself failed (a fatal, category-level error) — individual
    missing/out-of-range indices within an otherwise-successful call are not fatal."""
    llm = get_llm().with_structured_output(CategoryTranslations)
    max_workers = min(int(os.environ.get("LLM_MAX_WORKERS", "5")), max(1, len(categories)))

    fatal: set[str] = set()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_translate_one_category, llm, cat_key, articles): cat_key
            for cat_key, articles in categories.items()
        }
        for future in as_completed(futures):
            cat_key, is_fatal = future.result()
            if is_fatal:
                fatal.add(cat_key)
    return fatal


def _synth_one_hi(article: dict) -> bytes:
    text = f"{article['title_hi']}. {article['summary_hi']}"
    return synthesize(text, voice=KOKORO_VOICE_HI, lang="hi")


def generate_audio_all(categories: dict[str, list[dict]]) -> None:
    """Synthesizes + pushes Hindi audio for every article that has both title_hi and
    summary_hi. Sets article['audio_hi'] on success, '' on a per-article failure.
    Skips entirely (no error) if GH_MEDIA_TOKEN is unset, mirroring news_agent.py's
    node_generate_audio."""
    if not os.environ.get("GH_MEDIA_TOKEN"):
        print("[hindi] GH_MEDIA_TOKEN not set — skipping Hindi audio generation")
        return

    jobs = [
        (cat_key, idx, article)
        for cat_key, articles in categories.items()
        for idx, article in enumerate(articles)
        if article.get("title_hi") and article.get("summary_hi")
    ]
    max_workers = int(os.environ.get("TTS_MAX_WORKERS", "4"))
    print(f"[hindi] synthesizing audio for {len(jobs)} articles ({max_workers} workers in parallel) …")

    # Synthesis (CPU-bound) runs in parallel; pushes happen one at a time on the main
    # thread as results arrive — same rationale as node_generate_audio: GitHub's
    # Contents API races concurrent commits to the same branch.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {executor.submit(_synth_one_hi, article): (cat_key, idx, article) for cat_key, idx, article in jobs}
        done = 0
        for future in as_completed(future_to_job):
            cat_key, idx, article = future_to_job[future]
            done += 1
            try:
                mp3_bytes = future.result()
                article["audio_hi"] = push_audio_bytes(mp3_bytes, f"hi/{cat_key}/{idx}.mp3")
            except Exception as exc:
                print(f"[hindi] audio generation failed for {cat_key}[{idx}]: {exc}")
                article["audio_hi"] = ""
            print(f"[hindi] audio {done}/{len(jobs)} done ({cat_key}[{idx}])")
