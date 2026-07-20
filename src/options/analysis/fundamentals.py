"""
Fundamental analysis — scores a stock 0.0–1.0 based on financial health.
For sell-put strategy we prefer financially strong companies less likely to crash.
"""
import logging
from data.fetcher import get_fundamentals

logger = logging.getLogger(__name__)


def _score_pe(pe) -> float:
    """P/E ratio: prefer 10-25 range (not too cheap/expensive)."""
    if pe is None or pe <= 0:
        return 0.4
    if 10 <= pe <= 25:
        return 1.0
    if 25 < pe <= 40:
        return 0.7
    if pe > 40:
        return 0.4
    if pe < 10:  # could be value trap
        return 0.5
    return 0.4


def _score_debt(de) -> float:
    """Debt-to-equity: lower is better."""
    if de is None:
        return 0.5
    if de < 0.5:
        return 1.0
    if de < 1.0:
        return 0.8
    if de < 2.0:
        return 0.6
    if de < 4.0:
        return 0.3
    return 0.1


def _score_growth(g) -> float:
    """Revenue/earnings growth: higher is better."""
    if g is None:
        return 0.5
    if g > 0.20:
        return 1.0
    if g > 0.10:
        return 0.8
    if g > 0.0:
        return 0.6
    if g > -0.10:
        return 0.4
    return 0.2


def _score_roe(roe) -> float:
    """Return on equity: higher is better."""
    if roe is None:
        return 0.5
    if roe > 0.25:
        return 1.0
    if roe > 0.15:
        return 0.8
    if roe > 0.05:
        return 0.6
    if roe > 0:
        return 0.4
    return 0.2


def _score_beta(beta) -> float:
    """
    Beta: for sell-put we prefer moderate beta (0.5–1.5).
    Very high beta = volatile, risky for put sellers.
    """
    if beta is None:
        return 0.5
    if 0.5 <= beta <= 1.2:
        return 1.0
    if 1.2 < beta <= 1.8:
        return 0.7
    if beta > 1.8:
        return 0.4
    if beta < 0.5:  # defensive / low vol — low premium
        return 0.6
    return 0.5


def _score_earnings_proximity(earnings_date: str) -> float:
    """
    Penalise stocks with earnings within the option's DTE window (2-4 weeks).
    Earnings = volatility event we don't want to sell through.
    """
    if not earnings_date:
        return 0.8  # unknown → slight penalty
    from datetime import datetime, timedelta
    try:
        ed = datetime.strptime(earnings_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_to_earnings = (ed - today).days
        if 0 < days_to_earnings <= 28:
            return 0.1   # earnings during our window — avoid!
        if 28 < days_to_earnings <= 45:
            return 0.6   # getting close
        return 1.0       # earnings not imminent
    except Exception:
        return 0.8


def compute_fundamental_score(ticker: str, params: dict = None) -> dict:
    """
    Returns:
      score          : float 0–1
      pe_ratio       : float
      debt_to_equity : float
      roe            : float
      earnings_growth: float
      beta           : float
      earnings_date  : str
      market_cap     : int
    """
    result = {
        "score":          0.5,
        "pe_ratio":       None,
        "debt_to_equity": None,
        "roe":            None,
        "earnings_growth": None,
        "beta":           None,
        "earnings_date":  None,
        "market_cap":     None,
        "sector":         None,
    }

    info = get_fundamentals(ticker)
    if not info:
        logger.warning("No fundamentals for %s", ticker)
        return result

    pe       = info.get("pe_ratio")
    de       = info.get("debt_to_equity")
    roe      = info.get("roe")
    eg       = info.get("earnings_growth")
    rg       = info.get("revenue_growth")
    beta     = info.get("beta")
    ed       = info.get("earnings_date")
    mcap     = info.get("market_cap", 0) or 0
    margin   = info.get("profit_margin")

    # Only consider mid/large-cap (>$5B) — better liquidity for options
    if mcap > 0 and mcap < 5e9:
        result["market_cap"] = mcap
        result["score"] = 0.2  # small cap — skip
        return result

    # Weighted scoring
    score = (
        0.20 * _score_pe(pe) +
        0.20 * _score_debt(de) +
        0.15 * _score_roe(roe) +
        0.15 * _score_growth(eg or rg) +
        0.15 * _score_beta(beta) +
        0.15 * _score_earnings_proximity(ed)
    )

    # Bonus: profitable company (positive margin)
    if margin and margin > 0.10:
        score = min(score + 0.05, 1.0)

    result.update({
        "score":           round(min(max(score, 0), 1), 4),
        "pe_ratio":        pe,
        "debt_to_equity":  de,
        "roe":             roe,
        "earnings_growth": eg,
        "beta":            beta,
        "earnings_date":   ed,
        "market_cap":      mcap,
        "sector":          info.get("sector"),
    })
    return result
