from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from tools.news_data import search_news

def get_sentiment_analyst(model_client):
    
    news_tool = FunctionTool(search_news, description="Search for recent news about the ticker.")

    return AssistantAgent(
        name="SentimentAnalyst",
        model_client=model_client,
        tools=[news_tool],
        system_message="""
        You are a Sentiment Analyst.
        1. Search for recent news. The results now include **FinBERT Sentiment Scores** (e.g. [FinBERT: positive (0.95)]).
        2. Aggregate these FinBERT scores to determine the overall sentiment (Bullish/Bearish/Neutral).
        3. Assign a 'Sentiment Confidence' score based on the FinBERT probability scores.
           - If multiple articles have >0.90 positive/negative, confidence is HIGH.
           - If signals are mixed or low probability, confidence is LOW/MEDIUM.
        4. Output JSON:
           {
             "sentiment": "...",
             "confidence": "...",
             "key_events": ["..."],
             "risk_factors": ["..."]
           }
        """
    )
