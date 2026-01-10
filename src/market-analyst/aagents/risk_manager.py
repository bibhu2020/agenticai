from autogen_agentchat.agents import AssistantAgent

def get_risk_manager(model_client):
    
    return AssistantAgent(
        name="RiskManager",
        model_client=model_client,
        system_message="""
        You are the Chief Risk Officer.
        1. Review the proposed strategy and confidence score.
        2. STRICT RULE: If confidence < 70, reject the trade and recommend "WAIT".
        3. Validate the score calculation against the Rubric (Start 50 + Trend/Vol/Sentiment addons).
        4. Event Risk Check: If Earnings/CPI imminent, override and recommend "WAIT".
        
        Output final JSON:
           {
             "final_decision": "TRADE | WAIT",
             "confidence": ..., // The final validated score
             "actionable_recommendation": "Execute Bull Call Spread... / Stay in Cash",
             "entry_signal": "Net Credit | Net Debit",
             "entry_price": 1.50,
             "risk_warning": "..."
           }
        """
    )
