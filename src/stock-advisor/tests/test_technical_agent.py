# tests/test_technical_agent.py

import pytest
import pandas as pd
import numpy as np
from agents.technical_agent import TechnicalAgent

@pytest.fixture
def sample_data():
    # Create dummy OHLCV data
    np.random.seed(42)
    data = pd.DataFrame({
        "Open": np.random.rand(50) * 100,
        "High": np.random.rand(50) * 100,
        "Low": np.random.rand(50) * 100,
        "Close": np.random.rand(50) * 100,
        "Volume": np.random.randint(1000, 10000, size=50)
    })
    return data

@pytest.fixture
def agent():
    return TechnicalAgent()

def test_calculate_sma(agent, sample_data):
    sma = agent.calculate_sma(sample_data, period=20)
    assert isinstance(sma, pd.Series), "SMA should return a pandas Series"
    assert len(sma) == len(sample_data), "SMA Series should match input length"

def test_calculate_ema(agent, sample_data):
    ema = agent.calculate_ema(sample_data, period=20)
    assert isinstance(ema, pd.Series), "EMA should return a pandas Series"
    assert len(ema) == len(sample_data), "EMA Series should match input length"

def test_calculate_rsi(agent, sample_data):
    rsi = agent.calculate_rsi(sample_data, period=14)
    assert isinstance(rsi, pd.Series), "RSI should return a pandas Series"
    assert len(rsi) == len(sample_data), "RSI Series should match input length"
    # Check RSI values are between 0 and 100
    assert rsi.dropna().between(0, 100).all(), "RSI values should be between 0 and 100"

def test_analyze(agent, sample_data):
    analysis = agent.analyze(sample_data)
    assert isinstance(analysis, dict), "Analyze should return a dictionary"
    for key in ["SMA_20", "EMA_20", "RSI_14", "signal"]:
        assert key in analysis, f"{key} missing in analysis result"
    # Check signal is one of Buy/Hold/Sell
    assert analysis["signal"] in ["Buy", "Hold", "Sell"], "Signal should be Buy, Hold, or Sell"

def test_empty_data(agent):
    empty_df = pd.DataFrame()
    analysis = agent.analyze(empty_df)
    assert analysis == {}, "Analysis of empty data should return empty dictionary"
