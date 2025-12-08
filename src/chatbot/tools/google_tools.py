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

    Features:
    - Search for recent web pages.
    - Limit number of results.
    - Returns formatted title, link, date, and snippet for each result.
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
            Formatted string of top search results, each including:
            - Title of the page
            - URL link
            - Published date
            - Snippet / description
            If no results are found or API key is missing, returns an error message.

        Example:
        --------
        search("AI in finance", num_results=2)

        Output:
        Title: How AI is Transforming Finance
        Link: https://example.com/ai-finance
        Published: 2024-06-15
        Snippet: AI is increasingly used for trading, risk management...
        
        Title: AI Applications in Banking
        Link: https://example.com/ai-banking
        Published: 2024-06-10
        Snippet: Banks are leveraging AI for customer service, fraud detection...
        """
        try:
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return "Missing SERPER_API_KEY in environment variables."

            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            payload = {"q": query, "num": num_results, "tbs": "qdr:d"}  # results from last 24h

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "organic" not in data or not data["organic"]:
                return "No results found."

            formatted_results = [
                f"Title: {item.get('title')}\n"
                f"Link: {item.get('link')}\n"
                f"Snippet: {item.get('snippet', '')}\n"
                for item in data["organic"][:num_results]
            ]
            return "\n".join(formatted_results)

        except requests.exceptions.RequestException as e:
            return f"Network error during Google search: {e}"
        except Exception as e:
            return f"Error performing Google search: {e}"


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
