"""LLM factory for FIFA — returns a LangChain Gemini model."""
from __future__ import annotations
import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(model: str = "gemini-2.5-flash", temperature: float = 0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        temperature=temperature,
        max_tokens=2048,
    )
