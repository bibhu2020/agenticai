import os
from typing import Any, Union
from agents import OpenAIChatCompletionsModel

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI
except ImportError:
    pass # Handle if openai raw lib not installed, though agents depends on it.

class ModelFactory:
    """
    Factory to create Agent Model objects for different providers.
    """
    
    @staticmethod
    def get_model(provider: str, model_name: str) -> Union[str, Any]:
        """
        Returns a model configuration for the Agents SDK.
        
        Args:
            provider: "openai", "azure", "ollama", "deepseek", etc.
            model_name: The internal model ID (e.g. "gpt-4o", "llama3").
        """
        provider = provider.lower()
        
        if provider == "openai":
            return model_name
            
        elif provider == "azure":
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
            
            if not api_key or not endpoint:
                raise ValueError("Azure configuration missing.")
                
            client = AsyncAzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            
            return OpenAIChatCompletionsModel(
                openai_client=client,
                model=model_name
            )
            
        elif provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY missing.")
            
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            
            return OpenAIChatCompletionsModel(
                openai_client=client,
                model=model_name
            )

        elif provider == "huggingface":
            # Hugging Face Generic OpenAI-Compatible Router
            # Trying generic root: https://router.huggingface.co/v1/
            # The model ID is passed in the request body.
            base_url = "https://router.huggingface.co/v1/"
            api_key = os.getenv("HF_TOKEN")
            
            if not api_key:
                raise ValueError("HF_TOKEN required.")
                
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # The model name in the payload is often ignored by HF if URL is specific,
            # or it should match the URL. We pass it anyway.
            return OpenAIChatCompletionsModel(
                openai_client=client,
                model=model_name
            )

        elif provider in ["ollama", "local"]:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            
            client = AsyncOpenAI(
                base_url=base_url,
                api_key="ollama"
            )
            
            return OpenAIChatCompletionsModel(
                openai_client=client,
                model=model_name
            )
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
