import sys
import os
import json
import re
from typing import Dict, Any

# Ensure we can import from parent directory if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

# Import agents
# Adjust imports to work whether called from here or app.py
try:
    from ..aagents.market_analyst import get_market_analyst
    from ..aagents.sentiment_analyst import get_sentiment_analyst
    from ..aagents.strategy_advisor import get_strategy_advisor
    from ..aagents.risk_manager import get_risk_manager
except ImportError:
    # Fallback if running from proper package context
    try:
        from aagents.market_analyst import get_market_analyst
        from aagents.sentiment_analyst import get_sentiment_analyst
        from aagents.strategy_advisor import get_strategy_advisor
        from aagents.risk_manager import get_risk_manager
    except ImportError:
         # Try absolute (if market-analyst is in path but not as package)
         from src.market_analyst.aagents.market_analyst import get_market_analyst
         from src.market_analyst.aagents.sentiment_analyst import get_sentiment_analyst
         from src.market_analyst.aagents.strategy_advisor import get_strategy_advisor
         from src.market_analyst.aagents.risk_manager import get_risk_manager

def get_trading_team(model_client):
    """
    Creates and returns the RoundRobinGroupChat team.
    """
    market = get_market_analyst(model_client)
    sentiment = get_sentiment_analyst(model_client)
    strategy = get_strategy_advisor(model_client)
    risk = get_risk_manager(model_client)

    team = RoundRobinGroupChat(
        participants=[market, sentiment, strategy, risk],
        termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(12)
    )
    return team

def extract_json(text: str) -> Dict[str, Any]:
    """Helper to extract JSON from markdown code blocks or raw text."""
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except:
        return {}
