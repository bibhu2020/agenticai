from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool 
from tools.search_tools import _duckduckgo_search, searchQuery
from aagents.common import get_model_client

def get_news_agent():
    model_client = get_model_client()

    async def news_search(query: str) -> str:
        """
        Search for latest news regarding a topic or stock.
        """
        # Anchor search to reputable sources as per Suggestion 3
        reputable_sources = " (site:bloomberg.com OR site:reuters.com OR site:cnbc.com OR site:wsj.com OR site:finance.yahoo.com)"
        if "site:" not in query:
             query += reputable_sources

        # Use underlying function with proper params
        params = searchQuery(query=query, search_type="news", timelimit="d", max_results=5)
        # _duckduckgo_search returns list[dict], convert to str
        results = _duckduckgo_search(params)
        return str(results)

    news_tool = FunctionTool(news_search, description="Search for latest top 5 news for a given stock or topic. Returns headlines and snippets only.")

    news_agent = AssistantAgent(
        name="news_agent",
        model_client=model_client,
        tools=[news_tool],
        system_message=(
            "You are the News Agent. "
            "1. Search for the latest top 5 news stories related to the given stock using `news_tool`. "
            "2. Prioritize reputable result sources like Bloomberg, Reuters, CNBC, WSJ, and Yahoo Finance if possible. "
            "3. Summarize the key insights from the news stories. "
            "Do NOT provide any final investment decision."
        )
    )
    return news_agent
