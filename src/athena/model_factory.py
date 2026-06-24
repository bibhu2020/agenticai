"""Model factory — creates OpenAIChatCompletionsModel instances for multiple providers.

Providers supported:
  google  — Gemini models via Google's OpenAI-compatible endpoint
  openai  — OpenAI models (GPT-4o, etc.)
  ollama  — Local Ollama models via its OpenAI-compatible server

Langfuse tracing is applied automatically when LANGFUSE_SECRET_KEY and
LANGFUSE_PUBLIC_KEY are set in the environment.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from agents import OpenAIChatCompletionsModel

# ---------------------------------------------------------------------------
# Model catalog
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModelConfig:
    label: str        # display name shown in the sidebar
    provider: str     # internal routing key
    model_name: str   # identifier sent to the API
    key_env: str      # env var for the API key (empty → no key needed)
    note: str         # short description shown as tooltip / helper text


MODELS: list[ModelConfig] = [
    ModelConfig(
        "Gemini 2.5 Flash", "google", "gemini-2.5-flash",
        "GOOGLE_API_KEY", "Fast · free tier available",
    ),
    ModelConfig(
        "Gemini 2.5 Pro", "google", "gemini-2.5-pro",
        "GOOGLE_API_KEY", "More capable Google model",
    ),
    ModelConfig(
        "GPT-4o", "openai", "gpt-4o",
        "OPENAI_API_KEY", "OpenAI flagship model",
    ),
    ModelConfig(
        "GPT-4o Mini", "openai", "gpt-4o-mini",
        "OPENAI_API_KEY", "Faster · cheaper OpenAI model",
    ),
    ModelConfig(
        "Ollama (local)", "ollama", "",      # model_name chosen at runtime
        "", "Local model served by Ollama",
    ),
]

MODEL_LABELS: list[str] = [m.label for m in MODELS]
_BY_LABEL: dict[str, ModelConfig] = {m.label: m for m in MODELS}

OLLAMA_MODEL_OPTIONS: list[str] = [
    "qwen3:8b", "llama3.2", "llama3.1", "mistral", "phi4", "gemma3", "qwen2.5",
]

_PROVIDER_BASE_URLS: dict[str, str | None] = {
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openai": None,
    "ollama": os.environ.get("OLLAMA_BASE_URL", "http://localhost:30786/v1"),
}


def _wsl2_host_ip() -> str | None:
    """Return the Windows host IP visible from WSL2, or None if not in WSL2."""
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                if line.startswith("nameserver"):
                    ip = line.split()[1].strip()
                    # WSL2 nameserver is typically in the 172.x.x.x range
                    if ip.startswith("172."):
                        return ip
    except OSError:
        pass
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_model(provider: str, model_name: str) -> OpenAIChatCompletionsModel:
    """Return a ready-to-use model object for the given provider + model name."""
    from openai import AsyncOpenAI

    base_url = _PROVIDER_BASE_URLS.get(provider)
    key_env  = _BY_LABEL_by_provider(provider)
    api_key  = os.environ.get(key_env, "") if key_env else "ollama"

    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(**kwargs),
    )


def get_model_from_label(label: str, ollama_model: str = "llama3.2") -> OpenAIChatCompletionsModel:
    """Convenience wrapper used by the Streamlit UI."""
    cfg = _BY_LABEL.get(label)
    if cfg is None:
        raise ValueError(f"Unknown model label: {label!r}")
    model_name = ollama_model if cfg.provider == "ollama" else cfg.model_name
    return get_model(cfg.provider, model_name)


def provider_ready(label: str, ollama_model: str = "") -> tuple[bool, str]:
    """Return (is_ready, warning_message) for a model label."""
    cfg = _BY_LABEL.get(label)
    if cfg is None:
        return False, f"Unknown model: {label}"

    if cfg.provider == "ollama":
        return _check_ollama(ollama_model)

    if not cfg.key_env:
        return True, ""
    key = os.environ.get(cfg.key_env, "")
    if not key:
        return False, f"{cfg.key_env} is not set in environment"
    return True, ""


def _check_ollama(model_name: str = "") -> tuple[bool, str]:
    """Ping Ollama and optionally verify the requested model is loaded.

    Tries localhost first; if refused, retries with the WSL2 Windows-host IP
    (read from /etc/resolv.conf) and updates OLLAMA_BASE_URL for the session.
    """
    import requests as _req

    def _try(base_url: str) -> tuple[bool, str, bool]:
        """Returns (reachable, error_msg, model_ok)."""
        tags_url = base_url.rstrip("/").removesuffix("/v1") + "/api/tags"
        try:
            r = _req.get(tags_url, timeout=2)
            r.raise_for_status()
            if model_name:
                available = [m.get("name", "") for m in r.json().get("models", [])]
                if not any(model_name in n for n in available):
                    return True, f"Model '{model_name}' not found — run: ollama pull {model_name}", False
            return True, "", True
        except _req.exceptions.ConnectionError:
            return False, "", False
        except Exception as exc:
            return True, str(exc), False

    # 1. Try whatever is currently configured (default: localhost)
    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:30786/v1")
    reachable, msg, ok = _try(base)
    if reachable:
        return (True, "") if ok else (False, msg)

    # 2. Localhost refused — try the WSL2 Windows-host IP
    wsl_ip = _wsl2_host_ip()
    if wsl_ip:
        wsl_base = f"http://{wsl_ip}:30786/v1"
        reachable, msg, ok = _try(wsl_base)
        if reachable:
            # Persist for this session so get_model() also uses it
            os.environ["OLLAMA_BASE_URL"] = wsl_base
            _PROVIDER_BASE_URLS["ollama"] = wsl_base
            return (True, "") if ok else (False, msg)

    # 3. Both failed
    host = f"localhost or {wsl_ip}" if wsl_ip else "localhost"
    return False, (
        f"Ollama not reachable at {host}:30786. "
        "Check that the Ollama pod is running and the NodePort service is healthy "
        "(`kubectl get svc` / `kubectl get pods`). "
        "Override the URL with OLLAMA_BASE_URL in your .env if the address differs."
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _BY_LABEL_by_provider(provider: str) -> str:
    for m in MODELS:
        if m.provider == provider and m.key_env:
            return m.key_env
    return ""
