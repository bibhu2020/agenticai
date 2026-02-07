
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add mcp-trader to path to allow importing modules despite hyphen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/mcp-trader")))

from unittest.mock import MagicMock

@pytest.fixture
def bullish_data():
    """Returns a DataFrame with a clear uptrend."""
    dates = pd.date_range(start="2023-01-01", periods=100)
    prices = np.linspace(100, 200, 100) # Linearly increasing
    data = {
        "date": dates,
        "open": prices,
        "high": prices + 1,
        "low": prices - 1,
        "close": prices,
        "volume": np.random.randint(1000, 5000, 100)
    }
    return pd.DataFrame(data).set_index("date")

@pytest.fixture
def bearish_data():
    """Returns a DataFrame with a clear downtrend."""
    dates = pd.date_range(start="2023-01-01", periods=100)
    prices = np.linspace(200, 100, 100) # Linearly decreasing
    data = {
        "date": dates,
        "open": prices,
        "high": prices + 1,
        "low": prices - 1,
        "close": prices,
        "volume": np.random.randint(1000, 5000, 100)
    }
    return pd.DataFrame(data).set_index("date")

@pytest.fixture
def flat_data():
    """Returns a DataFrame with flat price action."""
    dates = pd.date_range(start="2023-01-01", periods=100)
    prices = np.full(100, 150) # constant
    data = {
        "date": dates,
        "open": prices,
        "high": prices + 1,
        "low": prices - 1,
        "close": prices,
        "volume": np.random.randint(1000, 5000, 100)
    }
    return pd.DataFrame(data).set_index("date")

@pytest.fixture
def mock_market_data(bullish_data):
    """
    Returns a list of dicts suitable for get_market_data return value based on bullish data.
    """
    data_list = []
    for index, row in bullish_data.iterrows():
        data_list.append({
            "date": index.strftime("%Y-%m-%d"),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"])
        })
    return data_list
