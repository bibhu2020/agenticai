
import os
import asyncio
from common.aagents.search_agent import search_agent
from common.aagents.news_agent import news_agent
from common.aagents.yf_agent import yf_agent
from aagents.input_validation_agent import input_validation_guardrail
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from openai import AsyncOpenAI
from core.model import get_model_client

# ----------------------------------------------------------
# PARALLEL EXECUTION TOOL
# ----------------------------------------------------------
@function_tool
async def prompt_broadcaster(query: str, include_finance: bool = True, include_news: bool = True, include_search: bool = True) -> str:
    """
    Broadcasts the search query to selected specialized agents in parallel and aggregates their responses.
    
    Args:
        query: The user's question or topic to research.
        include_finance: Whether to include the Yahoo Finance agent (default: True).
        include_news: Whether to include the News agent (default: True).
        include_search: Whether to include the Web Search agent (default: True).

    Returns:
        Combined reports from the selected agents.
    """
    
    
    # A better approach for variable tasks is to map them.
    active_agents = []
    if include_finance: active_agents.append(("YahooFinanceAgent", Runner.run(yf_agent, query)))
    if include_news: active_agents.append(("NewsAgent", Runner.run(news_agent, query)))
    if include_search: active_agents.append(("WebSearchAgent", Runner.run(search_agent, query)))

    if not active_agents:
        return "No agents were selected for this query."

    # Run in parallel
    agent_names = [name for name, _ in active_agents]
    coroutines = [coro for _, coro in active_agents]
    
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    
    outputs = []
    for name, res in zip(agent_names, results):
        if isinstance(res, Exception):
            outputs.append(f"❌ {name} Error: {str(res)}")
        else:
            outputs.append(f"✅ {name} Report:\n{res.final_output}")
            
    combined_response = "\n--- START OF AGENT REPORTS ---\n\n" + "\n\n-----------------------------------\n\n".join(outputs) + "\n\n--- END OF AGENT REPORTS ---"
    
    return combined_response

orchestrator_agent = Agent(
    name="AI Chat Orchestrator",
    tools=[prompt_broadcaster],
    instructions="""
    You are the **AI Chat Orchestrator**. 
    Your goal is to provide a comprehensive, multi-perspective answer by synthesizing data from specialized sub-agents.

    **Workflow**:
    1.  **Analyze Request**: Understand the user's question.
    2.  **Determine Needs**: Decide which specialized agents are required.
        *   **Finance**: For stock prices, market trends, company financials, or analyst ratings.
        *   **News**: For recent events, headlines, or breaking news.
        *   **Web Search**: For general knowledge, history, facts, or broad research.
    3.  **Broadcast Query**: Call the `prompt_broadcaster` tool with the `query` and set the `include_*` flags to True/False accordingly.
        *   *Optimization Tip*: efficiently select ONLY the necessary agents to reduce latency.
    4.  **Synthesize Results**: Read the returned "Agent Reports".
        *   Combine the financial data (prices, sentiment), news headlines, and general search context.
        *   Compare and contrast findings if necessary.
        *   Resolve conflicts by prioritizing specific data (e.g., Yahoo Finance for prices) over general text.
    5.  **Final Response**: Generate a clear, professional, and well-structured summary for the user. Do not simply paste the individual reports.

    **Final Response Structure**:
    You should adapt the response structure based on the user's query type:

    *   **For Market/Finance Queries**: Use the "Market Analysis" style with a Financial Snapshot (Price, Sentinel, Ratings), Key Developments, and Synthesis.
    *   **For News/Research**: Use a clear "Executive Summary" followed by "Key Findings" and "Details".
    *   **For General Chat**: Maintain a conversational but professional tone. Use markdown for clarity (bullet points, bold text).
    *   **For Coding Requests**: Provide clear code blocks and explanations.

    **Constraint**:
    *   Do NOT try to answer based on your own knowledge if live data is needed/requested.
    *   Use `prompt_broadcaster` when the query implies a need for external information.
    *   If agents return "No data", explicitly state that in the relevant section.
    """,
    model=get_model_client(),
)
orchestrator_agent.description = "An intelligent orchestrator that queries Finance, News, and Search agents in parallel and synthesizes a comprehensive response."


__all__ = ["orchestrator_agent"]
