
try:
    from ..data.market_data import get_market_data
    from ..indicators.technical import calculate_rsi, calculate_macd, calculate_sma
except (ImportError, ValueError):
    from data.market_data import get_market_data
    from indicators.technical import calculate_rsi, calculate_macd, calculate_sma
import pandas as pd

def analyze_momentum(symbol: str) -> dict:
    """
    Analyze momentum for a given symbol.
    Returns: StrategyResult dict
    """
    raw_data = get_market_data(symbol, period="3mo")
    if not raw_data:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": "No data found"}
    
    df = pd.DataFrame(raw_data)
    
    rsi = calculate_rsi(df)
    macd_data = calculate_macd(df)
    sma_50 = calculate_sma(df, 50)
    current_price = df['close'].iloc[-1]
    
    score = 0
    reasons = []
    
    # RSI Logic
    if rsi < 30:
        score += 1
        reasons.append(f"RSI is oversold ({rsi:.2f})")
    elif rsi > 70:
        score -= 1
        reasons.append(f"RSI is overbought ({rsi:.2f})")
    else:
        reasons.append(f"RSI is neutral ({rsi:.2f})")
        
    # MACD Logic
    if macd_data["histogram"] > 0:
        score += 1
        reasons.append("MACD histogram is positive")
    else:
        score -= 1
        reasons.append("MACD histogram is negative")
        
    # Trend Logic
    if current_price > sma_50:
        score += 1
        reasons.append("Price is above 50 SMA")
    else:
        score -= 1
        reasons.append("Price is below 50 SMA")
        
    # Final Decision
    action = "HOLD"
    if score >= 2:
        action = "BUY"
    elif score <= -2:
        action = "SELL"
        
    return {
        "strategy": "Momentum",
        "symbol": symbol,
        "action": action,
        "confidence": abs(score) / 3.0,
        "reasoning": "; ".join(reasons)
    }
