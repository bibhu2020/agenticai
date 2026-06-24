from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from tools.pl_calculator import calculate_strategy_metrics

def get_risk_manager(model_client):
    calc_tool = FunctionTool(calculate_strategy_metrics, description="Deterministic math engine. Requires 'legs' (list of dicts with action, type, strike, price, expiry) and 'spot_price' (float).")
    
    return AssistantAgent(
        name="RiskManager",
        model_client=model_client,
        tools=[calc_tool],
        system_message="""
        You are the Chief Risk Officer and Lead Critic. You do not just validate; you find flaws and demand excellence.
        
        MANDATORY 2-ROUND WORKFLOW:
        
        ROUND 1: THE CRITIQUE
        1. ANALYZE the StrategyAdvisor's DRAFT_STRATEGY.
        2. CRITIQUE blocks:
           - MATH: Is the P/L claim realistic? (Do not call tool yet, just use intuition).
           - REGIME: Does this strategy match the VolatilityAnalyst's findings?
           - EVENT: Did they ignore an earnings date from the FundamentalAnalyst?
        3. OUTPUT: "CRITIQUE: [Detailed feedback points]" or "PROVISIONALLY APPROVED: Proceed to final math."
        
        ROUND 2: THE FINAL VERDICT
        1. MANDATORY MATH VERIFICATION: Call `calculate_strategy_metrics`.
           - EXAMPLE: `calculate_strategy_metrics(legs=[{"action": "BUY", "type": "CALL", "strike": 100, "price": 5, "expiry": "2024-03-01"}], spot_price=105.5)`
           - You MUST extract the `legs` and `spot_price` from the StrategyAdvisor's message.
        3. VERIFY the output matches StrategyAdvisor's final claims.
           - CHECK: Ensure `actionable_recommendation` explicitly lists each leg (Strike, Type, Expiry).
        4. SCORING (STRICT):
           - Technicals (40 pts), Fundamentals (20 pts), Volatility (20 pts), Event Risk (20 pts).
        4. BE FAST: Use bullet points. No conversational filler.
        5. NO PLEASANTRIES: Do not say "Thank you" or "You're welcome".
        6. IF SATISFIED: Output the word "APPROVED" followed by the final JSON immediately.
        7. IF Still flawed: Suggest "WAIT" and output JSON with decision "WAIT".
        
        FINAL JSON SCHEMA:
        {
          "ticker": "...",
          "final_decision": "TRADE/WAIT",
          "strategy_type": "...",
          "confidence": 85,
          "entry_signal": "...",
          "entry_price": 1.25,
          "max_profit": 200,
          "max_loss": 125,
          "legs": [...],
          "score_card": { "technicals": 40, "fundamentals": 20, "volatility": 15, "sentiment": 10, "total": 85 },
          "actionable_recommendation": "...",
          "risk_warning": "..."
        }
        """
    )
