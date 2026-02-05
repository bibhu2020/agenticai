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
    from ..aagents.market_analyst import get_technical_analyst
    from ..aagents.volatility_analyst import get_volatility_analyst
    from ..aagents.sentiment_analyst import get_sentiment_analyst
    from ..aagents.strategy_advisor import get_strategy_advisor
    from ..aagents.risk_manager import get_risk_manager
    from ..aagents.fundamental_analyst import get_fundamental_analyst
except ImportError:
    try:
        from aagents.market_analyst import get_technical_analyst
        from aagents.volatility_analyst import get_volatility_analyst
        from aagents.sentiment_analyst import get_sentiment_analyst
        from aagents.strategy_advisor import get_strategy_advisor
        from aagents.risk_manager import get_risk_manager
        from aagents.fundamental_analyst import get_fundamental_analyst
    except ImportError:
         # Try absolute (if market-analyst is in path but not as package)
         from src.market_analyst.backend.aagents.market_analyst import get_technical_analyst
         from src.market_analyst.backend.aagents.volatility_analyst import get_volatility_analyst
         from src.market_analyst.backend.aagents.sentiment_analyst import get_sentiment_analyst
         from src.market_analyst.backend.aagents.strategy_advisor import get_strategy_advisor
         from src.market_analyst.backend.aagents.risk_manager import get_risk_manager
         from src.market_analyst.backend.aagents.fundamental_analyst import get_fundamental_analyst

def get_trading_team(model_client):
    """
    Creates and returns the RoundRobinGroupChat team for predictable sequential execution.
    """
    technical = get_technical_analyst(model_client)
    volatility = get_volatility_analyst(model_client)
    sentiment = get_sentiment_analyst(model_client)
    fundamental = get_fundamental_analyst(model_client)
    strategy = get_strategy_advisor(model_client)
    risk = get_risk_manager(model_client)

    team = RoundRobinGroupChat(
        participants=[technical, volatility, sentiment, fundamental, strategy, risk],
        # Increased limit for 2-round detailed discussion
        termination_condition=TextMentionTermination("APPROVED") | MaxMessageTermination(60)
    )
    return team

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON from text that may contain markdown code blocks or other content.
    Validates and ensures required fields are present.
    """
    # Try to find JSON in code blocks first
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_block_pattern, text, re.DOTALL)
    if matches:
        try:
            parsed = json.loads(matches[-1])
            return validate_and_complete_json(parsed)
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        for match in reversed(matches):
            try:
                parsed = json.loads(match)
                return validate_and_complete_json(parsed)
            except json.JSONDecodeError:
                continue
    
    return {}

def validate_and_complete_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate JSON has required fields and add defaults if missing.
    """
    required_fields = {
        "final_decision": "WAIT",
        "confidence": 0,
        "actionable_recommendation": "Incomplete analysis - please retry",
        "strategy_type": "None",
        "entry_signal": "N/A",
        "entry_price": 0,
        "max_profit": 0,
        "max_loss": 0,
        "risk_warning": "Analysis incomplete"
    }
    
    # Add missing required fields with defaults
    for field, default_value in required_fields.items():
        if field not in data:
            data[field] = default_value
    
    return data
