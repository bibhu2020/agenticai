
"""
Parallel research tool.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from .search import search_web
from .extract import extract_content

def research_topic(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Research a topic by searching and extracting content in parallel.
    """
    try:
        results = search_web(query, max_results)
        urls = [r['url'] for r in results]
        
        with ThreadPoolExecutor(max_workers=max_results) as executor:
            contents = list(executor.map(extract_content, urls))
            
        for i, content in enumerate(contents):
            results[i]['content'] = content
            
        return results
    except Exception as e:
        return [{"error": str(e)}]
