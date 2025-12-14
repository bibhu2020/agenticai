import os
import requests

from agents import function_tool
from typing import Optional



# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------


# ============================================================
# 🔹 GOOGLE SEARCH TOOLSET (Serper.dev API)
# ============================================================

@function_tool
def google_search(query: str, num_results: int = 3) -> str:
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
        - Snippet / description
        If no results are found or API key is missing, returns an error message.

    Example:
    --------
    google_search("AI in finance", num_results=2)

    Output:
    Title: How AI is Transforming Finance
    Link: https://example.com/ai-finance
    Snippet: AI is increasingly used for trading, risk management...
    
    Title: AI Applications in Banking
    Link: https://example.com/ai-banking
    Snippet: Banks are leveraging AI for customer service, fraud detection...
    """
    print(f"[DEBUG] google_search called with query='{query}', num_results={num_results}")
    
    try:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY missing in environment variables."

        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": num_results, "tbs": "qdr:d"}  # results from last 24h

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "organic" not in data or not data["organic"]:
            return f"No results found for query: '{query}'"

        formatted_results = [
            f"Title: {item.get('title')}\n"
            f"Link: {item.get('link')}\n"
            f"Snippet: {item.get('snippet', '')}\n"
            for item in data["organic"][:num_results]
        ]
        return "\n".join(formatted_results)

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error during Google search: {e}")
        return f"Network error during Google search: {e}"
    except Exception as e:
        print(f"[DEBUG] Error performing Google search: {e}")
        return f"Error performing Google search: {e}"


@function_tool
def google_search_recent(query: str, num_results: int = 3, timeframe: str = "d") -> str:
    """
    Perform a Google search with time-based filtering using Serper.dev API.

    Parameters:
    -----------
    query : str
        The search query string.
    num_results : int, optional (default=3)
        Maximum number of search results to return.
    timeframe : str, optional (default="d")
        Time range for results:
        - "d" = past day
        - "w" = past week
        - "m" = past month
        - "y" = past year

    Returns:
    --------
    str
        Formatted string of recent search results.
    """
    print(f"[DEBUG] google_search_recent called with query='{query}', timeframe={timeframe}")
    
    try:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY missing in environment variables."

        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": num_results, "tbs": f"qdr:{timeframe}"}

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "organic" not in data or not data["organic"]:
            return f"No recent results found for query: '{query}'"

        formatted_results = [
            f"Title: {item.get('title')}\n"
            f"Link: {item.get('link')}\n"
            f"Snippet: {item.get('snippet', '')}\n"
            for item in data["organic"][:num_results]
        ]
        
        return f"Recent results ({timeframe}):\n\n" + "\n".join(formatted_results)

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error: {e}")
        return f"Network error during Google search: {e}"
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        return f"Error performing Google search: {e}"
