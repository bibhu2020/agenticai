from typing import TypedDict, List, Annotated
import operator

class WebSearchItem(TypedDict):
    query: str
    reason: str

class WebSearchPlan(TypedDict):
    searches: List[WebSearchItem]
    note: str

class AgentState(TypedDict):
    query: str
    report_format: str
    research_depth: str
    search_plan: WebSearchPlan
    search_results: Annotated[List[str], operator.add]
    final_report: str
