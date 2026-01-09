import os
from pathlib import Path
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load .env
# current: notebooks/architecture_v4/layers/config.py
# root: ../../../
root_path = Path(__file__).resolve().parents[3]
load_dotenv(root_path / ".env")

def get_model_client(model_name="gpt-4o", provider="openai"):
    """
    Returns the OpenAIChatCompletionClient for AutoGen agents.
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    elif provider == "azure":
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            model_capabilities={
                "json_output": True,
                "function_calling": True,
                "vision": False,
            },
        )
    # Fallback to OpenAI standard
    return OpenAIChatCompletionClient(
        model=model_name,
        api_key=os.getenv("OPENAI_API_KEY")
    )
