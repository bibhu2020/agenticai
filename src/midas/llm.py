"""LLM factory for Midas — returns an AutoGen OpenAIChatCompletionClient.

Supported providers:
  openai  — GPT models                           (OPENAI_API_KEY)
  google  — Gemini via OpenAI-compat endpoint    (GOOGLE_API_KEY)
  groq    — Groq-hosted models                   (GROQ_API_KEY)
  azure   — Azure OpenAI via managed identity    (AZURE_OPENAI_API_URI, AZURE_OPENAI_API_VERSION)
  ollama  — Local Ollama server                  (no key)
"""
from __future__ import annotations

import os


def get_llm(
    provider: str = "google",
    model: str = "gemini-2.0-flash",
    temperature: float = 0,
    model_info: dict | None = None,
):
    """Return a configured AutoGen model client for the given provider."""
    try:
        from autogen_ext.models.openai import OpenAIChatCompletionClient
    except ImportError as exc:
        raise ImportError("autogen-ext[openai] is required for Midas.") from exc

    if provider == "openai":
        return OpenAIChatCompletionClient(
            model=model,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            temperature=temperature,
        )

    if provider in ("google", "gemini"):
        info = model_info or {
            "family": "gemini",
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
        }
        return OpenAIChatCompletionClient(
            model=model,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.environ.get("GOOGLE_API_KEY", ""),
            model_info=info,
            temperature=temperature,
            max_tokens=2048,
            structured_output=False,
        )

    if provider == "groq":
        info = model_info or {
            "family": "llama",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": False,
        }
        return OpenAIChatCompletionClient(
            model=model,
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY", ""),
            model_info=info,
            temperature=temperature,
            structured_output=False,
            max_tokens=2048,
        )

    if provider == "azure":
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        return OpenAIChatCompletionClient(
            model=model,
            azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_ad_token_provider=token_provider,
            temperature=temperature,
        )

    if provider == "ollama":
        return OpenAIChatCompletionClient(
            model=model,
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",
            model_info=model_info or {},
            temperature=temperature,
        )

    raise ValueError(f"Unsupported provider: {provider!r}. Choose openai | google | groq | azure | ollama.")
