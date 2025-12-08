# tests/test_fundamental_agent.py

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from agents.fundamental_agent import FundamentalAgent

@pytest.fixture
def agent():
    return FundamentalAgent()

def fake_ticker(symbol):
    # Create a fake ticker object with mocked financial data
    mock = MagicMock()
    mock.financials = pd.DataFrame({
        "Total Revenue": [100000],
        "Net Income": [15000]
    }, index=["Net Income", "Total Revenue"]).T
    mock.balance_sheet = pd.DataFrame({
        "Total Stockholder Equity": [50000],
        "Total Liab": [20000]
    }, index=["Total Liab", "Total Stockholder Equity"]).T
    mock.cashflow = pd.DataFrame({
        "Operating Cash Flow": [12000]
    })
    mock.income_stmt = pd.DataFrame({
        "Net Income": [15000]
    })
    return mock

@patch("yfinance.Ticker", side_effect=fake_ticker)
def test_fetch_financials(mock_ticker, agent):
    financials = agent.fetch_financials("AAPL")
    assert isinstance(financials, dict)
    assert "financials" in financials
    assert "balance_sheet" in financials
    assert "cashflow" in financials
    assert "earnings" in financials

@patch("yfinance.Ticker", side_effect=fake_ticker)
def test_calculate_ratios(mock_ticker, agent):
    financials = agent.fetch_financials("AAPL")
    ratios = agent.calculate_ratios(financials)
    assert isinstance(ratios, dict)
    assert "roe" in ratios
    assert "debt_to_equity" in ratios
    assert ratios["roe"] > 0
    assert ratios["debt_to_equity"] > 0

@patch("yfinance.Ticker", side_effect=fake_ticker)
def test_analyze_signal(mock_ticker, agent):
    result = agent.analyze("AAPL")
    assert isinstance(result, dict)
    assert "signal" in result
    assert result["signal"] in ["Strong", "Neutral", "Weak", "Data Unavailable"]
    assert "ratios" in result
    assert "financials" in result

def test_analyze_empty_data(agent):
    # Patch fetch_financials to return empty dict
    agent.fetch_financials = lambda symbol: {}
    result = agent.analyze("FAKE")
    assert result["signal"] == "Data Unavailable"
    assert result["ratios"] == {}
    assert result["financials"] == {}
