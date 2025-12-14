import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

class AutoGenModelFactory:
    """
    Factory for creating AutoGen compatible model instances.
    """

    @staticmethod
    def get_model(provider: str = "azure", # azure, openai, google, groq, ollama
                  model_name: str = "gpt-4o", 
                  temperature: float = 0,
                  model_info: dict = None
                  ):
        """
        Returns an AutoGen OpenAIChatCompletionClient instance.
        """
        
        # Lazy import to avoid dependency issues if autogen is not installed
        try:
            from autogen_ext.models.openai import OpenAIChatCompletionClient
        except ImportError as e:
            raise ImportError("AutoGen libraries (autogen-agentchat, autogen-ext[openai]) are not installed.") from e

        # ----------------------------------------------------------------------
        # AZURE
        # ----------------------------------------------------------------------
        if provider.lower() == "azure":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            return OpenAIChatCompletionClient(
                model=model_name,
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                azure_ad_token_provider=token_provider,
                temperature=temperature,
            )

        # ----------------------------------------------------------------------
        # OPENAI
        # ----------------------------------------------------------------------
        elif provider.lower() == "openai":
            return OpenAIChatCompletionClient(
                model=model_name,
                api_key=os.environ["OPENAI_API_KEY"],
                temperature=temperature,
            )
        
        # ----------------------------------------------------------------------
        # GOOGLE (GEMINI) via OpenAI Compat
        # ----------------------------------------------------------------------
        elif provider.lower() == "google" or provider.lower() == "gemini":
            return OpenAIChatCompletionClient(
                model=model_name,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.environ["GOOGLE_API_KEY"],
                model_info=model_info, # Pass full model_info for capabilities
                temperature=temperature,
            )

        # ----------------------------------------------------------------------
        # GROQ
        # ----------------------------------------------------------------------
        elif provider.lower() == "groq":
            return OpenAIChatCompletionClient(
                model=model_name,
                base_url="https://api.groq.com/openai/v1",
                api_key=os.environ["GROQ_API_KEY"],
                temperature=temperature,
            )
        
        # ----------------------------------------------------------------------
        # OLLAMA
        # ----------------------------------------------------------------------
        elif provider.lower() == "ollama":
            # Ensure model_info defaults to empty dict if None
            info = model_info if model_info is not None else {}
            return OpenAIChatCompletionClient(
                model=model_name,
                base_url="http://localhost:11434/v1",
                api_key="ollama", # dummy key
                model_info=info,
                temperature=temperature,
            )
        
        else:
            raise ValueError(f"Unsupported AutoGen provider: {provider}")
