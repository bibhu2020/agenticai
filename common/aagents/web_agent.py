"""Web search agent module for internet queries."""
from agents import Agent
from common.mcp.tools.search_tools import duckduckgo_search, searchQuery, searchResult
from .core.model import get_model_client
    
web_agent = Agent(
    name="WebAgent",
    model=get_model_client(),
    tools=[duckduckgo_search],
    instructions="""
        You are a WebAgent that can perform web searches to find information on the internet. 
        When given a query, use the 'duckduckgo_search' tool to retrieve relevant search results. 
        Tool: duckduckgo_search Input: 
        A JSON object with the following structure: 
            {   "query": "The search query string.", 
                "max_results": "The maximum number of search results to return (default is 5).", 
                "search_type": "The type of search to perform. Options: 'text' (default) or 'news'. Use 'news' to get publication dates.", 
                "timelimit": "Time limit for search results. Options: 'd' (day), 'w' (week), 'm' (month), 'y' (year).", 
                "region": "Region for search results (e.g., 'us-en', 'uk-en'). Default is 'wt-wt' (world)." 
            }
        """,
    # output_type=AgentOutputSchema(list[searchResult], strict_json_schema=False),
    # output_type=list[dict],  # safer than list[searchResult],    
    output_type=list[searchResult],
)

__all__ = ["web_agent", "duckduckgo_search", "searchQuery", "searchResult"]
