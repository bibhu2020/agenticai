
try:
    from ..data.market_data import get_market_data
except (ImportError, ValueError):
    from data.market_data import get_market_data

import pandas as pd

def analyze_macd_crossover(symbol: str) -> dict:
    """
    Analyze MACD Crossover (MACD line crosses Signal line) strategy.
    """
    raw_data = get_market_data(symbol, period="6mo")
    if not raw_data or len(raw_data) < 50:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": "Insufficient data"}
    
    df = pd.DataFrame(raw_data)
    
    # Calculate MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    
    curr_h = hist.iloc[-1]
    prev_h = hist.iloc[-2]
    
    # Cross Up (Bullish): Histogram goes from negative to positive
    cross_up = (prev_h <= 0) and (curr_h > 0)
    
    # Cross Down (Bearish): Histogram goes from positive to negative
    cross_down = (prev_h >= 0) and (curr_h < 0)
    
    action = "HOLD"
    confidence = 0.0
    reasoning = []
    
    if cross_up:
        action = "BUY"
        confidence = 0.8
        reasoning.append("MACD Bullish Crossover")
    elif cross_down:
        action = "SELL"
        confidence = 0.8
        reasoning.append("MACD Bearish Crossover")
    elif curr_h > 0:
        action = "BUY"
        confidence = 0.4
        reasoning.append("MACD Bullish Momentum (Above Signal)")
    else:
        action = "SELL"
        confidence = 0.4
        reasoning.append("MACD Bearish Momentum (Below Signal)")
        
    return {
        "strategy": "MACD Crossover",
        "symbol": symbol,
        "action": action,
        "confidence": confidence,
        "reasoning": "; ".join(reasoning)
    }
