from llm import get_llm

def get_model_client(provider: str = "google"):
    _MODELS = {
        "google": "gemini-2.0-flash",
        "openai": "gpt-4o-mini",
    }
    if provider.lower() not in _MODELS:
        raise ValueError(f"Unsupported provider: {provider}")
    return get_llm(provider=provider.lower(), model=_MODELS[provider.lower()])

