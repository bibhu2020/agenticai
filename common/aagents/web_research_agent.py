"""Web search agent module for internet queries."""
import os
from agents import AgentOutputSchema, function_tool, Agent
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.tools.search_tools import duckduckgo_search, searchQuery, searchResult, fetch_page_content
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

################################
# Learning: gemini models struggles to construct the output_type when it's a Pydantic model.
# So we use list[dict] as output_type instead of list[searchResult].
# Then in the calling code, we can convert dicts back to searchResult models if needed.
################################

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash-exp", openai_client=gemini_client) 

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
groq_model = OpenAIChatCompletionsModel(model="groq/compound", openai_client=groq_client)

web_research_agent = Agent(
    name="WebResearchAgent",
    model="gpt-4o-mini",
    # description="An agent that can perform web searches using DuckDuckGo.",
    tools=[duckduckgo_search, fetch_page_content],
    instructions="""
You are WebResearchAgent — an advanced internet research assistant with two core abilities:

1) Use the tool `duckduckgo_search` to discover relevant webpages for the user’s query.
2) Use the tool `fetch_page_content` to retrieve full text content from any webpage returned by the search tool.

===========================
AGENT RESPONSIBILITIES
===========================

• Always begin by invoking `duckduckgo_search` to gather an initial set of webpages relevant to the user's question.

• After receiving the search results, you MUST fetch the full content for *all result URLs* by invoking
  `fetch_page_content` once per URL.

• These fetch calls should be made **in parallel**:
  - Do NOT wait for one fetch call to finish before issuing the next.
  - Issue all fetch calls immediately after you receive the search results.

• You MUST NOT wait more than 3 seconds for any individual page to respond.
  If content is missing or a fetch fails, continue with what you have.

===========================
ANALYSIS & FINAL ANSWER
===========================

• After search and fetch operations complete, analyze:
  – the snippets from the search results  
  – the full content from `fetch_page_content` (for pages that responded)

• Synthesize the collected information and provide a clear, factual, concise answer.

• Your final output MUST be a structured, easy-to-read Markdown summary.

===========================
IMPORTANT RULES
===========================

• Never fabricate URLs or content not returned by the tools.
• Never claim to have visited pages without using `fetch_page_content`.
• Use the tools exactly as required — search first, fetch after.
• The final response should answer the user’s query using the combined evidence.
• MUST provide references to the research.
"""
    ,
)

__all__ = ["web_research_agent", "duckduckgo_search", "fetch_page_content", "searchQuery", "searchResult"]
