# tests/test_portfolio_agent.py

import pytest
from agents.portfolio_agent import PortfolioAgent

@pytest.fixture
def portfolio():
    return PortfolioAgent()

def test_add_position_new(portfolio):
    portfolio.add_position("AAPL", 10, 150.0)
    positions = portfolio.get_positions()
    assert "AAPL" in positions
    assert positions["AAPL"]["shares"] == 10
    assert positions["AAPL"]["price"] == 150.0

def test_add_position_existing(portfolio):
    portfolio.add_position("AAPL", 5, 150.0)
    portfolio.add_position("AAPL", 10, 155.0)  # Update existing
    positions = portfolio.get_positions()
    assert positions["AAPL"]["shares"] == 15
    assert positions["AAPL"]["price"] == 155.0

def test_remove_position(portfolio):
    portfolio.add_position("TSLA", 8, 900.0)
    portfolio.remove_position("TSLA", 3)
    positions = portfolio.get_positions()
    assert positions["TSLA"]["shares"] == 5

    # Remove remaining shares
    portfolio.remove_position("TSLA", 5)
    positions = portfolio.get_positions()
    assert "TSLA" not in positions

def test_update_price(portfolio):
    portfolio.add_position("GOOGL", 7, 1200.0)
    portfolio.update_price("GOOGL", 1250.0)
    positions = portfolio.get_positions()
    assert positions["GOOGL"]["price"] == 1250.0

def test_get_portfolio_value(portfolio):
    portfolio.add_position("AAPL", 10, 150.0)
    portfolio.add_position("TSLA", 5, 900.0)
    total_value = portfolio.get_portfolio_value()
    expected_value = 10 * 150.0 + 5 * 900.0
    assert total_value == expected_value

def test_remove_nonexistent_position_logs_warning(caplog, portfolio):
    with caplog.at_level("WARNING"):
        portfolio.remove_position("MSFT", 5)
        assert "not in portfolio" in caplog.text
