"""
Data fetching layer — wraps yfinance and free public sources.
All functions return plain dicts / DataFrames; callers handle DB writes.
"""
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Simple in-memory cache to avoid hammering yfinance
_CACHE: dict = {}
_CACHE_TTL = 300  # seconds


def _cached(key: str, ttl: int = _CACHE_TTL):
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["data"]
    return None


def _store(key: str, data):
    _CACHE[key] = {"data": data, "ts": time.time()}
    return data


# ── Stock price data ──────────────────────────────────────────────────────────

def get_stock_data(ticker: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """Return OHLCV DataFrame for the ticker."""
    key = f"hist_{ticker}_{period}"
    cached = _cached(key)
    if cached is not None:
        return cached
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, auto_adjust=True)
        if df.empty:
            return None
        return _store(key, df)
    except Exception as e:
        logger.warning("get_stock_data(%s) failed: %s", ticker, e)
        return None


def get_current_price(ticker: str) -> Optional[float]:
    """Return latest closing price."""
    df = get_stock_data(ticker, period="5d")
    if df is None or df.empty:
        return None
    return float(df["Close"].iloc[-1])


# ── Options chain ─────────────────────────────────────────────────────────────

def get_options_chain(ticker: str, min_dte: int = 14, max_dte: int = 28) -> list[dict]:
    """
    Return a list of put option contracts within the DTE window.
    Each dict has: expiry, strike, bid, ask, mid, iv, delta, volume, oi
    """
    key = f"options_{ticker}_{min_dte}_{max_dte}"
    cached = _cached(key, ttl=600)
    if cached is not None:
        return cached

    try:
        t = yf.Ticker(ticker)
        exps = t.options  # list of expiry date strings
        if not exps:
            return []

        today = datetime.now().date()
        results = []

        for exp_str in exps:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
            dte = (exp_date - today).days
            if dte < min_dte or dte > max_dte:
                continue

            chain = t.option_chain(exp_str)
            puts = chain.puts
            if puts.empty:
                continue

            for _, row in puts.iterrows():
                bid  = float(row.get("bid", 0) or 0)
                ask  = float(row.get("ask", 0) or 0)
                mid  = round((bid + ask) / 2, 4)
                iv   = float(row.get("impliedVolatility", 0) or 0)
                vol  = int(row.get("volume", 0) or 0)
                oi   = int(row.get("openInterest", 0) or 0)
                strike = float(row["strike"])
                delta = _estimate_delta(iv, strike, get_current_price(ticker) or strike, dte)

                if mid <= 0 or vol < 10:
                    continue

                results.append({
                    "expiry":  exp_str,
                    "dte":     dte,
                    "strike":  strike,
                    "bid":     bid,
                    "ask":     ask,
                    "mid":     mid,
                    "iv":      iv,
                    "delta":   delta,
                    "volume":  vol,
                    "open_interest": oi,
                })

        return _store(key, results)

    except Exception as e:
        logger.warning("get_options_chain(%s) failed: %s", ticker, e)
        return []


def _estimate_delta(iv: float, strike: float, spot: float, dte: int) -> float:
    """Simple Black-Scholes delta approximation (no mibian dependency)."""
    import math
    if iv <= 0 or spot <= 0 or dte <= 0:
        return 0.0
    try:
        T = dte / 365.0
        r = 0.05  # risk-free rate assumption
        d1 = (math.log(spot / strike) + (r + 0.5 * iv ** 2) * T) / (iv * math.sqrt(T))
        # Normal CDF approximation
        def ncdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        return ncdf(-d1)   # |put delta|; put delta itself is -ncdf(-d1)
    except Exception:
        return 0.0


def get_iv_rank(ticker: str) -> float:
    """
    Compute IV Rank (0-100) using 52-week high/low of historical volatility.
    Uses rolling 30-day realised vol as proxy for IV.
    """
    df = get_stock_data(ticker, period="1y")
    if df is None or len(df) < 30:
        return 50.0
    try:
        df["ret"] = df["Close"].pct_change()
        df["hv30"] = df["ret"].rolling(30).std() * (252 ** 0.5) * 100
        hv = df["hv30"].dropna()
        low, high = hv.min(), hv.max()
        current = hv.iloc[-1]
        if high == low:
            return 50.0
        return round((current - low) / (high - low) * 100, 1)
    except Exception:
        return 50.0


# ── Fundamentals ──────────────────────────────────────────────────────────────

