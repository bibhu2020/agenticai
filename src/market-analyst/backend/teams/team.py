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

from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, HandoffTermination

# Import agents
# Adjust imports to work whether called from here or app.py
try:
    from ..aagents.market_analyst import get_technical_analyst
    from ..aagents.volatility_analyst import get_volatility_analyst
    from ..aagents.sentiment_analyst import get_sentiment_analyst
    from ..aagents.strategy_advisor import get_strategy_advisor
    from ..aagents.risk_manager import get_risk_manager
    from ..aagents.fundamental_analyst import get_fundamental_analyst
    from ..aagents.orchestrator import get_lead_orchestrator
except ImportError:
    try:
        from aagents.market_analyst import get_technical_analyst
        from aagents.volatility_analyst import get_volatility_analyst
        from aagents.sentiment_analyst import get_sentiment_analyst
        from aagents.strategy_advisor import get_strategy_advisor
        from aagents.risk_manager import get_risk_manager
        from aagents.fundamental_analyst import get_fundamental_analyst
        from aagents.orchestrator import get_lead_orchestrator
    except ImportError:
         # Try absolute (if market-analyst is in path but not as package)
         from src.market_analyst.backend.aagents.market_analyst import get_technical_analyst
         from src.market_analyst.backend.aagents.volatility_analyst import get_volatility_analyst
         from src.market_analyst.backend.aagents.sentiment_analyst import get_sentiment_analyst
         from src.market_analyst.backend.aagents.strategy_advisor import get_strategy_advisor
         from src.market_analyst.backend.aagents.risk_manager import get_risk_manager
         from src.market_analyst.backend.aagents.fundamental_analyst import get_fundamental_analyst

from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat

def get_analyst_team(model_client):
    """
    Team 1: DATA COLLECTORS.
    Independent analysts gather data and provide a comprehensive market snapshot.
    """
    technical = get_technical_analyst(model_client)
    volatility = get_volatility_analyst(model_client)
    sentiment = get_sentiment_analyst(model_client)
    fundamental = get_fundamental_analyst(model_client)

    return RoundRobinGroupChat(
        participants=[technical, volatility, sentiment, fundamental],
        termination_condition=TextMentionTermination("[[DATA_COLLECTION_COMPLETE]]") | MaxMessageTermination(15)
    )

def get_decision_team(model_client):
    """
    Team 2: STRATEGY & RISK.
    Uses the Analyst Context (Team 1 output) to design, critique, and finalize the trade.
    """
    strategy = get_strategy_advisor(model_client)
    risk = get_risk_manager(model_client)
    orchestrator = get_lead_orchestrator(model_client)

    participants = [strategy, risk, orchestrator]

    selector_prompt = """
    Select the next agent based on the conversation history:
    - Choose StrategyAdvisor to propose or update the trade.
    - Choose RiskManager to verify the proposal or critique it.
    - Choose LeadOrchestrator ONLY if the RiskManager has said "APPROVED" or if the discussion is stuck.
    
    Output only the name of the next agent.
    """

    return SelectorGroupChat(
        participants=participants,
        model_client=model_client,
        termination_condition=TextMentionTermination("[[ANALYSIS_JUDGMENT_COMPLETE]]") | MaxMessageTermination(12),
        selector_prompt=selector_prompt
    )

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
        "risk_warning": "Analysis incomplete",
        "expiry_date": "N/A",
        "legs": []
    }
    
    # Add missing required fields with defaults
    for field, default_value in required_fields.items():
        if field not in data:
            data[field] = default_value
    
    # Fallback: If expiry_date is "N/A" but we have legs, take it from there
    if data.get("expiry_date") == "N/A" and data.get("legs"):
        # Take expiry of first leg
        data["expiry_date"] = data["legs"][0].get("expiry", "N/A")
    
    # Existing Fallback: If expiry_date is still "N/A", try to extract it from context
    if data.get("expiry_date") == "N/A":
        # Look for YYYY-MM-DD pattern
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        
        # Check 'actionable_recommendation' or 'reasoning' (if present)
        for search_field in ["actionable_recommendation", "reasoning", "risk_warning", "proposed_legs"]:
            field_val = data.get(search_field, "")
            if isinstance(field_val, str):
                match = re.search(date_pattern, field_val)
                if match:
                    data["expiry_date"] = match.group(0)
                    break
                    
    return data
