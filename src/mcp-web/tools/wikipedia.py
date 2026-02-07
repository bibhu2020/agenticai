
"""
Wikipedia Tool
"""
import wikipedia

def search_wikipedia(query: str, max_results: int = 5) -> list[str]:
    """
    Search Wikipedia for the given query.
    Returns: A list of result titles.
    """
    try:
        results = wikipedia.search(query, results=max_results)
        return results
    except Exception as e:
        return [f"Error: {str(e)}"]

def get_wikipedia_page(title: str) -> dict:
    """
    Get the content of a Wikipedia page.
    Returns: A dictionary with title, content, summary, url.
    """
    try:
        page = wikipedia.page(title)
        return {
            "title": page.title,
            "content": page.content,
            "summary": page.summary,
            "url": page.url
        }
    except Exception as e:
        return {"error": str(e)}
