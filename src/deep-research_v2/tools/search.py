import os
import requests
from langchain_core.tools import tool

@tool
def google_search(query: str) -> str:
    """
    Perform a general Google search using Serper.dev API.
    Returns the top 3 results with titles, links, and snippets.
    """
    try:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "❌ Missing SERPER_API_KEY environment variable."

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 3
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        organic_results = data.get("organic", [])
        if not organic_results:
            return "No search results found."

        formatted = []
        for item in organic_results:
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            snippet = item.get("snippet", "")
            formatted.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
        
        return "\n".join(formatted)

    except Exception as e:
        return f"⚠️ Error performing Google search: {e}"
