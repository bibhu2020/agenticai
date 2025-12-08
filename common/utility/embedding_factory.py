import os
from typing import Union
from azure.identity import DefaultAzureCredential
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingFactory:
    """
    A static utility class to create and return LLM Embedding instances based on the input type.
    """

    @staticmethod
    def get_llm(llm_type: str) -> Union[AzureOpenAIEmbeddings, OpenAIEmbeddings]:
        """
        Returns an LLM instance based on the specified type.

        Parameters:
            llm_type (str): The type of LLM to return. Valid values are 'azure' or 'openai'.

        Returns:
            Union[AzureOpenAIEmbeddings, OpenAIEmbeddings]: The LLM instance.
        """
        if llm_type.lower() == "azure":
            # Get the Azure Credential
            credential = DefaultAzureCredential()
            token=credential.get_token("https://cognitiveservices.azure.com/.default").token

            if not token:
                raise ValueError("Token is required for AzureOpenAIEmbeddings.")
            return AzureOpenAIEmbeddings(
                azure_endpoint=os.environ["AZURE_OPENAI_API_URI"],
                azure_deployment="text-embedding-3-small", #os.environ["AZURE_OPENAI_API_BASE_MODEL"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                api_key=token
            )
        elif llm_type.lower() == "openai":
            return OpenAIEmbeddings(
                api_key=os.environ["OPENAI_API_KEY"],
                model="text-embedding-3-large"
            )
        elif llm_type.lower() == "ollama": # must have ollama running locally with the following model
            return OllamaEmbeddings(model="gemma:2b") 
        elif llm_type.lower() == "hf": # must have key update in env:HF_TOKEN
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            raise ValueError("Invalid llm_type. Use 'azure' or 'openai'.")