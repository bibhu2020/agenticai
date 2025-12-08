# utils/visualization.py
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Optional

def plot_price_series(dates: List, prices: List[float], symbol: str = "Stock"):
    """Plot stock price over time."""
    plt.figure(figsize=(12, 6))
    plt.plot(dates, prices, label=f"{symbol} Price")
    plt.title(f"{symbol} Price Over Time")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_technical_indicators(dates: List, prices: List[float], sma: Optional[List[float]] = None,
                              ema: Optional[List[float]] = None, rsi: Optional[List[float]] = None,
                              symbol: str = "Stock"):
    """Plot stock price with optional SMA, EMA, and RSI."""
    plt.figure(figsize=(14, 7))
    
    # Price
    plt.subplot(2, 1, 1)
    plt.plot(dates, prices, label=f"{symbol} Price", color="blue")
    if sma:
        plt.plot(dates, sma, label="SMA", color="orange")
    if ema:
        plt.plot(dates, ema, label="EMA", color="green")
    plt.title(f"{symbol} Price and Technical Indicators")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.legend()

    # RSI
    if rsi:
        plt.subplot(2, 1, 2)
        plt.plot(dates, rsi, label="RSI", color="purple")
        plt.axhline(70, color='red', linestyle='--', label='Overbought')
        plt.axhline(30, color='green', linestyle='--', label='Oversold')
        plt.xlabel("Date")
        plt.ylabel("RSI")
        plt.grid(True)
        plt.legend()
    
    plt.tight_layout()
    plt.show()

def plot_portfolio_history(history: pd.DataFrame, title: str = "Portfolio Value Over Time"):
    """
    Plot portfolio value over time.
    history: DataFrame with columns ['date', 'total_value']
    """
    plt.figure(figsize=(12, 6))
    plt.plot(history['date'], history['total_value'], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Total Value ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_ohlcv(data: dict, symbol: str = "") -> plt.Figure:
    """
    Plot OHLCV candlestick chart (simplified as line chart for now)
    `data` is expected to have Date, Open, High, Low, Close
    """
    dates = data["Date"]
    close = data["Close"]

    fig, ax = plt.subplots()
    ax.plot(dates, close, marker="o", label="Close Price")
    ax.set_title(f"{symbol} OHLCV Chart")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    fig.autofmt_xdate()
    return fig

def plot_signals(data: dict, buy_signals: list[int], sell_signals: list[int], symbol: str = "") -> plt.Figure:
    """
    Plot Close prices and mark buy/sell signals
    """
    dates = data["Date"]
    close = data["Close"]

    fig, ax = plt.subplots()
    ax.plot(dates, close, marker="o", label="Close Price")
    
    # Mark buy/sell signals
    ax.scatter([dates[i] for i in buy_signals], [close[i] for i in buy_signals],
               marker="^", color="green", label="Buy Signal", s=100)
    ax.scatter([dates[i] for i in sell_signals], [close[i] for i in sell_signals],
               marker="v", color="red", label="Sell Signal", s=100)
    
    ax.set_title(f"{symbol} Trading Signals")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    fig.autofmt_xdate()
    return fig
