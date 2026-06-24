"""All research pipeline agents — Planner, Search, Writer, Guardrail, Email."""
import os
from typing import Dict

from agents import Agent, GuardrailFunctionOutput, Runner, function_tool, input_guardrail
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field

from model_factory import get_model


# ---------------------------------------------------------------------------
# Shared default model
# ---------------------------------------------------------------------------

def _default():
    return get_model("google", "gemini-2.5-flash")


# ---------------------------------------------------------------------------
# Guardrail
# ---------------------------------------------------------------------------

class _UnparliamentaryCheck(BaseModel):
    has_unparliamentary_language: bool
    explanation: str


def create_guardrail_agent(model=None):
    return Agent(
        name="Content Guardrail",
        instructions=(
            "Analyse the user input and decide whether it contains unparliamentary, "
            "offensive, or disrespectful language. "
            "Set has_unparliamentary_language=true and explain briefly if so; otherwise false."
        ),
        output_type=_UnparliamentaryCheck,
        model=model or _default(),
    )


def make_guardrail(model=None):
    _agent = create_guardrail_agent(model)

    @input_guardrail
    async def _check(ctx, agent, message: str):
        result = await Runner.run(_agent, message, context=ctx.context)
        triggered = result.final_output.has_unparliamentary_language
        return GuardrailFunctionOutput(
            output_info={"check": result.final_output.model_dump()},
            tripwire_triggered=triggered,
        )

    return _check


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

class WebSearchItem(BaseModel):
    reason: str = Field(description="Why this search matters for the query.")
    query:  str = Field(description="The exact search term to use.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="Ordered list of searches to perform.")
    note:     str                 = Field(default="", description="Optional status note.")


def create_planner_agent(model=None, guardrail=None, mcp_server=None):
    kwargs = {}
    if guardrail:
        kwargs["input_guardrails"] = [guardrail]
    if mcp_server:
        kwargs["mcp_servers"] = [mcp_server]
    return Agent(
        name="Planner",
        instructions=(
            "You are a research planner. Given a query, produce a precise set of web "
            "searches that will together answer it thoroughly. "
            "Call current_datetime first so searches can be temporally anchored."
        ),
        model=model or _default(),
        output_type=WebSearchPlan,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def create_search_agent(model=None, mcp_server=None):
    kwargs = {}
    if mcp_server:
        kwargs["mcp_servers"] = [mcp_server]
    return Agent(
        name="Search",
        instructions=(
            "You are a research assistant. Given a search term, use duckduckgo_search to "
            "find relevant results, then call fetch_page_content on the top 2–3 URLs to get "
            "full text. Produce a concise 5–6 paragraph summary (under 500 words). "
            "Capture the key facts and discard fluff. "
            "Do not add commentary beyond the summary itself."
        ),
        model=model or _default(),
        model_settings=ModelSettings(tool_choice="required"),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------

class ReportData(BaseModel):
    short_summary:       str        = Field(description="2–3 sentence executive summary.")
    markdown_report:     str        = Field(description="Full report in Markdown format.")
    follow_up_questions: list[str]  = Field(description="Suggested topics for further research.")


def create_writer_agent(model=None):
    return Agent(
        name="Writer",
        instructions=(
            "You are a senior researcher. Given an original query, search summaries, "
            "a requested report format, and a research depth level, produce a polished report.\n"
            "First outline the structure, then write the full report in Markdown. "
            "Adjust tone and length to the format and depth. "
            "Add tasteful emojis to section headers to improve readability."
        ),
        model=model or _default(),
        output_type=ReportData,
    )


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send the research report by email via SendGrid."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Content, Email, Mail, To

        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY", ""))
        mail = Mail(
            from_email=Email("bm80177@gmail.com"),
            to_emails=To("bibhup_mishra@yahoo.com"),
            subject=subject,
            html_content=Content("text/html", html_body),
        ).get()
        r = sg.client.mail.send.post(request_body=mail)
        return {"status": "sent", "code": str(r.status_code)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def create_email_agent(model=None):
    return Agent(
        name="Email",
        instructions=(
            "You can send a nicely formatted HTML email based on a detailed research report. "
            "Convert the report to clean, well-presented HTML with an appropriate subject line, "
            "then call send_email exactly once."
        ),
        tools=[send_email],
        model=model or _default(),
    )
