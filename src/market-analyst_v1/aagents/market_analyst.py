from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool
from tools.market_data import get_current_price, get_historical_volatility, get_option_chain_snapshot, get_technical_indicators

def get_market_analyst(model_client):
    
    # Wrap tools
    price_tool = FunctionTool(get_current_price, description="Get current price of a stock.")
    vol_tool = FunctionTool(get_historical_volatility, description="Get historical volatility and VIX context.")
    chain_tool = FunctionTool(get_option_chain_snapshot, description="Get option chain snapshot for near-term expiry.")
    tech_tool = FunctionTool(get_technical_indicators, description="Calculate SMA (20/50/200) and RSI (14) technical indicators.")

    return AssistantAgent(
        name="MarketAnalyst",
        model_client=model_client,
        tools=[price_tool, vol_tool, chain_tool, tech_tool],
        system_message="""
        You are a Market Technician.
        1. Fetch Price, Volatility, Option Chain, AND Technical Indicators (SMA, RSI) for the ticker.
        2. Analyze the Trend (Bullish/Bearish/Neutral) based on price action and SMA alignment (Price vs SMA200).
        3. Analyze the Volatility Regime (Low/Normal/High) using HV and VIX.
        4. Analyze Momentum: Check RSI levels (Overbought > 70 / Oversold < 30).
        5. Output a JSON similar to:
           {
             "ticker": "...",
             "price": ...,
             "trend": "...",
             "volatility": "...",
             "rsi_status": "Overbought/Neutral/Oversold",
             "liquidity_check": "Pass/Fail based on option chain availability",
             "notes": "..."
           }
        Do NOT recommend a trade yet. Just analyze the context.
        """
    )
