"""AI Research Orchestrator — fans out to specialist agents and synthesises results."""
import asyncio

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStdio

from content_guardrail import create_guardrail, enforce_content_policy
from specialists import (
    create_finance_agent, create_news_agent, create_web_agent,
    finance_agent, news_agent, web_agent,
)
from model_factory import get_model

_INSTRUCTIONS = """
You are the **AI Research Orchestrator** — the central intelligence that coordinates
three specialist agents and delivers polished, multi-source answers.

## Specialist Roster
| Agent | Best for |
|---|---|
| Financial Markets Analyst | Stock prices, market sentiment, analyst ratings, earnings, IV, sector screening |
| News Intelligence Specialist | Breaking news, recent events, headlines by topic or category |
| Web Research Specialist | General knowledge, history, facts, how-to, research |

## Workflow
1. **Understand** the user's intent.
2. **Select** only the specialists needed — set unused agents to `false` in
   `broadcast_to_specialists` to reduce latency.
3. **Call** `broadcast_to_specialists` with the user's query.
4. **Synthesise** the reports into one clear, structured response.

## Response Templates
- **Finance query** → Financial Snapshot table + Key Developments + Synthesis
- **News query** → Executive Summary + numbered headlines with sources
- **Research query** → Answer with cited evidence + Sources section
- **General chat** → Conversational markdown (bullet points, bold highlights)
- **Code request** → Fenced code blocks + step-by-step explanation

## Constraints
- For any query that needs live data, ALWAYS call `broadcast_to_specialists`.
- Finance and News specialists automatically fall back to Web Research if they fail.
- If all specialist reports return errors, tell the user clearly and suggest retrying.
"""


def _make_broadcast_tool(finance_a, news_a, web_a):
    @function_tool
    async def broadcast_to_specialists(
        query: str,
        include_finance: bool = True,
        include_news: bool = True,
        include_web_search: bool = True,
    ) -> str:
        """
        Fan out the query to selected specialist agents in parallel and merge reports.
        Finance and News specialists automatically fall back to Web Research on failure.

        Args:
            query: The user's question or research topic.
            include_finance: Query the Financial Markets Analyst (default True).
            include_news: Query the News Intelligence Specialist (default True).
            include_web_search: Query the Web Research Specialist (default True).
        """
        active: list[tuple[str, object]] = []
        if include_finance:
            active.append(("Financial Markets Analyst", Runner.run(finance_a, query)))
        if include_news:
            active.append(("News Intelligence Specialist", Runner.run(news_a, query)))
        if include_web_search:
            active.append(("Web Research Specialist", Runner.run(web_a, query)))

        if not active:
            return "No specialist agents were selected for this query."

        names      = [name for name, _ in active]
        coroutines = [coro for _, coro in active]
        results    = list(await asyncio.gather(*coroutines, return_exceptions=True))

        # Web fallback for failed Finance / News specialists
        fallback_indices = [
            i for i, (name, res) in enumerate(zip(names, results))
            if isinstance(res, Exception) and name != "Web Research Specialist"
        ]
        if fallback_indices:
            fallbacks = await asyncio.gather(
                *[Runner.run(web_a, query) for _ in fallback_indices],
                return_exceptions=True,
            )
            for i, fb in zip(fallback_indices, fallbacks):
                results[i] = fb
                names[i]   = f"{names[i]} → Web Fallback"

        sections = [
            f"✅ {name} Report:\n{res.final_output}"
            if not isinstance(res, Exception)
            else f"❌ {name} — Error: {res}"
            for name, res in zip(names, results)
        ]

        return (
            "\n--- SPECIALIST REPORTS BEGIN ---\n\n"
            + "\n\n---\n\n".join(sections)
            + "\n\n--- SPECIALIST REPORTS END ---"
        )

    return broadcast_to_specialists


def create_orchestrator(m=None) -> tuple[Agent, list[MCPServerStdio]]:
    """Return (orchestrator, [mcp_servers]).  Caller manages server lifecycle."""
    _model = m or get_model("google", "gemini-2.5-flash")
    _finance, _finance_mcp = create_finance_agent(_model)
    _news,    _news_mcp    = create_news_agent(_model)
    _web,     _web_mcp     = create_web_agent(_model)
    _, _guardrail = create_guardrail(_model)

    orchestrator = Agent(
        name="AI Research Orchestrator",
        model=_model,
        tools=[_make_broadcast_tool(_finance, _news, _web)],
        input_guardrails=[_guardrail],
        instructions=_INSTRUCTIONS,
    )
    orchestrator.description = (
        "Coordinates the Financial Markets Analyst, News Intelligence Specialist, and "
        "Web Research Specialist to deliver comprehensive, multi-source answers."
    )
    return orchestrator, [_finance_mcp, _news_mcp, _web_mcp]


# ---------------------------------------------------------------------------
# Module-level defaults (backwards compat / tests)
# ---------------------------------------------------------------------------

broadcast_to_specialists = _make_broadcast_tool(finance_agent, news_agent, web_agent)

ai_research_orchestrator = Agent(
    name="AI Research Orchestrator",
    model=get_model("google", "gemini-2.5-flash"),
    tools=[broadcast_to_specialists],
    input_guardrails=[enforce_content_policy],
    instructions=_INSTRUCTIONS,
)
ai_research_orchestrator.description = (
    "Coordinates the Financial Markets Analyst, News Intelligence Specialist, and "
    "Web Research Specialist to deliver comprehensive, multi-source answers."
)
