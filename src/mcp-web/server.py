
"""
MCP Web Server using FastMCP
"""
import sys
import os

# Add src to pythonpath so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Union
from core.mcp_telemetry import log_usage, log_trace, log_metric
import uuid
import time

# Local imports
try:
    from .tools.search import search_web
    from .tools.extract import extract_content
    from .tools.research import research_topic
    from .tools.wikipedia import search_wikipedia, get_wikipedia_page
    from .tools.arxiv import search_arxiv
except ImportError:
    # Fallback if run directly
    try:
        from tools.search import search_web
        from tools.extract import extract_content
        from tools.research import research_topic
        from tools.wikipedia import search_wikipedia, get_wikipedia_page
        from tools.arxiv import search_arxiv
    except ImportError:
         # Fallback if tools are relative to this file but not package
        sys.path.append(os.path.join(current_dir, "tools"))
        from search import search_web
        from extract import extract_content
        from research import research_topic
        from wikipedia import search_wikipedia, get_wikipedia_page
        from arxiv import search_arxiv

# Initialize FastMCP Server
mcp = FastMCP("MCP Web", host="0.0.0.0")

@mcp.tool()
def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for the given query using DuckDuckGo.
    Returns a list of results with title, url, snippet.
    """
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    log_usage("mcp-web", "search")
    
    try:
        results = search_web(query, max_results)
        duration = (time.time() - start_time) * 1000
        log_trace("mcp-web", trace_id, span_id, "search", duration, "ok")
        log_metric("mcp-web", "search_results_count", len(results), {"query": query})
        return results
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_trace("mcp-web", trace_id, span_id, "search", duration, "error")
        raise e

@mcp.tool()
def extract(url: str) -> str:
    """
    Extracts text content from a given URL.
    Useful for reading articles or documentation.
    """
    log_usage("mcp-web", "extract")
    return extract_content(url)

@mcp.tool()
def research(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Research a topic by searching and extracting content in parallel.
    Returns search results populated with full content.
    """
    log_usage("mcp-web", "research")
    return research_topic(query, max_results)

@mcp.tool()
def wikipedia_search(query: str, max_results: int = 5) -> List[str]:
    """
    Search Wikipedia for the given query.
    Returns a list of page titles.
    """
    log_usage("mcp-web", "wikipedia_search")
    return search_wikipedia(query, max_results)

@mcp.tool()
def wikipedia_page(title: str) -> Dict[str, Any]:
    """
    Get the content of a Wikipedia page.
    Returns title, content, summary, url.
    """
    log_usage("mcp-web", "wikipedia_page")
    return get_wikipedia_page(title)

@mcp.tool()
def arxiv_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Arxiv for papers.
    Returns metadata including title, summary, authors, pdf_url.
    """
    log_usage("mcp-web", "arxiv_search")
    return search_arxiv(query, max_results)

if __name__ == "__main__":
    # Run the MCP server
    import os
    if os.environ.get("MCP_TRANSPORT") == "sse":
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)
    else:
        mcp.run()
