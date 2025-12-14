import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_ollama import ChatOllama
from huggingface_hub import login

class LangChainModelFactory:
    """
    Factory for creating LangChain compatible model instances.
    """

    @staticmethod
    def get_model(provider: str = "openai", # openai, azure, huggingface, ollama
                  model_name: str = "gpt-4o", 
                  temperature: float = 0
                  ):
        """
        Returns a LangChain LLM instance.
        """
        
        # ----------------------------------------------------------------------
        # AZURE
        # ----------------------------------------------------------------------
        if provider.lower() == "azure":
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            return AzureChatOpenAI(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                azure_deployment=os.environ["AZURE_OPENAI_API_BASE_MODEL"], # Or specific model_name if deployment matches
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                azure_ad_token_provider=token_provider,
                model_name=model_name,
                temperature=temperature,
            )
        
        # ----------------------------------------------------------------------
        # OPENAI
        # ----------------------------------------------------------------------
        elif provider.lower() == "openai":
            return ChatOpenAI(
                api_key=os.environ["OPENAI_API_KEY"],
                model_name=model_name,
                temperature=temperature,
            )
        
        # ----------------------------------------------------------------------
        # HUGGING FACE
        # ----------------------------------------------------------------------
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

        # ----------------------------------------------------------------------
        # OLLAMA
        # ----------------------------------------------------------------------
        elif provider.lower() == "ollama":
            return ChatOllama(model=model_name, temperature=temperature)
        
        else:
            raise ValueError(f"Unsupported LangChain provider: {provider}")
