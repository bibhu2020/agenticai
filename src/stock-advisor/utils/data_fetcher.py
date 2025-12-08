# utils/data_fetcher.py
"""
Data Fetcher Utilities
----------------------

Provides a lightweight interface for fetching market data, company information,
and financial statements from Yahoo Finance (via yfinance).

This module is designed for use by agents and higher-level tools, returning
pandas DataFrames or simple dictionaries for easy consumption.

Notes:
- For production, consider using a paid provider (Polygon, Alpha Vantage) for reliability.
- Handles errors gracefully and logs exceptions.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd
import yfinance as yf
import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

NEWS_API_KEY = os.getenv("NEWS_API_KEY", None)


@dataclass
class OHLCRequest:
    ticker: str
    period: str = "1y"      # e.g., "1d", "5d", "1mo", "6mo", "1y", "5y", "max"
    interval: str = "1d"    # e.g., "1m", "2m", "5m", "1d", "1wk"
    auto_adjust: bool = True
    prepost: bool = False


def fetch_ohlcv(req: str | OHLCRequest) -> pd.DataFrame:
    """
    Download OHLCV data using yfinance.
    Accepts either a ticker string or OHLCRequest.
    """
    if isinstance(req, str):
        req = OHLCRequest(ticker=req)

    logger.info("Fetching OHLCV for %s (%s @ %s)", req.ticker, req.period, req.interval)
    try:
        ticker = yf.Ticker(req.ticker)
        df = ticker.history(
            period=req.period,
            interval=req.interval,
            auto_adjust=req.auto_adjust,
            prepost=req.prepost,
        )
        if df.empty:
            logger.warning("No OHLCV data returned for %s", req.ticker)
        df = df.rename(columns=lambda c: c.strip())
        return df
    except Exception as e:
        logger.exception("Failed to fetch OHLCV for %s: %s", req.ticker, e)
        return pd.DataFrame()



def fetch_company_info(ticker: str) -> Dict:
    """
    Fetch basic company metadata using yfinance.

    Returns a dictionary with keys:
    ['ticker', 'longName', 'sector', 'industry', 'website', 'marketCap', 'country', 'currency', 'logo_url', 'summary']
    """
    logger.info("Fetching company info for %s", ticker)
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        return {
            "ticker": ticker.upper(),
            "longName": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "marketCap": info.get("marketCap"),
            "country": info.get("country"),
            "currency": info.get("currency"),
            "logo_url": info.get("logo_url"),
            "summary": info.get("longBusinessSummary") or info.get("shortBusinessSummary"),
        }
    except Exception as e:
        logger.exception("Failed to fetch company info for %s: %s", ticker, e)
        return {"ticker": ticker.upper(), "error": str(e)}


def fetch_financials(ticker: str, statements: Optional[list] = None) -> Dict[str, pd.DataFrame]:
    """
    Fetch financial statements (income, balance sheet, cashflow, earnings).

    Returns a dictionary mapping statement name -> DataFrame.
    """
    logger.info("Fetching financials for %s", ticker)
    try:
        t = yf.Ticker(ticker)
        res = {
            "financials": t.financials if (statements is None or "financials" in statements) else pd.DataFrame(),
            "balance_sheet": t.balance_sheet if (statements is None or "balance_sheet" in statements) else pd.DataFrame(),
            "cashflow": t.cashflow if (statements is None or "cashflow" in statements) else pd.DataFrame(),
            "earnings": t.earnings if (statements is None or "earnings" in statements) else pd.DataFrame(),
        }
        return res
    except Exception as e:
        logger.exception("Failed to fetch financials for %s: %s", ticker, e)
        return {"error": str(e)}


def fetch_latest_price(ticker: str) -> Optional[float]:
    """
    Return the latest known close price for a ticker, or None if unavailable.
    """
    logger.debug("Fetching latest price for %s", ticker)
    try:
        t = yf.Ticker(ticker)
        price = t.info.get("regularMarketPrice") if t.info else None
        if price is None:
            hist = t.history(period="2d", interval="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        return price
    except Exception as e:
        logger.exception("Failed to fetch latest price for %s: %s", ticker, e)
        return None


def search_tickers_by_company(name: str, limit: int = 5) -> list:
    """
    Fuzzy search tickers by company name using Yahoo query endpoint.

    Returns a list of dicts with keys:
    ['symbol', 'shortname', 'exch', 'type']
    """
    logger.info("Searching tickers for company name: %s", name)
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": name, "quotesCount": limit, "newsCount": 0}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        quotes = r.json().get("quotes", [])[:limit]
        results = []
        for q in quotes:
            results.append({
                "symbol": q.get("symbol"),
                "shortname": q.get("shortname") or q.get("longname"),
                "exch": q.get("exchDisp"),
                "type": q.get("quoteType"),
            })
        return results
    except Exception as e:
        logger.exception("Ticker search failed for %s: %s", name, e)
        return []
