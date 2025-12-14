import requests
from ddgs import DDGS
from agents import function_tool

from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from typing import Optional



# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------


# ---------------------- MODELS ---------------------------
class searchQuery(BaseModel):
    query: str = Field(..., description="The search query string.")
    max_results: int = Field(5, description="The maximum number of search results to return.")
    search_type: str = Field(
        "text",
        description="Search type: 'text' (default) or 'news'. Use 'news' to get publication dates."
    )
    timelimit: str = Field(
        'd',
        description="Time limit for search results: 'd' (day), 'w' (week), 'm' (month), 'y' (year)."
    )
    region: str = Field("us-en", description="Region for search results (e.g., 'us-en').")


class searchResult(BaseModel):
    title: str
    link: str
    snippet: str
    datetime: Optional[str] = None


# ---------------------- PAGE FETCH TOOL ---------------------------
def _fetch_page_content(url: str, timeout: int = 3) -> Optional[str]:
    """Fetch and extract text content from a web page."""
    print(f"[DEBUG] fetch_page_content called with: {url} - timeout: {timeout}")
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove irrelevant elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        print(f"[WARNING] Failed to fetch content from {url}: {str(e)}")
        return None


@function_tool
def fetch_page_content(url: str, timeout: int = 3) -> Optional[str]:
    """Fetch and extract text content from a web page."""
    return _fetch_page_content(url, timeout)


# ---------------------- SEARCH TOOL ---------------------------
def _duckduckgo_search(params: searchQuery) -> list[dict]:
    """Perform a DuckDuckGo search and return only snippets.  
    No page content fetched here."""
    print(f"[DEBUG] duckduckgo_search called with: {params}")

    results = []
    with DDGS() as ddgs:
        if params.search_type == "news":
            search_results = ddgs.news(
                params.query,
                max_results=params.max_results,
                timelimit=params.timelimit,
                region=params.region
            )
            for result in search_results:
                results.append(
                    searchResult(
                        title=result.get("title", ""),
                        link=result.get("url", ""),
                        snippet=result.get("body", ""),
                        datetime=result.get("date", "")
                    ).model_dump()
                )
        else:
            search_results = ddgs.text(
                params.query,
                max_results=params.max_results,
                timelimit=params.timelimit,
                region=params.region
            )
            for result in search_results:
                results.append(
                    searchResult(
                        title=result.get("title", ""),
                        link=result.get("href", ""),
                        snippet=result.get("body", "")
                    ).model_dump()
                )

    print(f"[DEBUG] duckduckgo_search returning {len(results)} results")
    return results

@function_tool
def duckduckgo_search(params: searchQuery) -> list[dict]:
    """Perform a DuckDuckGo search and return only snippets.  
    No page content fetched here."""
    return _duckduckgo_search(params)

