
"""
Integration Tests for Trading Research MCP
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import importlib.util

# Clean up any existing mocks
for m in ["mcp", "mcp.server", "mcp.server.fastmcp"]:
    if m in sys.modules:
        del sys.modules[m]

# Create a pass-through MockFastMCP
class MockFastMCP:
    def __init__(self, name):
        self.name = name
    
    def tool(self):
        def decorator(func):
            return func
        return decorator
    
    def run(self):
        pass

# Mock the module structure
mock_mcp = MagicMock()
mock_server = MagicMock()
mock_fastmcp = MagicMock()
mock_fastmcp.FastMCP = MockFastMCP

sys.modules["mcp"] = mock_mcp
sys.modules["mcp.server"] = mock_server
sys.modules["mcp.server.fastmcp"] = mock_fastmcp

# Create mock yfinance *before* importing server
with patch.dict(sys.modules, {"yfinance": MagicMock()}):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-trading-research/server.py"))
    spec = importlib.util.spec_from_file_location("mcp_trading_research_server", file_path)
    server = importlib.util.module_from_spec(spec)
    sys.modules["mcp_trading_research_server"] = server
    spec.loader.exec_module(server)

def test_get_news_sentiment():
    mock_ticker = MagicMock()
    mock_ticker.news = [
        {"title": "Stock Soars After Great Earnings", "publisher": "CNBC", "link": "http://...", "providerPublishTime": 123},
        {"title": "Analyst Downgrades Stock Due to Risks", "publisher": "Bloomberg", "link": "http://...", "providerPublishTime": 124}
    ]
    
    # Patch yf on the loaded module
    with patch.object(server.yf, "Ticker", return_value=mock_ticker):
        res = server.get_news_sentiment("AAPL")
        
        assert len(res) == 2
        # 'Stock Soars' -> Positive
        assert res[0]["sentiment_label"] == "POSITIVE"
        # 'Downgrades Risks' -> Negative
        assert res[1]["sentiment_label"] == "NEGATIVE"

def test_get_insider_trades():
    mock_ticker = MagicMock()
    mock_df = MagicMock()
    mock_df.empty = False
    
    # Mock head().reset_index().astype().to_dict() chain
    mock_recent = MagicMock()
    mock_recent.to_dict.return_value = [{"Insider": "Cook Tim", "Type": "Sell"}]
    
    mock_df.head.return_value.reset_index.return_value.astype.return_value = mock_recent
    mock_ticker.insider_transactions = mock_df
    
    with patch.object(server.yf, "Ticker", return_value=mock_ticker):
        res = server.get_insider_trades("AAPL")
        assert len(res) == 1
        assert res[0]["Insider"] == "Cook Tim"

def test_get_analyst_ratings():
    mock_ticker = MagicMock()
    mock_df = MagicMock()
    mock_df.empty = False
    
    # Mock head().reset_index().astype().to_dict() chain
    mock_recent = MagicMock()
    mock_recent.to_dict.return_value = [{"Firm": "Goldman", "Action": "Buy"}]
    
    mock_df.tail.return_value.reset_index.return_value.astype.return_value = mock_recent
    mock_ticker.recommendations = mock_df
    
    with patch.object(server.yf, "Ticker", return_value=mock_ticker):
        res = server.get_analyst_ratings("AAPL")
        assert len(res) == 1
        assert res[0]["Firm"] == "Goldman"
