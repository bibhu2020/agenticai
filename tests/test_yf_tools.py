import sys
import json
import os
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
from common.mcp.tools import yf_tools, news_tools

# def test_get_summary_success():
#     result = yf_tools._get_summary("AAPL")
    
#     print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
    
#     assert "Apple Inc. (AAPL)" in result


# def test_get_summary_no_data():
#     result = yf_tools._get_summary("INVALID")
#     assert "No data found for symbol 'INVALID'" in result

# def test_get_market_sentiment_bullish():
#     result = yf_tools._get_market_sentiment("AAPL")
#     print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
#     assert any(word in result for word in ("Bullish", "Bearish"))

def test_get_history_success():
    
    result = yf_tools._get_history("AAPL")
    print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
    assert "Historical data for AAPL" in result
    # assert "105.0" in result # Should show last rows

# def test_get_analyst_recommendations_success():
#     result = yf_tools._get_analyst_recommendations("AAPL")
#     print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
#     assert "Analyst Recommendations for AAPL" in result

# def test_get_earnings_calendar_success_dict():
#     result = yf_tools._get_earnings_calendar("AAPL")
#     print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
#     assert "Earnings Calendar for AAPL" in result


# def test_search_news_success():
#     result = news_tools._search_news("News on APPL Stock", num_results=5, days_back=5)
#     print(f"\nDEBUG OUTPUT: {result}") # Added print for verification
#     assert "News Search Results for 'News on APPL Stock'" in result