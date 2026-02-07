
try:
    from ..data.market_data import get_market_data
    from ..indicators.technical import calculate_bollinger_bands, calculate_rsi
except (ImportError, ValueError):
    from data.market_data import get_market_data
    from indicators.technical import calculate_bollinger_bands, calculate_rsi
import pandas as pd

def analyze_mean_reversion(symbol: str) -> dict:
    """
    Analyze mean reversion potential.
    """
    raw_data = get_market_data(symbol, period="3mo")
    if not raw_data:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": "No data found"}
    
    df = pd.DataFrame(raw_data)
    
    bb = calculate_bollinger_bands(df)
    rsi = calculate_rsi(df)
    current_price = df['close'].iloc[-1]
    
    score = 0
    reasons = []
    
    # Bollinger Bands Logic
    if current_price < bb["lower"]:
        score += 2
        reasons.append(f"Price below lower BB ({bb['lower']:.2f})")
    elif current_price > bb["upper"]:
        score -= 2
        reasons.append(f"Price above upper BB ({bb['upper']:.2f})")
    else:
        reasons.append("Price within bands")
        
    # RSI Confirmation
    if rsi < 30 and score > 0:
        score += 1
        reasons.append("RSI confirms oversold")
    elif rsi > 70 and score < 0:
        score -= 1
        reasons.append("RSI confirms overbought")
        
    action = "HOLD"
    if score >= 2:
        action = "BUY"
    elif score <= -2:
        action = "SELL"
        
    return {
        "strategy": "Mean Reversion",
        "symbol": symbol,
        "action": action,
        "confidence": min(abs(score) / 3.0, 1.0),
        "reasoning": "; ".join(reasons)
    }
