
import pytest
from unittest.mock import patch, MagicMock
try:
    from server import get_stock_price, get_technical_summary, get_momentum_strategy
    from server import get_golden_cross_strategy, get_macd_crossover_strategy, get_bollinger_squeeze_strategy
except ImportError:
    # If standard import fails, try relative or assume sys.path
    import sys
    import os
    # Add src/mcp-trader again just in case (conftest handles it though)
    pass
    from server import get_stock_price, get_technical_summary, get_momentum_strategy
    from server import get_golden_cross_strategy, get_macd_crossover_strategy, get_bollinger_squeeze_strategy

def test_get_stock_price_tool():
    with patch("server.get_current_price", return_value=123.45):
        price = get_stock_price("AAPL")
        assert price == 123.45

def test_get_technical_summary_tool(mock_market_data):
    # Mock get_market_data in server module namespace if imported there directly
    # In server.py: from .data.market_data import get_market_data
    # So we patch server.get_market_data
    with patch("server.get_market_data", return_value=mock_market_data):
        summary = get_technical_summary("GOOGL")
        assert summary["symbol"] == "GOOGL"
        assert "rsi_14" in summary
        assert "sma_50" in summary
        # Check values roughly
        assert summary["price"] == mock_market_data[-1]["close"]

def test_get_momentum_strategy_tool(mock_market_data):
    # Mock analyze_momentum in server namespace
    # server.py imports analyze_momentum.
    # We can mock that import.
    mock_res = {"action": "BUY", "confidence": 0.8}
    with patch("server.analyze_momentum", return_value=mock_res):
        res = get_momentum_strategy("TSLA")
        assert res["action"] == "BUY"

def test_get_golden_cross_tool():
    mock_res = {"strategy": "Golden Cross", "action": "HOLD"}
    with patch("server.analyze_golden_cross", return_value=mock_res):
        res = get_golden_cross_strategy("SPY")
        assert res["strategy"] == "Golden Cross"

def test_get_macd_crossover_tool():
    mock_res = {"strategy": "MACD Crossover", "action": "BUY"}
    with patch("server.analyze_macd_crossover", return_value=mock_res):
        res = get_macd_crossover_strategy("QQQ")
        assert res["action"] == "BUY"

def test_get_bollinger_squeeze_tool():
    mock_res = {"strategy": "Bollinger Squeeze", "action": "SELL"}
    with patch("server.analyze_bollinger_squeeze", return_value=mock_res):
        res = get_bollinger_squeeze_strategy("IWM")
        assert res["action"] == "SELL"
