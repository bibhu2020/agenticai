import os
import requests
from dotenv import load_dotenv
from agents import function_tool
from core.logger import log_call

# Load environment variables once
load_dotenv()


# ============================================================
# 🔹 GOOGLE SEARCH TOOLSET (Serper.dev API)
# ============================================================
class GoogleTools:
    """
    GoogleTools provides function tools to perform web searches
    using the Serper.dev API (Google Search). I am a fallback for
    retrieving recent information from the web.
    """

    @staticmethod
    @function_tool
    @log_call
    def search(query: str, num_results: int = 3) -> str:
        """
        Perform a general Google search using Serper.dev API.

        Parameters:
        -----------
        query : str
            The search query string, e.g., "latest Tesla stock news".
        num_results : int, optional (default=3)
            Maximum number of search results to return.

        Returns:
        --------
        str
            Nicely formatted search results.
        """
        try:
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return "❌ Missing SERPER_API_KEY in environment variables."

            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "gl": "us",   # country code (optional)
                "hl": "en",   # language code (optional)
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            organic_results = data.get("organic", [])
            if not organic_results:
                return "No search results found."

            formatted = []
            for item in organic_results[:num_results]:
                title = item.get("title", "No title")
                link = item.get("link", "No link")
                snippet = item.get("snippet", "")
                formatted.append(
                    f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n"
                )
                # print(formatted[-1])  # Log each result

            return "\n".join(formatted)

        except requests.exceptions.RequestException as e:
            return f"⚠️ Network error during Google search: {e}"
        except Exception as e:
            return f"⚠️ Error performing Google search: {e}"


# ============================================================
# 🔹 OPENAI & OTHER MODEL TOOLS
# ============================================================
class ModelTools:
    """
    ModelTools provides function tools to interact with LLM APIs
    such as OpenAI, Gemini, or Groq. 

    Features:
    - Send prompts to a language model.
    - Receive structured text completions.
    - Can be extended to support multiple LLM providers.
    """

    @staticmethod
    @function_tool
    def query_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
        """
        Query an OpenAI language model with a prompt.

        Parameters:
        -----------
        prompt : str
            User-provided prompt for the model.
        model : str, optional (default="gpt-4o-mini")
            Model name to query (e.g., "gpt-4o-mini", "gpt-4").

        Returns:
        --------
        str
            Model's response content as text.
            If an error occurs (network/API), returns an error message.

        Example:
        --------
        query_openai("Explain AI in finance")

        Output:
        "AI in finance refers to the use of machine learning and natural language
        processing techniques to automate trading, risk assessment, and customer service..."
        """
        try:
            from openai import OpenAI  # delayed import
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying OpenAI API: {e}"
