from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
import os

from aagents import get_stock_trends_agent, get_news_agent, get_sentiment_agent, get_decision_agent, StockTrend
from autogen_agentchat.messages import StructuredMessage
from core.model import get_model_client

def get_investment_team():
    # Try to register the message type to avoid "not registered" errors in GroupChat
    try:
        from autogen_core import TypeSubscription
        pass
    except ImportError:
        pass
        
    text_termination = TextMentionTermination("Decision Made")
    max_message_termination = MaxMessageTermination(20)
    termination = text_termination | max_message_termination
    
    # # Model for the selector/moderator
    # selector_model = OpenAIChatCompletionClient(
    #     model="gemini-2.5-flash",
    #     api_key=os.getenv("GOOGLE_API_KEY"),
    #     model_info={
    #                     "family": "gemini",
    #                     "vision": True,
    #                     "function_calling": True,
    #                     "json_output": True,
    #                     "structured_output": True,
    #                 },
    #     temperature=0
    # )

    # Selector Group Chat which allows dynamic speaker selection
    investment_team = SelectorGroupChat(
        [
            get_stock_trends_agent(),
            get_news_agent(),
            get_sentiment_agent(),
            get_decision_agent(),
        ],
        model_client=get_model_client(),
        termination_condition=termination
    )
    return investment_team

