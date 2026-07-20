"""
Self-tuning algorithm — evaluates recent performance every 30 days
and adjusts algo parameters if win rate or P&L is below threshold.
"""
import logging
from datetime import datetime, timedelta

import config
from database.models import (
    get_closed_trades_since, get_algo_params, update_algo_param,
    record_performance, log_event, get_portfolio
)

logger = logging.getLogger(__name__)


def run_self_tune():
    """
    Compute performance metrics for the last 30 days.
    If performance is below threshold, tighten/adjust parameters.
    """
    log_event("self_tuner", "Starting 30-day self-tuning cycle")

    period_end   = datetime.now()
    period_start = period_end - timedelta(days=config.TUNE_INTERVAL_DAYS)

    trades = get_closed_trades_since(period_start.strftime("%Y-%m-%d %H:%M:%S"))

    if not trades:
        log_event("self_tuner", "No closed trades in period — skipping tune")
        return

    total     = len(trades)
    winners   = [t for t in trades if t["pnl"] > 0]
    win_rate  = len(winners) / total if total else 0
    total_pnl = sum(t["pnl"] for t in trades)
    avg_pnl   = total_pnl / total if total else 0
    portfolio = get_portfolio()

    record_performance(
        period_start    = period_start.strftime("%Y-%m-%d"),
        period_end      = period_end.strftime("%Y-%m-%d"),
        total_trades    = total,
        winning_trades  = len(winners),
        win_rate        = round(win_rate, 4),
        total_pnl       = round(total_pnl, 2),
        avg_pnl         = round(avg_pnl, 2),
        portfolio_value = portfolio["total_value"],
    )

    params = get_algo_params()

    needs_tune = (
        win_rate  < config.MIN_WIN_RATE_BEFORE_TUNE or
        total_pnl < config.MIN_PNL_BEFORE_TUNE
    )

    log_event(
        "self_tuner",
        f"Period: trades={total}, win_rate={win_rate:.1%}, "
        f"P&L=${total_pnl:.2f} | needs_tune={needs_tune}"
    )

    if not needs_tune:
        log_event("self_tuner", "Performance OK — no tuning needed")
        return

    # ── Tuning actions ────────────────────────────────────────────────────────

    # 1. Raise min composite score threshold (be more selective)
    current_min = params.get("min_score_to_trade", config.MIN_SCORE_TO_TRADE)
    new_min     = min(current_min + 0.05, 0.80)
    update_algo_param("min_score_to_trade", new_min)
    log_event("self_tuner", f"Raised min_score_to_trade: {current_min:.2f} → {new_min:.2f}")

    # 2. Move delta target lower (more OTM puts = safer but less premium)
    current_delta = params.get("target_delta", config.TARGET_DELTA)
    new_delta     = max(current_delta - 0.03, 0.15)
    update_algo_param("target_delta", new_delta)
    log_event("self_tuner", f"Lowered target_delta: {current_delta:.2f} → {new_delta:.2f}")

    # 3. Adjust score weights based on which sub-score correlated with losses
    _tune_weights(trades, params)

    # 4. Increase OTM buffer (require puts to be further OTM)
    current_buf = params.get("otm_buffer_pct", config.OTM_BUFFER_PCT)
    new_buf     = min(current_buf + 0.01, 0.12)
    update_algo_param("otm_buffer_pct", new_buf)
    log_event("self_tuner", f"Increased OTM buffer: {current_buf:.2%} → {new_buf:.2%}")

    log_event("self_tuner", "Self-tuning complete")


MIN_SCORED_TRADES_FOR_REWEIGHT = 5

# Position field -> (algo param name, config default)
SCORE_DIMENSIONS = {
    "signal_technical_score":   ("weight_technical",   config.WEIGHT_TECHNICAL),
    "signal_fundamental_score": ("weight_fundamental", config.WEIGHT_FUNDAMENTAL),
    "signal_sentiment_score":   ("weight_sentiment",   config.WEIGHT_SENTIMENT),
}

WEIGHT_FLOOR = 0.10   # never let a dimension's weight collapse to ~0
MAX_STEP     = 0.05   # largest single-cycle nudge for the most decisive dimension


def _tune_weights(trades: list[dict], params: dict):
    """
    Adjust scoring weights using the actual sub-scores (technical/fundamental/
    sentiment) recorded on the signal that opened each trade.

    For each dimension we compare the average sub-score among winning trades
    vs losing trades. A dimension where winners scored meaningfully higher
    than losers is discriminating well — its weight goes up. A dimension
    that's flat, or where losers scored as high or higher, isn't earning its
    weight — it goes down.
    """
    scored = [
        t for t in trades
        if all(t.get(f) is not None for f in SCORE_DIMENSIONS)
    ]

    if len(scored) < MIN_SCORED_TRADES_FOR_REWEIGHT:
        log_event(
            "self_tuner",
            f"Only {len(scored)} closed trades have linked signal scores "
            f"(need {MIN_SCORED_TRADES_FOR_REWEIGHT}) — skipping weight rebalance"
        )
        return

    winners = [t for t in scored if t["pnl"] > 0]
    losers  = [t for t in scored if t["pnl"] <= 0]

    if not winners or not losers:
        log_event("self_tuner",
                  "Need both winning and losing trades to rebalance weights — skipping")
        return

    diffs = {}
    for field in SCORE_DIMENSIONS:
        win_avg  = sum(t[field] for t in winners) / len(winners)
        lose_avg = sum(t[field] for t in losers) / len(losers)
        diffs[field] = win_avg - lose_avg   # >0: dimension separates winners from losers

    max_abs_diff = max(abs(d) for d in diffs.values()) or 1.0

    new_weights = {}
    for field, (param_name, default) in SCORE_DIMENSIONS.items():
        current = params.get(param_name, default)
        nudge   = MAX_STEP * (diffs[field] / max_abs_diff)   # scaled into [-MAX_STEP, MAX_STEP]
        new_weights[field] = max(current + nudge, WEIGHT_FLOOR)

    total = sum(new_weights.values())
    for field, (param_name, _default) in SCORE_DIMENSIONS.items():
        update_algo_param(param_name, round(new_weights[field] / total, 4))

    log_event(
        "self_tuner",
        "Weight rebalance (data-driven, n={}) → tech={:.2f} (Δwin-lose={:+.3f}) "
        "fund={:.2f} (Δ={:+.3f}) sent={:.2f} (Δ={:+.3f})".format(
            len(scored),
            new_weights["signal_technical_score"]   / total, diffs["signal_technical_score"],
            new_weights["signal_fundamental_score"] / total, diffs["signal_fundamental_score"],
            new_weights["signal_sentiment_score"]   / total, diffs["signal_sentiment_score"],
        )
    )
