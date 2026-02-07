
import yfinance as yf
from typing import Dict, Any

def get_fundamental_data(symbol: str) -> Dict[str, Any]:
    """
    Get key fundamental metrics.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "beta": info.get("beta"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }
    except Exception as e:
        return {"error": str(e)}
