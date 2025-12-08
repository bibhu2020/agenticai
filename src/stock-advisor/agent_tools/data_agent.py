"""
Data Agent
----------

The DataAgent provides a standardized interface to fetch financial and market data
for stocks. It wraps low-level data provider APIs (currently yfinance) and exposes
functions that are commonly needed by other agents in the system.

Responsibilities:
- Fetch OHLCV (Open, High, Low, Close, Volume) market data.
- Retrieve basic company metadata (industry, sector, market cap, etc.).
- Fetch financial statements (income, balance sheet, cashflow).
- Provide latest stock prices.
- Search for tickers based on company names.

Notes:
- This agent is read-only and intended as a data source. It does not perform
  any trading or portfolio management.
- For production, consider swapping yfinance with a paid provider for higher
  reliability and coverage.
- All functions return simple, predictable Python structures (dicts, pandas DataFrames)
  suitable for downstream agents or analysis.
- Logging is enabled to capture errors, warnings, and info messages.

Example Usage:

    from agents.data_agent import DataAgent

    agent = DataAgent()

    # Fetch company info
    info = agent.company("AAPL")
    print(info)

    # Fetch OHLCV data for 1 month, daily interval
    df = agent.ohlcv("AAPL", period="1mo", interval="1d")
    print(df.tail(3))

    # Fetch financial statements
    fin = agent.financials("AAPL")
    print(fin["financials"].head())

    # Get latest market price
    price = agent.latest_price("AAPL")
    print(price)

    # Search for tickers
    matches = agent.search("Apple")
    print(matches)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from utils.data_fetcher import (
    fetch_ohlcv,
    fetch_company_info,
    fetch_financials,
    fetch_latest_price,
    search_tickers_by_company,
)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


@dataclass
class OHLCRequest:
    """
    Encapsulates a request for OHLCV data.

    Attributes:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        period (str): Historical period to fetch (default: "1y").
        interval (str): Interval between data points (default: "1d").
        auto_adjust (bool): Whether to adjust OHLC for splits/dividends (default: True).
        prepost (bool): Include pre-market and post-market data (default: False).
    """
    ticker: str
    period: str = "1y"
    interval: str = "1d"
    auto_adjust: bool = True
    prepost: bool = False


class DataAgent:
    """
    A high-level data agent for market data and company info.

    Methods:
        ohlcv(ticker, period, interval): Returns OHLCV data as a pandas DataFrame.
        company(ticker): Returns company metadata as a dictionary.
        financials(ticker): Returns financial statements as a dict of DataFrames.
        latest_price(ticker): Returns the most recent market price.
        search(name, limit): Returns a list of ticker matches for a company name.
    """

    def __init__(self):
        self.name = "DataAgent"

    def ohlcv(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch OHLCV data for a given ticker.

        Args:
            ticker (str): Stock symbol, e.g., "AAPL".
            period (str): Historical period, e.g., "1mo", "1y".
            interval (str): Data interval, e.g., "1d", "1wk".

        Returns:
            pd.DataFrame: OHLCV data indexed by datetime.
        """
        req = OHLCRequest(ticker=ticker, period=period, interval=interval)
        return fetch_ohlcv(req)

    def company(self, ticker: str) -> Dict:
        """
        Fetch basic company information.

        Args:
            ticker (str): Stock symbol.

        Returns:
            dict: Company metadata including longName, sector, industry, marketCap, etc.
        """
        return fetch_company_info(ticker)

    def financials(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Fetch financial statements for a company.

        Args:
            ticker (str): Stock symbol.

        Returns:
            dict: Keys are "financials", "balance_sheet", "cashflow", each a DataFrame.
        """
        return fetch_financials(ticker)

    def latest_price(self, ticker: str) -> Optional[float]:
        """
        Get the latest market price for a stock.

        Args:
            ticker (str): Stock symbol.

        Returns:
            float | None: Most recent price or None if unavailable.
        """
        return fetch_latest_price(ticker)

    def search(self, name: str, limit: int = 5) -> list:
        """
        Search tickers by company name using Yahoo Finance query endpoint.

        Args:
            name (str): Partial or full company name.
            limit (int): Maximum number of results to return.

        Returns:
            list: List of dicts containing symbol, shortname, exchange, and type.
        """
        return search_tickers_by_company(name, limit)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level="INFO")
    agent = DataAgent()

    print(agent.company("AAPL"))
    df = agent.ohlcv("AAPL", period="1mo", interval="1d")
    print(df.tail(3))
