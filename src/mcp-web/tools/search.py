
"""
Search tool using DuckDuckGo
"""
from duckduckgo_search import DDGS
from typing import List, Dict, Any

def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for the given query.
    Returns a list of results with title, href, body.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # DuckDuckGo search returns a generator
            ddgs_gen = ddgs.text(query, max_results=max_results)
            for r in ddgs_gen:
                results.append({
                    "title": r.get('title'),
                    "url": r.get('href'),
                    "snippet": r.get('body'),
                    "source": "DuckDuckGo"
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]
