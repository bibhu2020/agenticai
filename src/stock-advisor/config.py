# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # optional, if using a news API

# Default stock settings
DEFAULT_STOCK_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Data settings
HISTORICAL_DATA_DAYS = 365  # Fetch 1 year of historical OHLCV data

# Technical analysis parameters
SMA_PERIOD = 20
EMA_PERIOD = 20
RSI_PERIOD = 14

# Gradio UI settings
GRADIO_SERVER_NAME = "0.0.0.0"
GRADIO_SERVER_PORT = 7860
