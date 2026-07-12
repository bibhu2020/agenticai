"""LLM factory for the news agent — Claude models via OpenRouter's OpenAI-compatible API."""
from __future__ import annotations
import os
from langchain_openai import ChatOpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_llm(model: str = "anthropic/claude-haiku-4.5", temperature: float = 0, max_tokens: int = 4096) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
    )
