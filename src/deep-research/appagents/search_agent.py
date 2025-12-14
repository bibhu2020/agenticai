import os
from agents import Agent
from tools.google_tools import GoogleTools
from core.model import get_model_client
from common.utility.logger import log_call
from agents.model_settings import ModelSettings

# INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
# produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
# words. Capture the main points. Write succintly, no need to have complete sentences or good \
# grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
# essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

# INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web and produce a detailed synthesis of the results. \
# The output must be structured into sections, one for each search result provided by the tool. \
# For each result, you MUST include the full link/URL and the title. \
# Your response should capture the main points and relevant details from all sources. \
# Do not add any personal commentary, introductions, or conclusions. \
# Format the entire output as a single, detailed block of text in markdown format, ensuring ALL source links are visible and preserved."

INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 5-6 paragraphs and less than 500 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."


# -----------------------------
# CONNECT TO MCP SERVER
# -----------------------------
@log_call
async def setup_mcp_tools():
    """
    Starts the MCP server via stdio and returns its list of tools
    that can be attached to the agent.
    """
    # Absolute path ensures the script is found even from a notebook
    import os
    script_path = os.path.abspath("../mcp/search-server.py")

    params = {
        "command": "uvx",  # or "uv" depending on your environment
        "args": ["run", script_path],
    }

    # Start MCP server and list available tools
    async with MCPServerStdio(
        params=params,
        client_session_timeout_seconds=60,
        verbose=True,  # helpful for debugging
    ) as server:
        mcp_tools = await server.list_tools()
        print(f"✅ Connected to MCP server with {len(mcp_tools)} tool(s).")
        return mcp_tools

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    # tools=[WebSearchTool(search_context_size="low")],
    tools=[GoogleTools.search],
    model=get_model_client(),
    model_settings=ModelSettings(tool_choice="required"),
)

