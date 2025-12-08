from mcp.server.fastmcp import FastMCP
from toosl.google_tools import GoogleTools


mcp = FastMCP("search-server")

@mcp.tool()
async def google_search(query: str, num_results: int = 5) -> list[str]:
    """Perform a Google search and return the top results.

    Args:
        query: The search query
        num_results: The number of top results to return
    """
    tools = GoogleTools()
    results = await tools.google_search(query, num_results=num_results)
    return results

if __name__ == "__main__":
    print("Starting Search MCP server...")
    mcp.run(transport='stdio')