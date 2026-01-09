import yfinance as yf
import pandas as pd
import math
from datetime import datetime
import json

def check_and_fix_ticker(symbol: str) -> str:
    """
    Checks if the ticker has data. If not, tries appending '.NS' (for NSE India).
    Returns the working ticker or the original if neither works.
    """
    symbol = symbol.upper().strip()
    ticker = yf.Ticker(symbol)
    try:
        if ticker.fast_info.last_price is not None:
             return symbol
    except:
        pass
        
    ns_symbol = symbol + ".NS"
    ns_ticker = yf.Ticker(ns_symbol)
    try:
        if ns_ticker.fast_info.last_price is not None:
            return ns_symbol
    except:
        pass
    return symbol

def get_market_data(symbol: str) -> dict:
    """
    Aggregates current price, technical indicators, and volatility into a single dict.
    """
    symbol = check_and_fix_ticker(symbol)
    
    # 1. Price
    price = 0.0
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        if price is None:
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
    except:
        pass

    # 2. Technicals (simplified version of get_technical_indicators logic)
    technicals_summary = "N/A"
    try:
        hist = ticker.history(period="1y")
        if not hist.empty:
             hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
             hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
             
             last = hist.iloc[-1]
             sma50 = last.get('SMA_50', 0)
             sma200 = last.get('SMA_200', 0)
             
             trend = "Neutral"
             if not pd.isna(sma200):
                 trend = "Bullish" if price > sma200 else "Bearish"
             
             technicals_summary = f"Trend: {trend}. Price: {round(price, 2)}. SMA50: {round(sma50, 2) if not pd.isna(sma50) else 'N/A'}"
    except:
        pass

    return {
        "ticker": symbol,
        "price": price or 0.0,
        "technicals": technicals_summary
    }

def get_technical_summary(symbol: str) -> str:
    """Helper to just get the string summary."""
    data = get_market_data(symbol)
    return data['technicals']
