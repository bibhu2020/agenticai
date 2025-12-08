import os
import requests
from typing import Dict, Any
from agents import function_tool
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

@function_tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for healthcare information using SerpAPI or DuckDuckGo."""
    print(f"[DEBUG] WEB_SEARCH called with query: '{query}'")
    
    # api_key = os.getenv("SERPER_API_KEY")
    # if api_key:
    #     print("[DEBUG] WEB_SEARCH: Using SerpAPI")
    #     # Example: SerpAPI
    #     url = "https://serpapi.com/search.json"
    #     params = {"q": query, "api_key": api_key, "engine": "google"}
    #     r = requests.get(url, params=params, timeout=10)
    #     data = r.json()
    #     # choose top organic results and snippet
    #     results = []
    #     for item in data.get("organic_results", [])[:5]:
    #         results.append({"title": item.get("title"), "snippet": item.get("snippet"), "link": item.get("link")})
    #     print(f"[DEBUG] WEB_SEARCH: SerpAPI returned {len(results)} results")
    #     return {"source": "serpapi", "query": query, "results": results}
    
    print("[DEBUG] WEB_SEARCH: Using DuckDuckGo fallback")
    # fallback to simple DuckDuckGo Instant Answer
    r = requests.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"}, timeout=10)
    data = r.json()
    abstract = data.get("AbstractText")
    results = []
    if abstract:
        results.append({"title": "DuckDuckGo Abstract", "snippet": abstract, "link": data.get("AbstractURL")})
        print(f"[DEBUG] WEB_SEARCH: DuckDuckGo returned abstract")
    else:
        print("[DEBUG] WEB_SEARCH: DuckDuckGo returned no results")
    return {"source": "duckduckgo", "query": query, "results": results}