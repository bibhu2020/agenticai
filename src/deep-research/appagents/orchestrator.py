from agents import Runner, trace, gen_trace_id, SQLiteSession
from appagents.search_agent import search_agent
from appagents.planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from appagents.writer_agent import writer_agent, ReportData
from appagents.email_agent import email_agent
from agents.exceptions import InputGuardrailTripwireTriggered
from core.logger import log_call
import asyncio

class Orchestrator:

    def __init__(self, session: SQLiteSession | None = None):
        self.session = session or SQLiteSession()

    @log_call
    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Deep Research Orchestrator", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)

            if not search_plan or not getattr(search_plan, "searches", []):
                note = getattr(search_plan, "note", "")
                if "unparliamentary" in note.lower():
                    print("⚠️ Guardrail triggered – unparliamentary language detected.")
                    yield note
                else:
                    yield note or "No search results found, ending research."
                    return
            
            yield "Searches planned, starting to search..."     
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."
            # await self.send_email(report)
            # yield "Email sent, research complete"
            yield report.markdown_report
        
    @log_call
    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Plan the searches to perform for the query."""
        print("Planning searches...")

        try:
            result = await Runner.run(
                planner_agent,              # use self. unless global
                f"Query: {query}",
                session=self.session,
            )

            print(f"Will perform {len(result.final_output.searches)} searches")
            return result.final_output_as(WebSearchPlan)

        except InputGuardrailTripwireTriggered as e:
            explanation = getattr(e, "result", {}).get("output_info", {}).get(
                "found_unparliamentary_word", {}
            ).get("explanation", "")
            print("⚠️ Guardrail triggered – unparliamentary language detected.")
            return WebSearchPlan(searches=[], note=f"Blocked due to unparliamentary input. {explanation}")

        except Exception as e:
            print(f"❌ Error during planning: {e}")
            return WebSearchPlan(searches=[], note="An error occurred while planning searches.")

    @log_call
    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    @log_call
    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    @log_call
    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    @log_call
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return report