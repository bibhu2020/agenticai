import os
from pydantic import BaseModel, Field
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from tools.time_tools import TimeTools
from appagents.guardrail_agent import guardrail_against_unparliamentary

HOW_MANY_SEARCHES = 10

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.  \
Use the tool to find current date & time, and use it where relevant to inform your search and summary."


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")
    current_date_time: str = Field(description="Current date and time.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key)
groq_model = OpenAIChatCompletionsModel(model="groq/compound", openai_client=groq_client)

openai_model = "gpt-4.1-mini"

# Note: Many models do not like tool call and json output_schema used together.

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model=openai_model,
    tools=[TimeTools.current_datetime],
    output_type=WebSearchPlan,
    input_guardrails=[guardrail_against_unparliamentary],
)