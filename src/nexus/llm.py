"""LLM factory for Nexus — returns OpenAIChatCompletionsModel (OpenAI Agents SDK).

Supported providers:
  openai  — GPT models          (OPENAI_API_KEY)
  google  — Gemini models       (GOOGLE_API_KEY)
  groq    — Groq-hosted models  (GROQ_API_KEY)
  ollama  — Local Ollama server (no key; OLLAMA_BASE_URL overrides default)
"""
from __future__ import annotations

import os

from agents import OpenAIChatCompletionsModel

_BASE_URLS: dict[str, str | None] = {
    "openai": None,
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "groq":   "https://api.groq.com/openai/v1",
    "ollama": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
}

_API_KEY_ENVS: dict[str, str | None] = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq":   "GROQ_API_KEY",
    "ollama": None,
}


def get_llm(
    provider: str = "google",
    model: str = "gemini-2.5-flash",
) -> OpenAIChatCompletionsModel:
    """Return a configured LLM for the given provider and model name."""
    from openai import AsyncOpenAI

    base_url = _BASE_URLS.get(provider)
    key_env  = _API_KEY_ENVS.get(provider)
    api_key  = os.environ.get(key_env, "") if key_env else "ollama"

    client_kwargs: dict = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=AsyncOpenAI(**client_kwargs),
    )
