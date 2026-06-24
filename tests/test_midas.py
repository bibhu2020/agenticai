"""Tests for Midas (stock-investment-analyst) — output types and agent structure."""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_midas_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../src/midas")
)
if _midas_path not in sys.path:
    sys.path.insert(0, _midas_path)

# Stub heavy deps before importing project modules
sys.modules.setdefault("yfinance", MagicMock())
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("autogen_agentchat", MagicMock())
sys.modules.setdefault("autogen_agentchat.agents", MagicMock())
sys.modules.setdefault("autogen_agentchat.conditions", MagicMock())
sys.modules.setdefault("autogen_agentchat.teams", MagicMock())
sys.modules.setdefault("autogen_agentchat.ui", MagicMock())
sys.modules.setdefault("autogen_agentchat.messages", MagicMock())
sys.modules.setdefault("autogen_core", MagicMock())
sys.modules.setdefault("autogen_core.tools", MagicMock())
sys.modules.setdefault("autogen_ext", MagicMock())
sys.modules.setdefault("autogen_ext.models", MagicMock())
sys.modules.setdefault("autogen_ext.models.openai", MagicMock())
_mock_client = MagicMock()
_mock_utility = MagicMock()
_mock_utility.AutoGenModelFactory = MagicMock(return_value=_mock_client)
sys.modules["utility"] = _mock_utility
sys.modules["utility.autogen_model_factory"] = _mock_utility

# Stub core.model used by agent files
_core_model = MagicMock()
_core_model.get_model_client = MagicMock(return_value=_mock_client)
sys.modules["core"] = MagicMock()
sys.modules["core.model"] = _core_model

# Stub tools used by agent files
sys.modules["tools"] = MagicMock()
sys.modules["tools.yf_tools"] = MagicMock()
sys.modules["tools.search_tools"] = MagicMock()

# Clear any cached 'aagents' that may have been loaded by a previous test module
# (e.g. test_agora.py loads market-analyst's aagents) and re-ensure midas is first
for _k in [k for k in list(sys.modules) if k == "aagents" or k.startswith("aagents.")]:
    del sys.modules[_k]
if _midas_path in sys.path:
    sys.path.remove(_midas_path)
sys.path.insert(0, _midas_path)

from aagents import StockTrend


# ── StockTrend Pydantic model ─────────────────────────────────────────────────

def test_stock_trend_fields():
    st = StockTrend(
        stock_name="AAPL",
        trade_date="2025-06-01",
        open_price=170.0,
        close_price=175.5,
        high_price=176.0,
        low_price=169.5,
        volume=5_000_000,
    )
    assert st.stock_name == "AAPL"
    assert st.close_price == 175.5
    assert st.volume == 5_000_000


def test_stock_trend_serialisable():
    st = StockTrend(
        stock_name="TSLA",
        trade_date="2025-06-01",
        open_price=200.0,
        close_price=210.0,
        high_price=215.0,
        low_price=198.0,
        volume=10_000_000,
    )
    d = st.model_dump()
    assert set(d.keys()) == {
        "stock_name", "trade_date", "open_price",
        "close_price", "high_price", "low_price", "volume",
    }


def test_stock_trend_requires_all_fields():
    with pytest.raises(Exception):
        StockTrend(stock_name="AAPL")  # missing numeric fields


# ── Agent factories return agent objects ──────────────────────────────────────

def test_get_stock_trends_agent_returns_object():
    from aagents.stock_trends_agent import get_stock_trends_agent
    agent = get_stock_trends_agent()
    assert agent is not None


def test_get_news_agent_returns_object():
    from aagents.news_agent import get_news_agent
    agent = get_news_agent()
    assert agent is not None


def test_get_sentiment_agent_returns_object():
    from aagents.sentiment_agent import get_sentiment_agent
    agent = get_sentiment_agent()
    assert agent is not None


def test_get_decision_agent_returns_object():
    from aagents.decision_agent import get_decision_agent
    agent = get_decision_agent()
    assert agent is not None
