
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
mcp = FastMCP("MCP Web")

@mcp.tool()
def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for the given query using DuckDuckGo.
    Returns a list of results with title, url, snippet.
    """
    return search_web(query, max_results)

@mcp.tool()
def extract(url: str) -> str:
    """
    Extracts text content from a given URL.
    Useful for reading articles or documentation.
    """
    return extract_content(url)

@mcp.tool()
def research(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Research a topic by searching and extracting content in parallel.
    Returns search results populated with full content.
    """
    return research_topic(query, max_results)

@mcp.tool()
def wikipedia_search(query: str, max_results: int = 5) -> List[str]:
    """
    Search Wikipedia for the given query.
    Returns a list of page titles.
    """
    return search_wikipedia(query, max_results)

@mcp.tool()
def wikipedia_page(title: str) -> Dict[str, Any]:
    """
    Get the content of a Wikipedia page.
    Returns title, content, summary, url.
    """
    return get_wikipedia_page(title)

@mcp.tool()
def arxiv_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Arxiv for papers.
    Returns metadata including title, summary, authors, pdf_url.
    """
    return search_arxiv(query, max_results)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
