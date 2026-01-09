import os
from pydantic import BaseModel, Field
from agents import Agent
from tools.time_tools import TimeTools
from appagents.guardrail_agent import guardrail_against_unparliamentary
from core.model import get_model_client

INSTRUCTIONS = "You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. \
Use the tool to find current date & time, and use it where relevant to inform your search and summary."


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")
    current_date_time: str = Field(description="Current date and time.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

openai_model = get_model_client()

# Note: Many models do not like tool call and json output_schema used together.

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model=openai_model,
    tools=[TimeTools.current_datetime],
    output_type=WebSearchPlan,
    input_guardrails=[guardrail_against_unparliamentary],
)