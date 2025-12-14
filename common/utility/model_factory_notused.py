import os
import tiktoken
from typing import Union
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI, ChatOpenAI, AzureOpenAIEmbeddings, OpenAIEmbeddings
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI, AsyncAzureOpenAI
from huggingface_hub import login
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings


class ModelFactory:
    """
    A static utility class to create and return LLM instances based on the input type.
    """

    @staticmethod
    def get_model(framework: str = "openai-sdk-agent", # openai-sdk-agent, langchain, autogen
                  provider: str = "openai", # openai, azure, google, groq, huggingface, ollama
                  model_name: str = "gpt-4o-mini", # gpt-4o-mini, gemini-flash-1.5, groq/compound
                  model_info: dict = None, # additional info (e.g. backend provider for autogen/langchain)
                  temperature: float = 0
                  ) -> Union[AzureChatOpenAI, ChatOpenAI, OpenAIChatCompletionsModel, ChatHuggingFace, ChatOllama]:
        """
        Returns an LLM instance based on the specified parameters.

        Parameters:
            framework (str): The framework to use ('langchain', 'openai-sdk-agent', 'autogen').
            provider (str): The model provider ('openai', 'azure', 'google', 'groq', 'huggingface', 'ollama').
            model_name (str): The specific model name.
            model_info (dict): Additional model info.
            temperature (float): The temperature for generation (default 0).

        Returns:
            Union[...]: The model instance.
        """
        
        # ----------------------------------------------------------------------
        # AUTOGEN SUPPORT
        # ----------------------------------------------------------------------
        if framework.lower() == "autogen":
            # Lazy import to avoid dependency issues if autogen is not installed
            try:
                from autogen_ext.models.openai import OpenAIChatCompletionClient
            except ImportError as e:
                raise ImportError("AutoGen libraries (autogen-agentchat, autogen-ext[openai]) are not installed.") from e

            # Azure Backend
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

            # OpenAI Backend
            elif provider.lower() == "openai":
                return OpenAIChatCompletionClient(
                    model=model_name,
                    api_key=os.environ["OPENAI_API_KEY"],
                    temperature=temperature,
                )
            
            # Google Backend (Gemini via OpenAI compat)
            elif provider.lower() == "google" or provider.lower() == "gemini":
                return OpenAIChatCompletionClient(
                    model=model_name,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=os.environ["GOOGLE_API_KEY"],
                    model_info=model_info, # Pass full model_info for capabilities
                    temperature=temperature,
                )

            # Groq Backend
            elif provider.lower() == "groq":
                return OpenAIChatCompletionClient(
                    model=model_name,
                    base_url="https://api.groq.com/openai/v1",
                    api_key=os.environ["GROQ_API_KEY"],
                    temperature=temperature,
                )
            
            # Ollama Backend
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

        # ----------------------------------------------------------------------
        # LANGCHAIN SUPPORT
        # ----------------------------------------------------------------------
        elif framework.lower() == "langchain":
            
            if provider.lower() == "azure":
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
                )
                return AzureChatOpenAI(
                    azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                    azure_deployment=os.environ["AZURE_OPENAI_API_BASE_MODEL"],
                    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                    azure_ad_token_provider=token_provider,
                    model_name=model_name,
                    temperature=temperature,
                )
            
            elif provider.lower() == "openai":
                return ChatOpenAI(
                    api_key=os.environ["OPENAI_API_KEY"],
                    model_name=model_name,
                    temperature=temperature,
                )
            
            elif provider.lower() == "huggingface":
                if os.environ.get("HF_TOKEN"):
                    login(token=os.environ.get("HF_TOKEN"))
                llm = HuggingFaceEndpoint(
                    repo_id=model_name,
                    task="text-generation",
                    temperature=temperature,
                    max_new_tokens=512,
                    huggingfacehub_api_token=os.environ.get("HF_TOKEN")
                )
                return ChatHuggingFace(llm=llm)

            elif provider.lower() == "ollama":
                return ChatOllama(model=model_name, temperature=temperature)
            
            else:
                raise ValueError(f"Unsupported LangChain provider: {provider}")
        
        # ----------------------------------------------------------------------
        # STANDARD LOGIC (Agents Lib / OpenAI SDK)
        # ----------------------------------------------------------------------
        elif framework.lower() == "openai-sdk-agent" or framework.lower() == "openai-sdk" or framework.lower() == "openai":
        
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

            elif provider.lower() == "openai":
                client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
                return OpenAIChatCompletionsModel(model=model_name, openai_client=client)
                
            elif provider.lower() == "google":
                GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
                client = AsyncOpenAI(
                    base_url=GEMINI_BASE_URL,
                    api_key=os.environ["GOOGLE_API_KEY"]
                )
                return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

            elif provider.lower() == "groq":
                GROQ_BASE_URL = "https://api.groq.com/openai/v1"
                client = AsyncOpenAI(
                    base_url=GROQ_BASE_URL,
                    api_key=os.environ["GROQ_API_KEY"]
                )
                return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

            elif provider.lower() == "ollama":
                client = AsyncOpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"
                )
                return OpenAIChatCompletionsModel(model=model_name, openai_client=client)

            elif provider.lower() == "huggingface":
                 # Agents lib doesn't have native HF support in the same way
                 raise ValueError("For Hugging Face, please use framework='langchain'")

            else:
                raise ValueError(f"Unsupported provider for openai-sdk-agent: {provider}")

        else:
             raise ValueError(f"Unsupported framework: {framework}")


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
# GLOBAL HELPER FUNCTIONS (for agents)
# =================================================================================================

# model used for orchestrator or executor
# def get_model(provider:str = "google", framework:str = "openai-sdk", model_name:str = "gemini-2.5-flash"):
def get_model(provider:str = "openai", framework:str = "openai", model_name:str = "gpt-4-turbo"):
# def get_model(provider:str = "groq", framework:str = "openai-sdk", model_name:str = "openai/gpt-oss-120b"):
    model_info = None
    if provider in list["gemini", "google"]:
        model_info = {
            "family": "gemini",
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
        }
    
    return ModelFactory.get_model(  framework=framework,
                                    provider=provider,
                                    model_name=model_name,
                                    model_info=model_info,
                                    temperature=0)
    # else:
    #     return ModelFactory.get_model(  framework="openai-sdk", 
    #                                 provider="openai",
    #                                 model_name="gpt-4o-mini",
    #                                 temperature=0)

# Use this model where agent executing tool and returning JSON
def get_model_json(model_name: str = "gpt-4.1-mini", provider: str = "openai"):
    return ModelFactory.get_model(  framework="openai-sdk",
                                    provider=provider,
                                    model_name=model_name, 
                                    temperature=0)
