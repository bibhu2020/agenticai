# tests/test_data_agent.py
import pytest
import pandas as pd
from agents.data_agent import DataAgent

@pytest.fixture
def agent():
    """Return a reusable DataAgent instance"""
    return DataAgent()

def test_fetch_ohlcv(agent):
    """Test that OHLCV data is returned as a non-empty DataFrame"""
    df = agent.ohlcv("AAPL", period="1mo", interval="1d")
    assert isinstance(df, pd.DataFrame), "OHLCV should be a DataFrame"
    assert not df.empty, "OHLCV DataFrame should not be empty"
    assert all(col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"]), "Columns missing"

def test_company_info(agent):
    """Test that company info returns expected keys"""
    info = agent.company("AAPL")
    assert isinstance(info, dict), "Company info should be a dict"
    expected_keys = ["ticker", "longName", "sector", "industry", "website", "marketCap", "summary"]
    for key in expected_keys:
        assert key in info, f"{key} missing in company info"

def test_latest_price(agent):
    """Test that latest price returns a float or None"""
    price = agent.latest_price("AAPL")
    print(f"Latest price for AAPL: {price}")
    assert price is None or isinstance(price, float), "Latest price should be a float or None"

def test_financials(agent):
    """Test that financials returns a dict with DataFrames"""
    financials = agent.financials("AAPL")
    assert isinstance(financials, dict), "Financials should be a dict"
    for key in ["financials", "balance_sheet", "cashflow"]:
        assert key in financials, f"{key} missing in financials dict"
        assert isinstance(financials[key], pd.DataFrame), f"{key} should be a DataFrame"
