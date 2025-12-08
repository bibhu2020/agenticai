# tests/test_utils.py
import pytest
import datetime
from utils import helpers, visualization
import matplotlib.pyplot as plt

# -----------------------
# Tests for helpers.py
# -----------------------

def test_get_today_date():
    today = helpers.get_today_date()
    assert isinstance(today, str)
    assert len(today) == 10  # YYYY-MM-DD

def test_format_and_parse_date():
    date = datetime.datetime(2025, 10, 21)
    formatted = helpers.format_date(date)
    assert formatted == "2025-10-21"

    parsed = helpers.parse_date(formatted)
    assert parsed == date

def test_daterange():
    start = "2025-10-20"
    end = "2025-10-22"
    dates = helpers.daterange(start, end)
    assert dates == ["2025-10-20", "2025-10-21", "2025-10-22"]

def test_safe_get():
    d = {"a": 1}
    assert helpers.safe_get(d, "a") == 1
    assert helpers.safe_get(d, "b", default=2) == 2
    assert helpers.safe_get(d, "b") is None

def test_normalize_text():
    assert helpers.normalize_text("  Hello World ") == "hello world"

def test_clamp():
    assert helpers.clamp(5, 0, 10) == 5
    assert helpers.clamp(-1, 0, 10) == 0
    assert helpers.clamp(20, 0, 10) == 10

# -----------------------
# Tests for visualization.py
# -----------------------
# We'll just test that functions run and return matplotlib Figure objects

def test_plot_ohlcv_runs():
    sample_data = {
        "Date": ["2025-10-20", "2025-10-21", "2025-10-22"],
        "Open": [100, 102, 101],
        "High": [105, 103, 104],
        "Low": [99, 100, 100],
        "Close": [104, 101, 102],
        "Volume": [1000, 1100, 1050]
    }
    fig = visualization.plot_ohlcv(sample_data, symbol="TEST")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_signals_runs():
    sample_data = {
        "Date": ["2025-10-20", "2025-10-21", "2025-10-22"],
        "Close": [104, 101, 102]
    }
    buy_signals = [1]  # index 1
    sell_signals = [2]  # index 2
    fig = visualization.plot_signals(sample_data, buy_signals, sell_signals, symbol="TEST")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
