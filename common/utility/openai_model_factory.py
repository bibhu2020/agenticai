import os
import tiktoken
from typing import Union
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI, AsyncAzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from huggingface_hub import login

class OpenAIModelFactory:
    """
    Factory for creating OpenAI-SDK compatible model instances (using the 'agents' library).
    Supports multiple providers via the OpenAI-compatible API format.
    """

    @staticmethod
    def get_model(provider: str = "openai", # openai, azure, google, groq, ollama
                  model_name: str = "gpt-4o", 
                  temperature: float = 0
                  ) -> OpenAIChatCompletionsModel:
        """
        Returns an OpenAIChatCompletionsModel instance.
        """
        
        # ----------------------------------------------------------------------
        # AZURE OPENAI
        # ----------------------------------------------------------------------
        if provider.lower() == "azure":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            client = AsyncAzureOpenAI(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                azure_ad_token_provider=token_provider,
            )
            return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

        # ----------------------------------------------------------------------
        # STANDARD OPENAI
        # ----------------------------------------------------------------------
        elif provider.lower() == "openai":
            client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
            return OpenAIChatCompletionsModel(model=model_name, openai_client=client)
            
        # ----------------------------------------------------------------------
        # GOOGLE (GEMINI) via OpenAI Compat
        # ----------------------------------------------------------------------
        elif provider.lower() == "google" or provider.lower() == "gemini":
            GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
            client = AsyncOpenAI(
                base_url=GEMINI_BASE_URL,
                api_key=os.environ["GOOGLE_API_KEY"]
            )
            return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

        # ----------------------------------------------------------------------
        # GROQ via OpenAI Compat
        # ----------------------------------------------------------------------
        elif provider.lower() == "groq":
            GROQ_BASE_URL = "https://api.groq.com/openai/v1"
            client = AsyncOpenAI(
                base_url=GROQ_BASE_URL,
                api_key=os.environ["GROQ_API_KEY"]
            )
            return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

        # ----------------------------------------------------------------------
        # OLLAMA via OpenAI Compat
        # ----------------------------------------------------------------------
        elif provider.lower() == "ollama":
            client = AsyncOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

        # ----------------------------------------------------------------------
        # UNSUPPORTED
        # ----------------------------------------------------------------------
        else:
            raise ValueError(f"Unsupported provider for OpenAIModelFactory: {provider}")


    @staticmethod
    def num_tokens_from_messages(messages, model: str = "gpt-4o"):
        """
        Return the number of tokens used by a list of messages.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3
        num_tokens = 0

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if key == "name":
                    num_tokens += 1
                
                # Encode values if they are strings
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                elif isinstance(value, list) and key == "content":
                    for part in value:
                        if isinstance(part, dict) and part.get("type") == "text":
                                num_tokens += len(encoding.encode(part.get("text", "")))
                        elif isinstance(part, dict) and part.get("type") == "image_url":
                                num_tokens += 85 

        num_tokens += 3 
        return num_tokens


class EmbeddingFactory:
    """
    A static utility class to create and return Embedding Model instances.
    """

    @staticmethod
    def get_embedding_model(provider: str = "openai",
                            model_name: str = "text-embedding-3-small"
                            ) -> Union[AzureOpenAIEmbeddings, OpenAIEmbeddings, OllamaEmbeddings, HuggingFaceEmbeddings]:
        
        if provider.lower() == "azure":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            return AzureOpenAIEmbeddings(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", model_name),
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                azure_ad_token_provider=token_provider,
            )
        elif provider.lower() == "openai":
            return OpenAIEmbeddings(
                api_key=os.environ["OPENAI_API_KEY"],
                model=model_name
            )
        elif provider.lower() == "ollama":
            return OllamaEmbeddings(model=model_name)
        elif provider.lower() == "huggingface":
            if os.environ.get("HF_TOKEN"):
                login(token=os.environ.get("HF_TOKEN"))
            return HuggingFaceEmbeddings(model_name=model_name)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")


# =================================================================================================
# GLOBAL HELPER FUNCTIONS
# =================================================================================================

def get_model(provider:str = "openai", model_name:str = "gpt-4o"):
    """
    Global helper to get an OpenAI-SDK compatible model.
    Defaults to OpenAI provider and gpt-4o.
    """
    return OpenAIModelFactory.get_model(
        provider=provider,
        model_name=model_name,
        temperature=0
    )

def get_model_json(model_name: str = "gpt-4o-2024-08-06", provider: str = "openai"):
    """
    Global helper to get a JSON-capable model (Structured Outputs).
    Defaults to gpt-4o-2024-08-06 on OpenAI.
    """
    return OpenAIModelFactory.get_model(
        provider=provider,
        model_name=model_name,
        temperature=0
    )
