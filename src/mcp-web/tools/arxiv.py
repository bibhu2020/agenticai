
"""
Arxiv Tool
"""
import arxiv

def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """
    Search Arxiv for papers.
    Returns: List of metadata.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in search.results():
            results.append({
                "title": result.title,
                "summary": result.summary,
                "authors": [a.name for a in result.authors],
                "url": result.pdf_url,
                "published": str(result.published)
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
