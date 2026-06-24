"""LLM factory for Remedy — returns a LangChain chat model.

Supported providers:
  openai  — GPT models via langchain-openai      (OPENAI_API_KEY)
  google  — Gemini via langchain-google-genai     (GOOGLE_API_KEY)
  groq    — Groq-hosted models via langchain-groq (GROQ_API_KEY)
"""
from __future__ import annotations

import os
from langchain_core.language_models.chat_models import BaseChatModel


def get_llm(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    temperature: float = 0,
) -> BaseChatModel:
    """Return a configured LangChain chat model for the given provider."""
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        )

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        )

    raise ValueError(f"Unsupported provider: {provider!r}. Choose openai | google | groq.")
