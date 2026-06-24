"""Deep Research Orchestrator — plans, searches, and writes a comprehensive report."""
import asyncio
import logging
import sys
from pathlib import Path

from agents import Runner, SQLiteSession, trace, gen_trace_id
from agents.exceptions import InputGuardrailTripwireTriggered
from agents.mcp import MCPServerManager, MCPServerStdio, MCPServerStdioParams

from research_agents import (
    WebSearchItem, WebSearchPlan, ReportData,
    create_planner_agent, create_search_agent,
    create_writer_agent, create_email_agent, make_guardrail,
)

_MCPDIR = Path(__file__).resolve().parent.parent / "_mcpservers"

log = logging.getLogger(__name__)

_DEPTH_SEARCHES = {"Quick": 5, "Standard": 10, "Deep": 15}


class Orchestrator:
    """Coordinates the research pipeline and streams status updates to the caller."""

    def __init__(self, model, session: SQLiteSession | None = None):
        self.model   = model
        self.session = session or SQLiteSession()

        self._mcp = MCPServerStdio(
            params=MCPServerStdioParams(
                command=sys.executable,
                args=[str(_MCPDIR / "mcp-web-search" / "server.py")],
            ),
            cache_tools_list=True,
            name="web-search-mcp",
        )

        guardrail            = make_guardrail(model)
        self.planner_agent   = create_planner_agent(model, guardrail=guardrail, mcp_server=self._mcp)
        self.search_agent    = create_search_agent(model, mcp_server=self._mcp)
        self.writer_agent    = create_writer_agent(model)
        self.email_agent     = create_email_agent(model)

    async def run(
        self, query: str,
        report_format: str = "Academic",
        research_depth: str = "Standard",
    ):
        """Async generator that yields status strings, then the final markdown report."""
        num_searches = _DEPTH_SEARCHES.get(research_depth, 10)

        async with MCPServerManager([self._mcp]):
            with trace("Deep Research", trace_id=gen_trace_id()):
                # Plan
                yield f"Planning {num_searches} searches…"
                search_plan = await self._plan(query, num_searches)

                if not search_plan.searches:
                    yield search_plan.note or "No searches could be planned."
                    return

                # Search
                yield f"Running {len(search_plan.searches)} searches (depth: {research_depth})…"
                results = await self._search_all(search_plan)
                yield f"Searches complete ({len(results)} results). Writing report…"

                # Write
                report = await self._write(query, results, report_format, research_depth)
                yield report.markdown_report

    # ------------------------------------------------------------------

    async def _plan(self, query: str, num_searches: int) -> WebSearchPlan:
        try:
            result = await Runner.run(
                self.planner_agent,
                f"Query: {query}\nGenerate exactly {num_searches} search terms.",
                session=self.session,
            )
            return result.final_output_as(WebSearchPlan)
        except InputGuardrailTripwireTriggered:
            return WebSearchPlan(
                searches=[],
                note="⚠️ Your query was blocked by the content policy. Please rephrase.",
            )
        except Exception as exc:
            log.error("Planning failed: %s", exc)
            return WebSearchPlan(searches=[], note=f"Planning error: {exc}")

    async def _search_all(self, plan: WebSearchPlan) -> list[str]:
        tasks = [asyncio.create_task(self._search_one(item)) for item in plan.searches]
        results = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                results.append(result)
        return results

    async def _search_one(self, item: WebSearchItem) -> str | None:
        try:
            result = await Runner.run(
                self.search_agent,
                f"Search term: {item.query}\nReason: {item.reason}",
            )
            return str(result.final_output)
        except Exception as exc:
            log.warning("Search failed for '%s': %s", item.query, exc)
            return None

    async def _write(
        self, query: str, results: list[str],
        report_format: str, research_depth: str,
    ) -> ReportData:
        result = await Runner.run(
            self.writer_agent,
            (
                f"Original query: {query}\n"
                f"Report Format: {report_format}\n"
                f"Research Depth: {research_depth}\n"
                f"Search summaries:\n{results}"
            ),
        )
        return result.final_output_as(ReportData)
