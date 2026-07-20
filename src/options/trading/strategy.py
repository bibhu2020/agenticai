"""
Strategy layer — decides which signals to execute as sell-put orders.
"""
import logging
from datetime import datetime

import config
from database.models import (
    get_portfolio, get_open_positions, get_algo_params,
    update_signal, log_event
)
from data.fetcher import get_current_price, get_options_chain
from .paper_broker import PaperBroker

logger = logging.getLogger(__name__)
broker = PaperBroker()


def select_put_to_sell(signals: list[dict]) -> list[dict]:
    """
    Given ranked signals from the scanner, decide which ones to trade.
    Returns the list of executed trade results.
    """
    params       = get_algo_params()
    portfolio    = get_portfolio()
    open_pos     = get_open_positions()
    put_count    = sum(1 for p in open_pos if p["position_type"] == "SELL_PUT")
    max_pos      = int(params.get("max_open_positions", config.MAX_OPEN_POSITIONS))
    max_size_pct = params.get("max_position_size_pct", config.MAX_POSITION_SIZE_PCT)

    if put_count >= max_pos:
        log_event("strategy", f"Max positions reached ({max_pos}) — skipping scan results")
        return []

    total_value  = portfolio["total_value"]
    cash         = portfolio["cash"]
    executed     = []
    open_tickers = {p["ticker"] for p in open_pos}

    slots_available = max_pos - put_count

    for sig in signals[:slots_available * 2]:   # look at top 2× slots
        ticker = sig["ticker"]

        # Skip if already have a position in this ticker
        if ticker in open_tickers:
            continue

        strike  = sig["strike"]
        expiry  = sig["expiry"]
        premium = sig["premium"]
        price   = sig["current_price"]

        if not (strike and expiry and premium and price):
            continue

        # Position sizing: max 20% of total portfolio value as margin
        contracts     = 1
        margin_needed = round(strike * contracts * 100 * 0.20, 2)
        max_margin    = round(total_value * max_size_pct, 2)

        if margin_needed > max_margin:
            log_event("strategy", f"Skip {ticker}: margin ${margin_needed:.0f} > limit ${max_margin:.0f}")
            continue

        if margin_needed > cash * 0.90:  # keep 10% cash buffer
            log_event("strategy", f"Skip {ticker}: insufficient cash")
            continue

        result = broker.sell_put(
            ticker           = ticker,
            strike           = strike,
            expiry           = expiry,
            premium          = premium,
            contracts        = contracts,
            underlying_price = price,
            signal_id        = sig.get("signal_id"),
        )

        if result["success"]:
            executed.append({
                "ticker":      ticker,
                "position_id": result["position_id"],
                "credit":      result["credit"],
                "strike":      strike,
                "expiry":      expiry,
            })
            open_tickers.add(ticker)

            if len(executed) >= slots_available:
                break

    return executed
