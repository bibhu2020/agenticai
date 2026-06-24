"""Tests for Agora (market-analyst) — pure utility functions."""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_agora_backend = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src/market-analyst/backend")
)
if _agora_backend not in sys.path:
    sys.path.insert(0, _agora_backend)

# Stub yfinance so tests run without network access
sys.modules.setdefault("yfinance", MagicMock())
sys.modules.setdefault("pandas", MagicMock())

from tools.market_data import normalize_period
from tools.pl_calculator import calculate_strategy_metrics


# ── normalize_period ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("1yr",    "1y"),
    ("1year",  "1y"),
    ("3mo",    "3mo"),
    ("3month", "3mo"),
    ("1mo",    "1mo"),
    ("1month", "1mo"),
    ("1wk",    "1wk"),
    ("1week",  "1wk"),
    ("6mo",    "6mo"),    # pass-through
    ("  1YR ", "1y"),     # whitespace + case-insensitive
])
def test_normalize_period(raw, expected):
    assert normalize_period(raw) == expected


# ── calculate_strategy_metrics — empty legs ───────────────────────────────────

def test_empty_legs_returns_zeroes():
    result = calculate_strategy_metrics([], spot_price=100)
    assert result == {"max_profit": 0, "max_loss": 0, "breakeven": 0, "net_cost": 0}


# ── single leg (long call) ────────────────────────────────────────────────────

def test_long_call_max_loss_equals_premium():
    legs = [{"action": "BUY", "type": "CALL", "strike": 100, "price": 5.0, "expiry": "2025-12-19"}]
    result = calculate_strategy_metrics(legs, spot_price=100)
    assert result["max_loss"] == 5.0 * 100
    assert result["max_profit"] == "Unlimited"


def test_short_call_max_profit_equals_premium():
    legs = [{"action": "SELL", "type": "CALL", "strike": 100, "price": 4.0, "expiry": "2025-12-19"}]
    result = calculate_strategy_metrics(legs, spot_price=100)
    assert result["max_profit"] == 4.0 * 100
    assert result["max_loss"] == "Unlimited"


# ── vertical spread (debit) ───────────────────────────────────────────────────

def test_bull_call_spread_metrics():
    legs = [
        {"action": "BUY",  "type": "CALL", "strike": 100, "price": 5.0, "expiry": "2025-12-19"},
        {"action": "SELL", "type": "CALL", "strike": 110, "price": 2.0, "expiry": "2025-12-19"},
    ]
    result = calculate_strategy_metrics(legs, spot_price=100)
    net_premium = 3.0          # debit
    spread_width = 10 * 100    # = 1000
    assert result["is_debit"] is True
    assert result["max_loss"]   == pytest.approx(net_premium * 100)
    assert result["max_profit"] == pytest.approx(spread_width - net_premium * 100)


# ── vertical spread (credit) ──────────────────────────────────────────────────

def test_bull_put_spread_credit_metrics():
    legs = [
        {"action": "SELL", "type": "PUT", "strike": 100, "price": 5.0, "expiry": "2025-12-19"},
        {"action": "BUY",  "type": "PUT", "strike": 90,  "price": 2.0, "expiry": "2025-12-19"},
    ]
    result = calculate_strategy_metrics(legs, spot_price=100)
    net_premium = 3.0          # credit
    spread_width = 10 * 100
    assert result["is_debit"] is False
    assert result["max_profit"] == pytest.approx(net_premium * 100)
    assert result["max_loss"]   == pytest.approx(spread_width - net_premium * 100)


# ── iron condor (4-leg) ───────────────────────────────────────────────────────

def test_iron_condor_max_profit_equals_credit():
    legs = [
        {"action": "BUY",  "type": "PUT",  "strike":  80, "price": 1.0, "expiry": "2025-12-19"},
        {"action": "SELL", "type": "PUT",  "strike":  90, "price": 3.0, "expiry": "2025-12-19"},
        {"action": "SELL", "type": "CALL", "strike": 110, "price": 3.0, "expiry": "2025-12-19"},
        {"action": "BUY",  "type": "CALL", "strike": 120, "price": 1.0, "expiry": "2025-12-19"},
    ]
    result = calculate_strategy_metrics(legs, spot_price=100)
    assert result["is_debit"] is False
    assert result["max_profit"] == pytest.approx(4.0 * 100)


# ── leg_details list ──────────────────────────────────────────────────────────

def test_leg_details_populated():
    legs = [{"action": "BUY", "type": "CALL", "strike": 100, "price": 5.0, "expiry": "2025-12-19"}]
    result = calculate_strategy_metrics(legs, spot_price=100)
    assert len(result["leg_details"]) == 1
    assert "BUY" in result["leg_details"][0]
    assert "CALL" in result["leg_details"][0]
