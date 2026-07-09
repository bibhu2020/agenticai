"""Local text-to-speech via Kokoro-82M (ONNX, CPU). Lazily loads a singleton model.

The underlying onnxruntime InferenceSession supports concurrent Run() calls from
multiple threads, so `synthesize()` is safe to call from a thread pool once the
model is loaded — only the lazy singleton construction itself needs a lock.
"""
from __future__ import annotations
import io
import os
import threading
from pathlib import Path

import requests
import soundfile as sf

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

DEFAULT_VOICE = os.environ.get("KOKORO_VOICE", "af_heart")
CACHE_DIR = Path(os.environ.get("KOKORO_CACHE_DIR", Path.home() / ".cache" / "kokoro"))
MODEL_PATH = CACHE_DIR / "kokoro-v1.0.onnx"
VOICES_PATH = CACHE_DIR / "voices-v1.0.bin"

_kokoro = None
_kokoro_lock = threading.Lock()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    tmp.rename(dest)


def _ensure_model_files() -> None:
    if not MODEL_PATH.exists():
        print(f"[tts] downloading Kokoro model to {MODEL_PATH} …")
        _download(MODEL_URL, MODEL_PATH)
    if not VOICES_PATH.exists():
        print(f"[tts] downloading Kokoro voices to {VOICES_PATH} …")
        _download(VOICES_URL, VOICES_PATH)


def _get_kokoro():
    global _kokoro
    if _kokoro is None:
        with _kokoro_lock:
            if _kokoro is None:
                from kokoro_onnx import Kokoro
                _ensure_model_files()
                _kokoro = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
    return _kokoro


def synthesize(text: str, voice: str = DEFAULT_VOICE, speed: float = 1.0) -> bytes:
    """Synthesize text to speech, returning MP3 bytes."""
    kokoro = _get_kokoro()
    samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    buf = io.BytesIO()
    sf.write(buf, samples, sample_rate, format="MP3")
    return buf.getvalue()
