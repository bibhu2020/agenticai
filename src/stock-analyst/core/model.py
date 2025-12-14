from common.utility.autogen_model_factory import AutoGenModelFactory

def get_model_client(provider:str = "google"):
    if provider.lower() == "google":
        return AutoGenModelFactory.get_model(
            provider="google",
            model_name="gemini-3-pro-preview",
            temperature=0,
        model_info={
            "family": "gemini",
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
        },
    )
    elif provider.lower() == "openai":
        return AutoGenModelFactory.get_model(
            provider="openai",
            model_name="gpt-4o-mini",
            temperature=0,
        model_info={
            "family": "gpt",
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
        },
    )
    else: 
        raise  ValueError(f"Unsupported provider: {provider}")

