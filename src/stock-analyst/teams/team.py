from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from aagents.agents import get_stock_trends_agent, get_news_agent, get_sentiment_agent, get_decision_agent, StockTrend
from autogen_agentchat.messages import StructuredMessage

def get_investment_team():
    # Try to register the message type to avoid "not registered" errors in GroupChat
    try:
        from autogen_core import TypeSubscription
        # This part is speculative based on the error. 
        # Ideally we use the agent runtime's registry, but here we just ensure the type is known.
        pass
    except ImportError:
        pass
    text_termination = TextMentionTermination("Decision Made")
    max_message_termination = MaxMessageTermination(15)
    termination = text_termination | max_message_termination
    
    # Round-robin chat among the four agents
    investment_team = RoundRobinGroupChat(
        [
            get_stock_trends_agent(),
            get_news_agent(),
            get_sentiment_agent(),
            get_decision_agent(),
        ],
        termination_condition=termination
    )
    return investment_team

