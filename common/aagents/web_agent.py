"""Web search agent module for internet queries."""
import os
from agents import AgentOutputSchema, function_tool, Agent
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.tools.search_tools import duckduckgo_search, searchQuery, searchResult
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

web_agent = Agent(
    name="WebAgent",
    model="gpt-4o-mini",
    # description="An agent that can perform web searches using DuckDuckGo.",
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
