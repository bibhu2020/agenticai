# tests/test_orchestrator.py
import pandas as pd
import pytest
from unittest.mock import patch

from core.orchestrator import Orchestrator

@patch("core.orchestrator.PortfolioAgent")
@patch("core.orchestrator.StrategyAgent")
@patch("core.orchestrator.SentimentAgent")
@patch("core.orchestrator.FundamentalAgent")
@patch("core.orchestrator.TechnicalAgent")
@patch("core.orchestrator.DataAgent")
def test_analyze_stock(MockData, MockTechnical, MockFundamental, MockSentiment, MockStrategy, MockPortfolio):
    # Mock OHLCV DataFrame
    ohlcv_df = pd.DataFrame({
        "Open": [150, 151],
        "High": [152, 153],
        "Low": [149, 150],
        "Close": [151, 152],
        "Volume": [1000, 1100]
    })

    # Setup DataAgent mocks
    mock_data = MockData.return_value
    mock_data.latest_price.return_value = 150.0
    mock_data.financials.return_value = {"financials": {}, "balance_sheet": {}, "cashflow": {}, "earnings": {}}
    mock_data.ohlcv.return_value = ohlcv_df

    # TechnicalAgent mock
    mock_tech = MockTechnical.return_value
    mock_tech.analyze.return_value = "Buy"

    # FundamentalAgent mock
    mock_fund = MockFundamental.return_value
    mock_fund.analyze.return_value = "Strong"

    # SentimentAgent mocks
    mock_sent = MockSentiment.return_value
    mock_sent.fetch_news.return_value = ["Good news headline"]
    mock_sent.analyze_sentiment.return_value = "Positive"

    # StrategyAgent mock
    mock_strategy = MockStrategy.return_value
    mock_strategy.generate_strategy.return_value = "Buy"

    # PortfolioAgent mock
    mock_portfolio = MockPortfolio.return_value
    mock_portfolio.get_portfolio_value.return_value = 2000.0

    # Create orchestrator AFTER patching
    orchestrator = Orchestrator()

    # Run orchestrator
    result = orchestrator.analyze_stock("AAPL")

    # Assertions
    assert result["symbol"] == "AAPL"
    assert result["latest_price"] == 150.0
    assert result["technical"] == "Buy"
    assert result["fundamental"] == "Strong"
    assert result["sentiment"] == "Positive"
    assert result["strategy"] == "Buy"
    assert result["portfolio_value"] == 2000.0
    assert result["news_headlines"] == ["Good news headline"]
