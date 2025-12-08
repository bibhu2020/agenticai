import os
from agents import Agent, OpenAIChatCompletionsModel, WebSearchTool
from openai import AsyncOpenAI

from agents.model_settings import ModelSettings
from tools.google_tools import GoogleTools

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
produce a concise summary of the results. The summary must 3-5 paragraphs and less than 500 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)

# search_agent = Agent(
#     name="Search agent",
#     instructions=INSTRUCTIONS,
#     tools=[WebSearchTool(search_context_size="low")],
#     # tools=[GoogleTools.search],
#     model="gpt-4o-mini",
#     model_settings=ModelSettings(tool_choice="required"),
# )

# -----------------------------
# CONNECT TO MCP SERVER
# -----------------------------
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

# # Note: Gemini does not like 
# search_agent = Agent(
#     name="Search agent",
#     instructions=INSTRUCTIONS,
#     # tools=[WebSearchTool(search_context_size="low")],
#     tools=[GoogleTools.search],
#     model=gemini_model,
#     model_settings=ModelSettings(tool_choice="required"),
# )


search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    # tools=[WebSearchTool(search_context_size="low")],
    tools=[GoogleTools.search],
    model=gemini_model,
    model_settings=ModelSettings(tool_choice="required"),
)

