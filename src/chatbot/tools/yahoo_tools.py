import os
import requests
import yfinance as yf
from dotenv import load_dotenv
from agents import function_tool
from core.logger import log_call
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()


# ============================================================
# 🔹 YAHOO FINANCE TOOLSET
# ============================================================
class FinanceTools:
    """
    FinanceTools provides a set of function tools for interacting with Yahoo Finance for **Financial Data** only.
    These tools can be used by an AI agent to fetch stock, ETF, or crypto data,
    analyze recent market trends, market sentiments, and generate market insights.
    """

    @staticmethod
    @function_tool
    @log_call
    def get_summary(symbol: str, period: str = "1d", interval: str = "1h") -> str:
        """
        Fetch the latest summary information and intraday price data for a given ticker.
        Ensures recent data is retrieved by calculating start/end dates dynamically.

        Parameters:
        -----------
        symbol : str
            The ticker symbol (e.g., "AAPL", "GOOG", "BTC-USD").
        period : str, optional (default="1d")
            Time range for price data. Examples: "1d", "5d", "1mo", "3mo".
        interval : str, optional (default="1h")
            Granularity of the data. Examples: "1m", "5m", "1h", "1d".

        Returns:
        --------
        str
            A formatted string containing:
            - Company/ticker name
            - Current price and change
            - Open, High, Low prices
            - Volume
            - Period and interval used
        """
        try:
            ticker = yf.Ticker(symbol)

            # Calculate start and end dates based on period
            end_date = datetime.today()
            if period.endswith("d"):
                days = int(period[:-1])
            elif period.endswith("mo"):
                days = int(period[:-2]) * 30
            elif period.endswith("y"):
                days = int(period[:-1]) * 365
            else:
                days = 30  # default 1 month
            start_date = end_date - timedelta(days=days)

            # Fetch recent data explicitly
            data = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval=interval
            )

            if data.empty:
                return f"No data found for symbol '{symbol}'."

            latest = data.iloc[-1]
            current_price = round(latest["Close"], 2)
            open_price = round(latest["Open"], 2)
            change = round(current_price - open_price, 2)
            pct_change = round((change / open_price) * 100, 2)

            info = ticker.info
            long_name = info.get("longName", symbol)
            currency = info.get("currency", "USD")

            formatted = [
                f"📈 {long_name} ({symbol})",
                f"Current Price: {current_price} {currency}",
                f"Change: {change} ({pct_change}%)",
                f"Open: {open_price} | High: {round(latest['High'], 2)} | Low: {round(latest['Low'], 2)}",
                f"Volume: {int(latest['Volume'])}",
                f"Period: {period} | Interval: {interval}",
            ]
            return "\n".join(formatted)

        except Exception as e:
            return f"Error fetching data for '{symbol}': {e}"

    @staticmethod
    @function_tool
    @log_call
    def get_market_sentiment(symbol: str, period: str = "1mo") -> str:
        """
        Analyze recent price changes and provide a simple market sentiment.
        Uses dynamic start/end dates to ensure recent data.

        This tool computes the percentage change over the specified period and
        classifies the sentiment as:
        - Bullish (if price increased >2%)
        - Bearish (if price decreased >2%)
        - Neutral (otherwise)

        Parameters:
        -----------
        symbol : str
            The ticker symbol (e.g., "AAPL", "GOOG", "BTC-USD").
        period : str, optional (default="1mo")
            Time range to analyze. Examples: "7d", "1mo", "3mo".

        Returns:
        --------
        str
            A human-readable sentiment string including percentage change.
        """
        try:
            ticker = yf.Ticker(symbol)

            # Calculate start/end dynamically
            end_date = datetime.today()
            if period.endswith("d"):
                days = int(period[:-1])
            elif period.endswith("mo"):
                days = int(period[:-2]) * 30
            elif period.endswith("y"):
                days = int(period[:-1]) * 365
            else:
                days = 30
            start_date = end_date - timedelta(days=days)

            data = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )

            if data.empty:
                return f"No data for {symbol}."

            recent_change = data["Close"].iloc[-1] - data["Close"].iloc[0]
            pct_change = (recent_change / data["Close"].iloc[0]) * 100

            sentiment = "Neutral"
            if pct_change > 2:
                sentiment = "Bullish"
            elif pct_change < -2:
                sentiment = "Bearish"

            return f"{symbol} market sentiment ({period}): {sentiment} ({pct_change:.2f}% change)"

        except Exception as e:
            return f"Error fetching market sentiment for '{symbol}': {e}"

    @staticmethod
    @function_tool
    @log_call
    def get_history(symbol: str, period: str = "1mo") -> str:
        """
        Fetch historical price data for a given ticker.
        Ensures recent data is retrieved dynamically using start/end dates.

        Parameters:
        -----------
        symbol : str
            The ticker symbol (e.g., "AAPL", "GOOG", "BTC-USD").
        period : str, optional (default="1mo")
            The length of historical data to retrieve. Examples: "1d", "5d", "1mo", "3mo", "1y", "5y".

        Returns:
        --------
        str
            A formatted string showing the last 5 rows of historical prices (Open, High, Low, Close, Volume).
        """
        try:
            ticker = yf.Ticker(symbol)

            # Calculate start/end dynamically
            end_date = datetime.today()
            if period.endswith("d"):
                days = int(period[:-1])
            elif period.endswith("mo"):
                days = int(period[:-2]) * 30
            elif period.endswith("y"):
                days = int(period[:-1]) * 365
            else:
                days = 30
            start_date = end_date - timedelta(days=days)

            data = ticker.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d")
            )

            if data.empty:
                return f"No historical data found for '{symbol}'."
            return f"Historical data for {symbol} ({period}):\n{data.tail(5).to_string()}"

        except Exception as e:
            return f"Error fetching historical data for '{symbol}': {e}"
