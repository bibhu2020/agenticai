import os
from pydantic import BaseModel, Field
from agents import Agent
from core.model import get_model_client

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, some initial research done by a research assistant, "
    "and a requested Report Format and Research Depth.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format. "
    "Adjust the tone, structure, and length based on the requested Report Format and Research Depth. "
    "Make the output colorful and add minimal emojis to make the content appealing and aesthetic."
)


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=get_model_client(),
    output_type=ReportData,
)