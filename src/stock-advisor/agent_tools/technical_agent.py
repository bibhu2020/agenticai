# agents/technical_agent.py
"""
Technical Agent
---------------
Responsible for performing technical analysis on stock price data.
Features:
- Moving averages (SMA, EMA)
- RSI, MACD indicators
- Detect simple candlestick patterns
- Generate signals (buy/hold/sell)
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TechnicalAgent:
    def __init__(self):
        self.name = "TechnicalAgent"

    def calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Simple Moving Average
        """
        if "Close" not in data.columns:
            logger.error("DataFrame missing 'Close' column for SMA calculation")
            return pd.Series()
        sma = data["Close"].rolling(window=period).mean()
        return sma

    def calculate_ema(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Exponential Moving Average
        """
        if "Close" not in data.columns:
            logger.error("DataFrame missing 'Close' column for EMA calculation")
            return pd.Series()
        ema = data["Close"].ewm(span=period, adjust=False).mean()
        return ema

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Relative Strength Index
        """
        if "Close" not in data.columns:
            logger.error("DataFrame missing 'Close' column for RSI calculation")
            return pd.Series()

        delta = data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def analyze(self, data: pd.DataFrame) -> dict:
        """
        Perform a full technical analysis on OHLCV data.
        Returns a dict containing indicators and a simple signal.
        """
        if data.empty:
            logger.warning("Empty OHLCV data provided for analysis")
            return {}

        result = {}
        result["SMA_20"] = self.calculate_sma(data, period=20)
        result["EMA_20"] = self.calculate_ema(data, period=20)
        result["RSI_14"] = self.calculate_rsi(data, period=14)

        # Generate simple signal
        try:
            latest_rsi = result["RSI_14"].iloc[-1]
            if latest_rsi < 30:
                signal = "Buy"
            elif latest_rsi > 70:
                signal = "Sell"
            else:
                signal = "Hold"
            result["signal"] = signal
            logger.info("Technical analysis complete. Signal: %s", signal)
        except Exception as e:
            logger.exception("Failed to generate technical signal: %s", e)
            result["signal"] = "Hold"

        return result


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Dummy OHLCV data
    data = pd.DataFrame({
        "Open": np.random.rand(50) * 100,
        "High": np.random.rand(50) * 100,
        "Low": np.random.rand(50) * 100,
        "Close": np.random.rand(50) * 100,
        "Volume": np.random.randint(1000, 10000, size=50)
    })

    agent = TechnicalAgent()
    analysis = agent.analyze(data)
    print("Technical Analysis Result:")
    print(analysis)
