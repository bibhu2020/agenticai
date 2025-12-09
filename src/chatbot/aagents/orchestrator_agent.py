
import os
import asyncio
from common.aagents.search_agent import search_agent
from common.aagents.news_agent import news_agent
from common.aagents.yf_agent import yf_agent
from aagents.input_validation_agent import input_validation_guardrail
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Model setup ---
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=gemini_client
)

# ----------------------------------------------------------
# PARALLEL EXECUTION TOOL
# ----------------------------------------------------------
@function_tool
async def broadcast_research(query: str) -> str:
    """
    Broadcasts the search query to multiple specialized agents (Finance, News, Web Search) 
    in parallel and aggregates their responses.

    Args:
        query: The user's question or topic to research.

    Returns:
        Combined reports from all agents.
    """
    print(f"[DEBUG] broadcast_research called with query='{query}'")
    
    # Define tasks for parallel execution
    # We use a new Runner.run call for each agent. 
    # Note: We are not passing a session to keep them stateless/independent for this query.
    
    task_yf = Runner.run(yf_agent, query)
    task_news = Runner.run(news_agent, query)
    task_search = Runner.run(search_agent, query)
    
    # Run all in parallel
    results = await asyncio.gather(task_yf, task_news, task_search, return_exceptions=True)
    
    yf_res, news_res, search_res = results
    
    # Access .final_output safely (handling potential exceptions)
    def extract_output(res, name):
        if isinstance(res, Exception):
            return f"❌ {name} Error: {str(res)}"
        return f"✅ {name} Report:\n{res.final_output}"

    out_yf = extract_output(yf_res, "YahooFinanceAgent")
    out_news = extract_output(news_res, "NewsAgent")
    out_search = extract_output(search_res, "WebSearchAgent")
    
    combined_response = f"""
    --- START OF AGENT REPORTS ---
    
    {out_yf}
    
    -----------------------------------
    
    {out_news}
    
    -----------------------------------
    
    {out_search}
    
    --- END OF AGENT REPORTS ---
    """
    return combined_response

orchestrator_agent = Agent(
    name="AI Market Research Orchestrator",
    tools=[broadcast_research],
    instructions="""
    You are the **AI Market Research Orchestrator**. 
    Your goal is to provide a comprehensive, multi-perspective answer by synthesizing data from specialized sub-agents.

    **Workflow**:
    1.  **Analyze Request**: Understand the user's question.
    2.  **Broadcast Query**: IMMEDIATELY call the `broadcast_research` tool with a relevant search query.
        *   This tool runs the Finance, News, and Web Search agents in parallel.
    3.  **Synthesize Results**: Read the returned "Agent Reports".
        *   Combine the financial data (prices, sentiment), news headlines, and general search context.
        *   Compare and contrast findings if necessary.
        *   Resolve conflicts by prioritizing specific data (e.g., Yahoo Finance for prices) over general text.
    4.  **Final Response**: Generate a clear, professional, and well-structured summary for the user. Do not simply paste the individual reports.

    **Final Response Structure (MANDATORY)**:
    You MUST structure your final response exactly as follows:
    
    # [Market Analysis Title]
    
    ## 📊 Financial Snapshot
    *   **Price/Sentiment**: [Synthesized from Yahoo Finance]
    *   **Analyst Rating**: [Buy/Sell/Hold consensus]
    
    ## 📰 Key Developments
    *   [Headline 1] - [Source]
    *   [Headline 2] - [Source]
    
    ## 🔍 Web Insights
    *   [Key finding from general search, if any]
    
    ## ⚖️ Synthesis & Recommendation
    *   [Your comprehensive summary merging all data points. Highlight any conflicts.]
    
    **Constraint**:
    *   Do NOT try to answer based on your own knowledge if live data is needed.
    *   ALWAYS use `broadcast_research` for queries requiring up-to-date information.
    *   If agents return "No data", explicitly state that in the relevant section.
    """,
    model=gemini_model,
)
orchestrator_agent.description = "An intelligent orchestrator that queries Finance, News, and Search agents in parallel and synthesizes a comprehensive response."


__all__ = ["orchestrator_agent"]
