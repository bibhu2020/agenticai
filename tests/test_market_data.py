
import pytest
from unittest.mock import patch, MagicMock
from data.market_data import get_market_data, get_current_price
from data.fundamentals import get_fundamental_data

def test_get_market_data(mock_market_data):
    # Mock yfnance.Ticker
    with patch("data.market_data.yf.Ticker") as mock_ticker_cls:
        mock_instance = mock_ticker_cls.return_value
        # ticker.history() returns a DataFrame.
        # We can construct a DataFrame from mock_market_data.
        import pandas as pd
        df = pd.DataFrame(mock_market_data)
        # Rename columns to match yfinance (Open, High, Low, Close, Volume)
        df_yf = df.rename(columns={
            "open": "Open", 
            "high": "High", 
            "low": "Low", 
            "close": "Close", 
            "volume": "Volume"
        })
        # yfinance index is Datetime usually.
        df_yf.index = pd.to_datetime(df["date"])
        
        mock_instance.history.return_value = df_yf
        
        res = get_market_data("AAPL")
        assert len(res) == len(mock_market_data)
        assert res[0]["close"] == mock_market_data[0]["close"]

def test_get_current_price():
    with patch("data.market_data.yf.Ticker") as mock_ticker_cls:
        mock_instance = mock_ticker_cls.return_value
        import pandas as pd
        df = pd.DataFrame({"Close": [150.0]})
        mock_instance.history.return_value = df
        
        price = get_current_price("AAPL")
        assert price == 150.0

def test_get_fundamental_data():
    with patch("data.fundamentals.yf.Ticker") as mock_ticker_cls:
        mock_instance = mock_ticker_cls.return_value
        mock_instance.info = {
            "marketCap": 2000000000,
            "trailingPE": 25.0,
            "dividendYield": 0.01
        }
        
        data = get_fundamental_data("AAPL")
        assert data["market_cap"] == 2000000000
        assert data["pe_ratio"] == 25.0
