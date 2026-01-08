import os
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.language_models import BaseChatModel

class CognitionLayer:
    """
    The Brain (LLM) configuration for LangGraph agents.
    """
    
    @staticmethod
    def get_model(model_name: str = "gpt-4o", provider: str = "openai") -> BaseChatModel:
        """
        Returns a configured LangChain Chat Model.
        """
        provider = provider.lower()
        if provider == "openai":
            return ChatOpenAI(model=model_name, temperature=0)
            
        elif provider == "azure":
             return AzureChatOpenAI(
                 deployment_name=model_name,
                 api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
                 azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                 api_key=os.getenv("AZURE_OPENAI_API_KEY")
             )
             
        elif provider == "huggingface":
            # Using OpenAI compatible client in LangChain
            return ChatOpenAI(
                model=model_name,
                openai_api_key=os.getenv("HF_TOKEN"),
                openai_api_base=f"https://router.huggingface.co/models/{model_name}/v1",
                temperature=0
            )

        elif provider in ["ollama", "local"]:
             return ChatOpenAI(
                 model=model_name,
                 openai_api_key="ollama",
                 openai_api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                 temperature=0
             )
             
        # Default
        return ChatOpenAI(model=model_name)
