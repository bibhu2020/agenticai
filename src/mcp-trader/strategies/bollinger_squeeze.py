
try:
    from ..data.market_data import get_market_data
except (ImportError, ValueError):
    from data.market_data import get_market_data

import pandas as pd
import numpy as np

def analyze_bollinger_squeeze(symbol: str) -> dict:
    """
    Analyze BB Squeeze (Low Volatility) + Direction.
    """
    try:
        raw_data = get_market_data(symbol, period="6mo")
        if not raw_data or len(raw_data) < 50:
            return {"action": "HOLD", "confidence": 0.0, "reasoning": "Insufficient data"}
        
        df = pd.DataFrame(raw_data)
        
        # Calculate Bands
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        
        upper = sma + (2 * std)
        lower = sma - (2 * std)
        
        # Band Width relative to price
        df['bandwidth'] = (upper - lower) / sma
        
        # Recent Band Width percentile (last 6 months)
        current_bw = df['bandwidth'].iloc[-1]
        bw_rank = df['bandwidth'].rank(pct=True).iloc[-1]
        
        # Squeeze Condition: Width in lowest 20% of last 6mo
        squeeze_on = bw_rank <= 0.20
        
        # Momentum direction (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        action = "HOLD"
        confidence = 0.0
        reasoning = []
        
        if squeeze_on:
            reasoning.append(f"Volatility Squeeze ACTIVE (Rank: {bw_rank:.0%})")
            if current_rsi > 50:
                action = "BUY"
                confidence = 0.7  # Breakout potential upwards
                reasoning.append("Squeeze + Bullish Momentum (RSI > 50)")
            else:
                action = "SELL"
                confidence = 0.7 # Breakout potential downwards
                reasoning.append("Squeeze + Bearish Momentum (RSI < 50)")
        else:
            reasoning.append(f"No Squeeze (Rank: {bw_rank:.0%})")
            
        return {
            "strategy": "Bollinger Squeeze",
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "reasoning": "; ".join(reasoning)
        }
    except Exception as e:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": f"Error: {str(e)}"}
