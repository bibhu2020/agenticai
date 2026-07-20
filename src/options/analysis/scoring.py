"""
Composite scoring — combines technical, fundamental and sentiment scores
using dynamically tunable weights from the database.
"""
import logging
from database.models import get_algo_params
from .technical    import compute_technical_score
from .fundamentals import compute_fundamental_score
from .sentiment    import compute_sentiment_score

logger = logging.getLogger(__name__)

_DEFAULT_WEIGHTS = {
    "weight_technical":   0.35,
    "weight_fundamental": 0.30,
    "weight_sentiment":   0.35,
}


def compute_composite_score(ticker: str) -> dict:
    """
    Run all three sub-analyses and combine into a composite score.

    Returns a flat dict suitable for creating a signal record:
      composite_score, technical_score, fundamental_score, sentiment_score,
      plus all sub-analysis fields for display.
    """
    # Load live params (may have been updated by self-tuner)
    try:
        params = get_algo_params()
    except Exception:
        params = {}

    w_tech  = params.get("weight_technical",   _DEFAULT_WEIGHTS["weight_technical"])
    w_fund  = params.get("weight_fundamental", _DEFAULT_WEIGHTS["weight_fundamental"])
    w_sent  = params.get("weight_sentiment",   _DEFAULT_WEIGHTS["weight_sentiment"])

    # Normalise weights in case they don't sum to 1
    total = w_tech + w_fund + w_sent
    if total > 0:
        w_tech /= total; w_fund /= total; w_sent /= total

    tech  = compute_technical_score(ticker, params)
    fund  = compute_fundamental_score(ticker, params)
    sent  = compute_sentiment_score(ticker, params)

    composite = (
        w_tech  * tech["score"] +
        w_fund  * fund["score"] +
        w_sent  * sent["score"]
    )

    result = {
        # composite
        "composite_score":    round(composite, 4),
        "technical_score":    tech["score"],
        "fundamental_score":  fund["score"],
        "sentiment_score":    sent["score"],
        # technical details
        "rsi":                tech.get("rsi"),
        "macd_signal":        tech.get("macd_signal"),
        "above_50ma":         tech.get("above_50ma"),
        "above_200ma":        tech.get("above_200ma"),
        "iv_rank":            tech.get("iv_rank"),
        "trend":              tech.get("trend"),
        # fundamental details
        "pe_ratio":           fund.get("pe_ratio"),
        "debt_to_equity":     fund.get("debt_to_equity"),
        "beta":               fund.get("beta"),
        "earnings_date":      fund.get("earnings_date"),
        "sector":             fund.get("sector"),
        "market_cap":         fund.get("market_cap"),
        # sentiment details
        "sentiment_compound": sent.get("compound"),
        "headline_count":     sent.get("headline_count"),
        "sample_headlines":   sent.get("sample_headlines", []),
    }

    logger.info(
        "%s → composite=%.3f  tech=%.3f  fund=%.3f  sent=%.3f",
        ticker, composite, tech["score"], fund["score"], sent["score"]
    )
    return result
