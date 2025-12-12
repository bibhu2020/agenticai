from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

def get_model_client(model="gemini-flash-latest", temperature=0):
    return OpenAIChatCompletionClient(
        model=model,
        model_info={
            "family": "gemini",
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
        },
        api_key=gemini_api_key,
        temperature=temperature
    )
