"""
Universe scanner — finds the best sell-put candidates.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import config
from data.fetcher import get_sp500_tickers, get_current_price, get_options_chain
from analysis.scoring import compute_composite_score
from database.models import get_algo_params, create_signal, log_event

logger = logging.getLogger(__name__)

MAX_WORKERS = 8   # concurrent tickers to analyse


def _analyse_ticker(ticker: str, params: dict) -> Optional[dict]:
    """Analyse one ticker; return signal dict or None if not worth trading."""
    try:
        price = get_current_price(ticker)
        if not price or price < 5:    # skip penny stocks
            return None

        scores = compute_composite_score(ticker)
        min_score = params.get("min_score_to_trade", config.MIN_SCORE_TO_TRADE)

        if scores["composite_score"] < min_score:
            return None

        # Find best put option
        min_dte = int(params.get("min_dte", config.MIN_DTE))
        max_dte = int(params.get("max_dte", config.MAX_DTE))
        options = get_options_chain(ticker, min_dte=min_dte, max_dte=max_dte)

        if not options:
            return None

        target_delta = params.get("target_delta", config.TARGET_DELTA)
        otm_buffer   = params.get("otm_buffer_pct", config.OTM_BUFFER_PCT)

        best = _select_best_put(options, price, target_delta, otm_buffer)
        if not best:
            return None

        signal = {
            "ticker":              ticker,
            "current_price":       price,
            "scores":              {
                "composite":   scores["composite_score"],
                "technical":   scores["technical_score"],
                "fundamental": scores["fundamental_score"],
                "sentiment":   scores["sentiment_score"],
            },
            "details":             scores,
            "strike":              best["strike"],
            "expiry":              best["expiry"],
            "premium":             best["mid"],
            "iv":                  best["iv"],
            "delta":               best["delta"],
            "dte":                 best["dte"],
        }
        return signal

    except Exception as e:
        logger.warning("Error analysing %s: %s", ticker, e)
        return None


def _select_best_put(options: list[dict], price: float,
                     target_delta: float, otm_buffer: float) -> Optional[dict]:
    """
    From the available puts pick the one closest to our target delta
    that is also sufficiently OTM.
    """
    min_strike = price * (1 - otm_buffer)   # at least 5% OTM

    candidates = [
        o for o in options
        if o["strike"] <= min_strike and o["delta"] > 0 and o["mid"] > 0.05
    ]

    if not candidates:
        return None

    # Sort by closeness to target delta
    candidates.sort(key=lambda o: abs(o["delta"] - target_delta))
    return candidates[0]


def scan_universe(tickers: list[str] = None) -> list[dict]:
    """
    Scan the given tickers (or default universe) and return ranked signals.
    Writes signal records to DB.
    """
    if not tickers:
        try:
            tickers = get_sp500_tickers()
        except Exception:
            tickers = config.DEFAULT_UNIVERSE

    params = {}
    try:
        params = get_algo_params()
    except Exception:
        pass

    log_event("scanner", f"Starting scan of {len(tickers)} tickers")

    signals = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_analyse_ticker, t, params): t for t in tickers}
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                signals.append(result)

    # Sort by composite score descending
    signals.sort(key=lambda s: s["scores"]["composite"], reverse=True)

    # Persist signals to DB — every candidate, not just the top slice, so any
    # signal that strategy.py later trades on has a signal_id to link back to
    # for self-tuning (see scheduler/self_tuner.py::_tune_weights).
    for sig in signals:
        try:
            sig["signal_id"] = create_signal(
                ticker   = sig["ticker"],
                scores   = sig["scores"],
                price    = sig["current_price"],
                strike   = sig["strike"],
                expiry   = sig["expiry"],
                premium  = sig["premium"],
                iv       = sig["iv"],
            )
        except Exception as e:
            logger.warning("Failed to persist signal for %s: %s", sig["ticker"], e)

    log_event("scanner", f"Scan complete — {len(signals)} candidates found")
    return signals
