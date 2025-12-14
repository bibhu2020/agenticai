from common.utility.openai_model_factory  import OpenAIModelFactory

def get_model_client(provider:str = "openai"):
    if provider.lower() == "google":
        return OpenAIModelFactory.get_model(
            provider="google",
            model_name="gemini-2.5-flash",
            temperature=0
    )
    elif provider.lower() == "openai":
        return OpenAIModelFactory.get_model(
            provider="openai",
            model_name="gpt-4.1-mini",
            temperature=0
    )
    elif provider.lower() == "azure":
        return OpenAIModelFactory.get_model(
            provider="azure",
            model_name="gpt-4o-mini",
            temperature=0
    )
    elif provider.lower() == "groq":
        return OpenAIModelFactory.get_model(
            provider="groq",
            model_name="gpt-4o-mini",
            temperature=0
    )
    elif provider.lower() == "ollama":
        return OpenAIModelFactory.get_model(
            provider="ollama",
            model_name="gpt-4o-mini",
            temperature=0
    )
    else: 
        raise  ValueError(f"Unsupported provider: {provider}")

