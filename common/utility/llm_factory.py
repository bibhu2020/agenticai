import os
import tiktoken
from typing import Any
from langchain_openai.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings, OpenAIEmbeddings
from azure.identity import DefaultAzureCredential
from huggingface_hub import login
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_groq import ChatGroq
# from langchain_openai import OpenAIEmbeddings

class LLMFactory:
    """
    Factory class to provide LLM and embedding model instances for different providers.
    """

    @staticmethod
    def get_llm(provider: str, **kwargs) -> Any:
        """
        Returns a chat/completion LLM instance based on the provider.
        Supported providers: openai, azureopenai, huggingface, ollama, groq
        """
        if provider == "openai":
            # OpenAI Chat Model
            return ChatOpenAI(
                openai_api_key=kwargs.get("api_key", os.environ.get("OPENAI_API_KEY")),
                model_name=kwargs.get("model_name", "gpt-4")
            )

        elif provider == "azureopenai":
            # Azure OpenAI Chat Model using Azure Identity for token
            credential = DefaultAzureCredential()
            token = credential.get_token("https://cognitiveservices.azure.com/.default").token
            if not token:
                raise ValueError("Token is required for AzureChatOpenAI.")
            return AzureChatOpenAI(
                azure_endpoint=kwargs["endpoint"],
                azure_deployment=kwargs.get("deployment_name", "gpt-4"),
                api_version=kwargs["api_version"],
                api_key=token
            )

        # pip install langchain langchain-huggingface huggingface_hub
        elif provider == "huggingface":
            # If using a private model or endpoint, authenticate
            login(token=kwargs.get("api_key", os.environ.get("HF_TOKEN")))  

            return ChatHuggingFace(
                repo_id=kwargs.get("model_name", "mistralai/Mistral-Nemo-Instruct-2407"),  # Or any other chat-friendly model
                task="text-generation",
                model_kwargs={
                    "temperature": 0.7,
                    "max_new_tokens": 256
                }
            )

        elif provider == "ollama":
            # Ollama local model
            return ChatOllama(
                model=kwargs.get("model_name", "gemma:2b"),
                temperature=0
            )

        elif provider == "groq":
            # Groq LLM
            return ChatGroq(
                model=kwargs.get("model_name", "Gemma2-9b-It"),
                max_tokens=512,
                api_key=kwargs.get("api_key", os.environ.get("GROQ_API_KEY"))
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def get_embedding_model(provider: str, **kwargs) -> Any:
        """
        Returns an embedding model instance based on the provider.
        Supported providers: openai, huggingface
        """
        if provider == "openai":
            return OpenAIEmbeddings(
                model=kwargs.get("model_name", "text-embedding-3-large"),
                openai_api_key=kwargs.get("api_key", os.environ.get("OPENAI_API_KEY"))
            )
        if provider == "azureopenai":
            # Get the Azure Credential
            credential = DefaultAzureCredential()
            token=credential.get_token("https://cognitiveservices.azure.com/.default").token

            if not token:
                raise ValueError("Token is required for AzureOpenAIEmbeddings.")
            return AzureOpenAIEmbeddings(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                azure_deployment=kwargs.get("azure_deployment", "text-embedding-3-large"), 
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                api_key=token
            )
        elif provider == "huggingface":
            # If using a private model or endpoint, authenticate
            login(token=kwargs.get("api_key", os.environ.get("HF_TOKEN")))  

            return HuggingFaceEmbeddings(
                model_name=kwargs.get("model_name", "all-MiniLM-L6-v2")
            )
        elif provider == "groq":
            raise ValueError(f"No embedding support from the provider: {provider}")
        elif provider == "ollama":
            return OllamaEmbeddings(model=kwargs.get("model_name", "gemma:2b")) 
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

    @staticmethod
    def num_tokens_from_messages(messages) -> int:
        """
        Return the number of tokens used by a list of messages.
        Adapted from the OpenAI cookbook token counter.
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens_per_message = 3  # <|start|>, role, <|end|>
        num_tokens = 0

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))

        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens