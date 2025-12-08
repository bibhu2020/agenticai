# tests/test_data_fetcher.py

import sys
import utils.data_fetcher as data_fetcher
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path so `utils` can be imported
# sys.path.append(str(Path(__file__).resolve().parent.parent))

# from utils.data_fetcher import fetch_ohlcv, fetch_company_info, fetch_financials

@pytest.mark.parametrize("symbol", ["AAPL", "MSFT"])
def test_fetch_ohlcv(symbol):
    df = data_fetcher.fetch_ohlcv(symbol)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"])

@pytest.mark.parametrize("symbol", ["AAPL", "MSFT"])
def test_fetch_company_info(symbol):
    info = data_fetcher.fetch_company_info(symbol)
    assert isinstance(info, dict)
    # Updated keys according to current yfinance
    assert "name" in info or "longName" in info or "shortName" in info

@pytest.mark.parametrize("symbol", ["AAPL", "MSFT"])
def test_fetch_financials(symbol):
    fin = data_fetcher.fetch_financials(symbol)
    assert isinstance(fin, dict)
    assert all(key in fin for key in ["financials", "balance_sheet", "cashflow", "earnings"])
