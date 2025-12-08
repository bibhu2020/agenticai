import os
from pydantic import BaseModel, Field
from agents import Agent, OpenAIChatCompletionsModel, WebSearchTool
from openai import AsyncOpenAI

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)


# writer_agent = Agent(
#     name="WriterAgent",
#     instructions=INSTRUCTIONS,
#     model="gpt-5-mini",
#     output_type=ReportData,
# )

writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=gemini_model,
    output_type=ReportData,
)