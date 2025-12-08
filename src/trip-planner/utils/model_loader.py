import os
from dotenv import load_dotenv
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from azure.identity import AzureCliCredential, ManagedIdentityCredential

# Load .env file
load_dotenv()

class ConfigLoader:
    def __init__(self):
        print("Loading config...")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader:
    def __init__(self, model_provider: str = "azureopenai"):
        
        print(f"Initializing ModelLoader with provider: {model_provider}")
        self.model_provider = model_provider.lower()
        self.config = ConfigLoader()

    def load_llm(self):
        self.model_provider = "openai"
        print(f"LLM loading from provider: {self.model_provider}")

        if self.model_provider == "groq":
            print("→ Using Groq")
            groq_api_key = os.getenv("GROQ_API_KEY")
            print(f"Groq API Key: {groq_api_key}")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")
            model_name = self.config["llm"]["groq"]["model_name"]
            return ChatGroq(model=model_name, api_key=groq_api_key)

        elif self.model_provider == "openai":
            print("→ Using OpenAI")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            model_name = self.config["llm"]["openai"]["model_name"]
            return ChatOpenAI(model_name=model_name, api_key=openai_api_key)

        elif self.model_provider == "azureopenai":
            print("→ Using Azure OpenAI")
            client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
            if client_id and len(client_id) > 1: 
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = AzureCliCredential()
            
            token = credential.get_token("https://cognitiveservices.azure.com/.default").token
            if not token:
                raise ValueError("Azure token could not be retrieved.")
            return AzureChatOpenAI(
                azure_endpoint=self.config["llm"]["azureopenai"]["endpoint"],
                azure_deployment=self.config["llm"]["azureopenai"]["model_name"],
                api_version=self.config["llm"]["azureopenai"]["api_version"],
                api_key=token
            )

        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    
