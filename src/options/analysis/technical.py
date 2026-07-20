"""
Technical analysis — scores a stock 0.0–1.0 for sell-put suitability.
Higher score = better candidate (uptrend, not overbought, good IV context).
"""
import logging
import pandas as pd
import numpy as np

from data.fetcher import get_stock_data, get_iv_rank

logger = logging.getLogger(__name__)


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _macd(close: pd.Series):
    fast = _ema(close, 12)
    slow = _ema(close, 26)
    macd_line   = fast - slow
    signal_line = _ema(macd_line, 9)
    return macd_line, signal_line


def _bollinger(close: pd.Series, period: int = 20):
    sma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    pct_b = (close - lower) / (upper - lower + 1e-9)
    return sma, upper, lower, pct_b


def compute_technical_score(ticker: str, params: dict = None) -> dict:
    """
    Returns a dict:
      score       : float 0–1
      rsi         : float
      macd_signal : str  (BULLISH|BEARISH|NEUTRAL)
      above_50ma  : bool
      above_200ma : bool
      iv_rank     : float
      bb_pct_b    : float
      trend       : str
    """
    result = {
        "score": 0.5,
        "rsi": 50.0,
        "macd_signal": "NEUTRAL",
        "above_50ma": False,
        "above_200ma": False,
        "iv_rank": 50.0,
        "bb_pct_b": 0.5,
        "trend": "NEUTRAL",
    }

    df = get_stock_data(ticker, period="1y")
    if df is None or len(df) < 50:
        logger.warning("Not enough data for %s technical analysis", ticker)
        return result

    close = df["Close"]
    volume = df["Volume"]

    # ── Trend ────────────────────────────────────────────────────────────────
    ma50  = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    price = close.iloc[-1]

    above_50  = price > ma50.iloc[-1]
    above_200 = price > ma200.iloc[-1]

    # Uptrend: 50MA rising and above 200MA
    ma50_rising = ma50.iloc[-1] > ma50.iloc[-10]
    if above_50 and above_200 and ma50_rising:
        trend = "STRONG_UP"
    elif above_50 and ma50_rising:
        trend = "UP"
    elif not above_50 and not above_200:
        trend = "DOWN"
    else:
        trend = "NEUTRAL"

    # ── RSI ───────────────────────────────────────────────────────────────────
    rsi_series = _rsi(close)
    rsi_val = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

    # ── MACD ─────────────────────────────────────────────────────────────────
    macd_line, signal_line = _macd(close)
    if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
        macd_sig = "BULLISH_CROSS"
    elif macd_line.iloc[-1] > signal_line.iloc[-1]:
        macd_sig = "BULLISH"
    elif macd_line.iloc[-1] < signal_line.iloc[-1]:
        macd_sig = "BEARISH"
    else:
        macd_sig = "NEUTRAL"

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    _, _, _, pct_b = _bollinger(close)
    pct_b_val = float(pct_b.iloc[-1]) if not pct_b.empty else 0.5

    # ── Volume trend ──────────────────────────────────────────────────────────
    avg_vol_20 = volume.rolling(20).mean().iloc[-1]
    avg_vol_5  = volume.rolling(5).mean().iloc[-1]
    vol_rising = avg_vol_5 > avg_vol_20

    # ── IV Rank ───────────────────────────────────────────────────────────────
    iv_rank = get_iv_rank(ticker)

    # ── Scoring ───────────────────────────────────────────────────────────────
    # For sell-put we want: uptrend, RSI not overbought (30-65), moderate IV rank
    score = 0.0

    # Trend (0.35 weight)
    trend_scores = {
        "STRONG_UP": 1.0, "UP": 0.75, "NEUTRAL": 0.40, "DOWN": 0.10
    }
    score += 0.35 * trend_scores.get(trend, 0.4)

    # RSI (0.25 weight) — ideal for sell-put: 40-60 (not oversold/overbought)
    if 40 <= rsi_val <= 60:
        rsi_score = 1.0
    elif 30 <= rsi_val < 40 or 60 < rsi_val <= 70:
        rsi_score = 0.7
    elif rsi_val < 30:        # oversold — good opportunity but risky
        rsi_score = 0.5
    else:                     # overbought (>70) — avoid
        rsi_score = 0.2
    score += 0.25 * rsi_score

    # MACD (0.20 weight)
    macd_scores = {
        "BULLISH_CROSS": 1.0, "BULLISH": 0.75, "NEUTRAL": 0.50, "BEARISH": 0.20
    }
    score += 0.20 * macd_scores.get(macd_sig, 0.5)

    # IV Rank (0.20 weight) — moderate IV rank (30-70) ideal for premium selling
    if 30 <= iv_rank <= 70:
        iv_score = 1.0
    elif iv_rank > 70:        # very high IV — premium rich but risky
        iv_score = 0.7
    else:                     # low IV — not worth selling
        iv_score = 0.3
    score += 0.20 * iv_score

    result.update({
        "score":        round(min(max(score, 0), 1), 4),
        "rsi":          round(rsi_val, 2),
        "macd_signal":  macd_sig,
        "above_50ma":   bool(above_50),
        "above_200ma":  bool(above_200),
        "iv_rank":      iv_rank,
        "bb_pct_b":     round(pct_b_val, 4),
        "trend":        trend,
    })
    return result
