from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool 
from tools.yf_tools import _get_analyst_recommendations
from core.model import get_model_client

def get_sentiment_agent():
    model_client = get_model_client()

    async def get_market_sentiment(symbol: str, period: str) -> str:
        """Get market sentiment for a stock."""
        from tools.yf_tools import _get_market_sentiment
        return _get_market_sentiment(symbol, period)

    async def get_analyst_recs(symbol: str) -> str:
        """Get analyst recommendations for a stock."""
        # _get_analyst_recommendations is already imported
        return _get_analyst_recommendations(symbol)

    sentiment_tool = FunctionTool(get_market_sentiment, description="Get market sentiment")
    analyst_tool = FunctionTool(get_analyst_recs, description="Get analyst recommendations")

    sentiment_agent = AssistantAgent(
        name="sentiment_agent",
        model_client=model_client,
        tools=[sentiment_tool, analyst_tool],
        system_message=(
            "You are the Market Sentiment Agent. "
            "You gather overall market sentiment, relevant analyst reports, and expert opinions. "
            "Do NOT provide any final investment decision."
        )
    )
    return sentiment_agent
