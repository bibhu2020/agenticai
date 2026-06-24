"""Healthcare RAG Agent — LangGraph graph combining FAISS RAG with DuckDuckGo web search."""
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from tools.rag_tool import rag_search

_SYSTEM_PROMPT = """\
You are a healthcare information retrieval assistant. Use only the results returned by your tools — never your pre-trained knowledge.

## Workflow (MANDATORY for every question)

1. Call `rag_search` first with the user's question.
2. Evaluate the result:
   - Useful medical information → synthesise and format it.
   - "No relevant information found" or only references/page numbers → call `duckduckgo_search`.
3. Synthesise tool results into a clear, well-structured Markdown response.
4. If both tools fail, say "I don't have information on this topic."

## Response format

## [Topic Name]
[Brief introduction]

### Key Points
- **Point**: Description

### Detailed Information
[Organised paragraphs with medical details]

---
**Source:** Knowledge Base / Web Search
**Disclaimer:** For educational purposes only. Always consult a qualified healthcare professional.
"""

_web_search = DuckDuckGoSearchRun(name="duckduckgo_search")
_tools = [rag_search, _web_search]
_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(_tools)


def _call_agent(state: MessagesState):
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]
    return {"messages": [_llm.invoke(messages)]}


_builder = StateGraph(MessagesState)
_builder.add_node("agent", _call_agent)
_builder.add_node("tools", ToolNode(_tools))
_builder.add_edge(START, "agent")
_builder.add_conditional_edges("agent", tools_condition)
_builder.add_edge("tools", "agent")

healthcare_graph = _builder.compile()

__all__ = ["healthcare_graph"]
