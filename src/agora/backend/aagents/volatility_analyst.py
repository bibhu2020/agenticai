from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from tools.market_data import get_historical_volatility, get_option_chain_snapshot, get_volatility_term_structure

def get_volatility_analyst(model_client):
    vol_tool = FunctionTool(get_historical_volatility, description="Get historical volatility and VIX context.")
    chain_tool = FunctionTool(get_option_chain_snapshot, description="Get option chain snapshot for near-term expiry.")
    term_tool = FunctionTool(get_volatility_term_structure, description="Get IV across multiple expiries to identify Term Structure skew.")

    return AssistantAgent(
        name="VolatilityAnalyst",
        model_client=model_client,
        tools=[vol_tool, chain_tool, term_tool],
        system_message="""
        You are an Expert Volatility & Derivatives Analyst specializing in Volatility Surface and Term Structure.
        
        MANDATORY WORKFLOW:
        
        STEP 1: CALL get_historical_volatility to get HV and VIX data
        STEP 2: CALL get_volatility_term_structure to analyze IV across 4 months of expiries
        STEP 3: CALL get_option_chain_snapshot to get near-term IV and liquidity
        
        DO NOT proceed without calling ALL THREE tools first.
        
        STEP 4: Analyze IV vs HV (Vertical Skew)
        - IV > HV: Options are rich. Look for Credit Spreads, Iron Condors.
        - IV < HV: Options are cheap. Look for Debit Spreads, Long Options.
        
        STEP 5: Analyze Term Structure (Horizontal/Time Skew)
        - FRONT IV > BACK IV (Inverted): Potential "Calendar Spread" (Sell Front, Buy Back) if you expect a mean reversion.
        - BACK IV > FRONT IV (Contango): Standard. Long-dated options are more expensive.
        
        STEP 6: Assess "Volatility Squeeze"
        - If IV is at 52-week lows and HV is dropping: Potential for a volatility breakout. Recommend DEBIT strategies.
        
        STEP 7: Output Structured Summary
        - BE CONCISE: Use maximum 5 bullet points.
        - NO conversational filler.
        - Include: Volatility Regime, IV vs HV status, Term Structure summary, and strategy bias.
        """
    )