def get_fundamentals(ticker: str) -> dict:
    """Return key fundamental metrics for the ticker."""
    key = f"fundamentals_{ticker}"
    cached = _cached(key, ttl=3600)
    if cached is not None:
        return cached

    try:
        t = yf.Ticker(ticker)
        info = t.info or {}

        data = {
            "pe_ratio":           info.get("trailingPE"),
            "forward_pe":         info.get("forwardPE"),
            "peg_ratio":          info.get("pegRatio"),
            "price_to_book":      info.get("priceToBook"),
            "debt_to_equity":     info.get("debtToEquity"),
            "current_ratio":      info.get("currentRatio"),
            "roe":                info.get("returnOnEquity"),
            "roa":                info.get("returnOnAssets"),
            "profit_margin":      info.get("profitMargins"),
            "revenue_growth":     info.get("revenueGrowth"),
            "earnings_growth":    info.get("earningsGrowth"),
            "dividend_yield":     info.get("dividendYield"),
            "market_cap":         info.get("marketCap"),
            "sector":             info.get("sector"),
            "industry":           info.get("industry"),
            "beta":               info.get("beta"),
            "52w_high":           info.get("fiftyTwoWeekHigh"),
            "52w_low":            info.get("fiftyTwoWeekLow"),
            "50d_ma":             info.get("fiftyDayAverage"),
            "200d_ma":            info.get("twoHundredDayAverage"),
            "short_ratio":        info.get("shortRatio"),
            "earnings_date":      _next_earnings(info),
        }
        return _store(key, data)
    except Exception as e:
        logger.warning("get_fundamentals(%s) failed: %s", ticker, e)
        return {}


def _next_earnings(info: dict) -> Optional[str]:
    ts = info.get("earningsTimestamp") or info.get("earningsTimestampStart")
    if ts:
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        except Exception:
            pass
    return None


# ── S&P 500 ticker list ───────────────────────────────────────────────────────

def get_sp500_tickers() -> list[str]:
    """Fetch current S&P 500 constituents from Wikipedia (free, no key)."""
    key = "sp500_tickers"
    cached = _cached(key, ttl=86400)  # cache 24h
    if cached is not None:
        return cached
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url, header=0)
        tickers = tables[0]["Symbol"].tolist()
        # Clean BRK.B → BRK-B for yfinance
        tickers = [t.replace(".", "-") for t in tickers]
        return _store(key, tickers)
    except Exception as e:
        logger.warning("get_sp500_tickers failed: %s – using default list", e)
        import config
        return config.DEFAULT_UNIVERSE


# ── News headlines (free, no API key) ────────────────────────────────────────

def get_yahoo_news(ticker: str, limit: int = 10) -> list[str]:
    """Fetch recent news headlines via yfinance."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        headlines = []
        for item in news[:limit]:
            title = item.get("title") or item.get("content", {}).get("title", "")
            if title:
                headlines.append(title)
        return headlines
    except Exception:
        return []


def get_google_news_rss(ticker: str, limit: int = 10) -> list[str]:
    """Scrape Google News RSS feed for a ticker (completely free)."""
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")[:limit]
        return [item.find("title").get_text() for item in items if item.find("title")]
    except Exception:
        return []


def get_finviz_news(ticker: str, limit: int = 10) -> list[str]:
    """Scrape headlines from Finviz quote page (free)."""
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="fullview-news-outer")
        if not table:
            return []
        links = table.find_all("a", class_="tab-link-news")[:limit]
        return [a.get_text() for a in links]
    except Exception:
        return []


def get_reddit_mentions(ticker: str, subreddits: list[str] = None) -> list[str]:
    """
    Fetch Reddit posts mentioning the ticker using old.reddit.com JSON API.
    No API key needed — uses public JSON endpoints.
    """
    if subreddits is None:
        subreddits = ["wallstreetbets", "stocks", "options"]

    posts = []
    headers = {"User-Agent": "options-paper-trader/1.0"}

    for sub in subreddits[:2]:   # limit to 2 subs to avoid rate limits
        try:
            url = f"https://old.reddit.com/r/{sub}/search.json?q={ticker}&sort=new&limit=10&restrict_sr=on"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for child in data.get("data", {}).get("children", []):
                title = child.get("data", {}).get("title", "")
                if ticker.upper() in title.upper() and title:
                    posts.append(title)
        except Exception:
            continue
        time.sleep(0.5)  # be polite

    return posts


def get_all_news(ticker: str) -> list[str]:
    """Aggregate headlines from all free sources."""
    headlines = []
    headlines += get_yahoo_news(ticker, limit=8)
    headlines += get_google_news_rss(ticker, limit=8)
    headlines += get_finviz_news(ticker, limit=5)
    headlines += get_reddit_mentions(ticker)
    # Deduplicate
    seen = set()
    unique = []
    for h in headlines:
        h_clean = h.strip()
        if h_clean and h_clean not in seen:
            seen.add(h_clean)
            unique.append(h_clean)
    return unique
