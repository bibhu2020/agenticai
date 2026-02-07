
try:
    from ..data.market_data import get_market_data
except (ImportError, ValueError):
    from data.market_data import get_market_data

import pandas as pd

def analyze_golden_cross(symbol: str) -> dict:
    """
    Analyze Golden Cross (SMA 50 crosses above SMA 200) strategy.
    """
    # Need enough data for 200 SMA -> ~1 year (252 trading days) + buffer
    raw_data = get_market_data(symbol, period="2y")
    if not raw_data or len(raw_data) < 200:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": "Insufficient data for 200 SMA"}
    
    df = pd.DataFrame(raw_data)
    
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()
    
    current_50 = df['sma_50'].iloc[-1]
    current_200 = df['sma_200'].iloc[-1]
    
    prev_50 = df['sma_50'].iloc[-2]
    prev_200 = df['sma_200'].iloc[-2]
    
    # Check for crossover
    # Golden Cross: 50 crosses above 200
    golden_cross = (prev_50 <= prev_200) and (current_50 > current_200)
    
    # Death Cross: 50 crosses below 200
    death_cross = (prev_50 >= prev_200) and (current_50 < current_200)
    
    # Trend Context
    bullish_trend = current_50 > current_200
    
    action = "HOLD"
    confidence = 0.0
    reasoning = []
    
    if golden_cross:
        action = "BUY"
        confidence = 0.9
        reasoning.append("Golden Cross Detected (50 SMA crossed above 200 SMA)")
    elif death_cross:
        action = "SELL"
        confidence = 0.9
        reasoning.append("Death Cross Detected (50 SMA crossed below 200 SMA)")
    elif bullish_trend:
        action = "BUY"
        confidence = 0.5
        reasoning.append("Bullish Trend (50 SMA > 200 SMA)")
    else:
        action = "SELL"
        confidence = 0.5
        reasoning.append("Bearish Trend (50 SMA < 200 SMA)")
        
    return {
        "strategy": "Golden Cross",
        "symbol": symbol,
        "action": action,
        "confidence": confidence,
        "reasoning": "; ".join(reasoning)
    }
