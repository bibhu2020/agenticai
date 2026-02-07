
import yfinance as yf
import pandas as pd
from typing import List, Dict, Union

# Try relative import first (for package mode), then absolute (for script/test mode)
try:
    from ..schemas import OHLC, StockData
except (ImportError, ValueError):
    try:
        from schemas import OHLC, StockData
    except (ImportError, ValueError):
        # Fallback if both fail (e.g. running from root but parent not package)
        # This shouldn't be needed if path is correct
        pass

def get_market_data(symbol: str, period: str = "1mo", interval: str = "1d") -> List[Dict]:
    """
    Fetch historical data for a symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            return []
            
        data = []
        for index, row in history.iterrows():
            data.append({
                "date": index.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return []

def get_current_price(symbol: str) -> float:
    """Get the latest price."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.history(period="1d")
        if not info.empty:
            return float(info["Close"].iloc[-1])
        return 0.0
    except Exception:
        return 0.0
