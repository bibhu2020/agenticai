
try:
    from ..data.fundamentals import get_fundamental_data
except (ImportError, ValueError):
    from data.fundamentals import get_fundamental_data

def analyze_value(symbol: str) -> dict:
    """
    Analyze value based on fundamentals.
    """
    fund_data = get_fundamental_data(symbol)
    if "error" in fund_data:
        return {"action": "HOLD", "confidence": 0.0, "reasoning": f"Error: {fund_data['error']}"}
    
    pe = fund_data.get("pe_ratio")
    # forward_pe = fund_data.get("forward_pe")
    # sector = fund_data.get("sector")
    
    score = 0
    reasons = []
    
    # Simple PE Logic (Generic)
    if pe:
        if pe < 15:
            score += 1
            reasons.append(f"Low PE Ratio ({pe})")
        elif pe > 30:
            score -= 1
            reasons.append(f"High PE Ratio ({pe})")
        else:
            reasons.append(f"Moderate PE Ratio ({pe})")
    else:
        reasons.append("PE Ratio data missing")
        
    # Dividend Logic (if applicable)
    div_yield = fund_data.get("dividend_yield")
    if div_yield and div_yield > 0.03:
        score += 0.5
        reasons.append(f"Good Dividend Yield ({div_yield:.1%})")

    action = "HOLD"
    if score >= 1:
        action = "BUY"
    elif score <= -1:
        action = "SELL"
        
    return {
        "strategy": "Value",
        "symbol": symbol,
        "action": action,
        "confidence": min(abs(score) / 2.0, 1.0),
        "reasoning": "; ".join(reasons)
    }
