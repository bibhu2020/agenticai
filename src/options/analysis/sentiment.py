"""
Sentiment analysis using VADER on free news + Reddit sources.
Returns a score 0.0–1.0 (0=very negative, 0.5=neutral, 1=very positive).
"""
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from data.fetcher import get_all_news

logger = logging.getLogger(__name__)

_analyzer = SentimentIntensityAnalyzer()


def _vader_compound(text: str) -> float:
    """Return VADER compound score (-1 to 1)."""
    try:
        return _analyzer.polarity_scores(text)["compound"]
    except Exception:
        return 0.0


def _normalise(compound: float) -> float:
    """Map VADER compound (-1 to 1) → 0 to 1."""
    return round((compound + 1) / 2, 4)


def compute_sentiment_score(ticker: str, params: dict = None) -> dict:
    """
    Returns:
      score          : float 0–1
      compound       : float (-1 to 1)
      headline_count : int
      sample_headlines : list[str]
    """
    result = {
        "score":             0.5,
        "compound":          0.0,
        "headline_count":    0,
        "sample_headlines":  [],
    }

    headlines = get_all_news(ticker)
    if not headlines:
        logger.info("No headlines found for %s — neutral sentiment", ticker)
        return result

    scores = [_vader_compound(h) for h in headlines]
    if not scores:
        return result

    # Weighted average: recent headlines (first in list) weight more
    weights = [1 / (i + 1) for i in range(len(scores))]
    total_w = sum(weights)
    compound = sum(s * w for s, w in zip(scores, weights)) / total_w

    result.update({
        "score":             _normalise(compound),
        "compound":          round(compound, 4),
        "headline_count":    len(headlines),
        "sample_headlines":  headlines[:5],
    })
    return result
