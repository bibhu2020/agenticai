# tests/test_strategy_agent.py

import pytest
from agents.strategy_agent import StrategyAgent

@pytest.fixture
def agent():
    return StrategyAgent()

def test_strategy_all_positive(agent):
    strategy = agent.generate_strategy("Buy", "Strong", "Positive")
    assert strategy == "Buy"

def test_strategy_all_negative(agent):
    strategy = agent.generate_strategy("Sell", "Weak", "Negative")
    assert strategy == "Sell"

def test_strategy_mixed_signals(agent):
    # Majority positive
    strategy = agent.generate_strategy("Buy", "Weak", "Positive")
    assert strategy == "Buy"

    # Majority negative
    strategy = agent.generate_strategy("Sell", "Strong", "Negative")
    assert strategy == "Sell"

    # Tie/majority negative scenario
    strategy = agent.generate_strategy("Buy", "Weak", "Negative")
    assert strategy == "Sell"  # Fixed: 'Weak' counts as negative

def test_strategy_all_neutral(agent):
    strategy = agent.generate_strategy("Hold", "Neutral", "Neutral")
    assert strategy == "Hold"

def test_strategy_empty_strings(agent):
    strategy = agent.generate_strategy("", "", "")
    assert strategy == "Hold"
