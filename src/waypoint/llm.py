"""LLM factory for Waypoint — returns a Phidata model instance.

Supported providers:
  openai  — GPT models via phi.model.openai  (OPENAI_API_KEY)
  google  — Gemini via phi.model.google      (GOOGLE_API_KEY)
"""
from __future__ import annotations

import os


def get_llm(provider: str = "openai", model: str = "gpt-4o-mini"):
    """Return a configured Phidata model for the given provider."""
    if provider == "openai":
        from phi.model.openai import OpenAIChat
        return OpenAIChat(
            id=model,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

    if provider == "google":
        from phi.model.google import Gemini
        return Gemini(
            id=model,
            api_key=os.environ.get("GOOGLE_API_KEY", ""),
        )

    raise ValueError(f"Unsupported provider: {provider!r}. Choose openai | google.")
