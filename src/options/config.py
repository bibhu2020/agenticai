"""
Central configuration for the Options Paper Trading App.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Portfolio ─────────────────────────────────────────────────────────────────
STARTING_CAPITAL = 5000.0          # Initial paper trading capital
MAX_POSITION_SIZE_PCT = 0.20       # Max 20% of portfolio per position
MAX_OPEN_POSITIONS = 5             # Max concurrent sell-put positions

# ── Option selection ──────────────────────────────────────────────────────────
MIN_DTE = 14                       # Minimum days to expiration
MAX_DTE = 28                       # Maximum days to expiration
TARGET_DELTA = 0.30                # Target delta for short puts (0.20–0.35)
MIN_DELTA = 0.15
MAX_DELTA = 0.40
OTM_BUFFER_PCT = 0.05              # Strike at least 5% below current price

# ── Exit rules ────────────────────────────────────────────────────────────────
PROFIT_TARGET_PCT = 0.30           # Close at 30% profit of premium collected
STOP_LOSS_PCT = 0.30               # Close at 30% loss of premium collected

# ── Scoring weights (sum to 1.0) ──────────────────────────────────────────────
WEIGHT_TECHNICAL   = 0.35
WEIGHT_FUNDAMENTAL = 0.30
WEIGHT_SENTIMENT   = 0.35

MIN_SCORE_TO_TRADE = 0.55          # Minimum composite score (0–1) to place trade

# ── Self-tuning ───────────────────────────────────────────────────────────────
TUNE_INTERVAL_DAYS = 30            # Re-evaluate algo every 30 days
MIN_WIN_RATE_BEFORE_TUNE = 0.50    # Tune if win rate drops below 50%
MIN_PNL_BEFORE_TUNE = 0.0         # Tune if cumulative P&L is negative

# ── Stock universe ────────────────────────────────────────────────────────────
# S&P 500 subset to scan — well-known, liquid options
DEFAULT_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "HD", "CVX", "ABBV", "MRK",
    "PEP", "KO", "AVGO", "LLY", "TMO", "COST", "DHR", "ACN", "VZ",
    "CMCSA", "ADBE", "NEE", "NKE", "TXN", "PM", "HON", "UNH", "IBM",
    "AMD", "INTC", "BA", "CAT", "GS", "MS", "BAC", "WFC", "C",
    "NFLX", "DIS", "PYPL", "CRM", "ORCL", "QCOM",
]

# ── Scheduler ─────────────────────────────────────────────────────────────────
# All times in US/Eastern
SCAN_HOUR   = 10          # Run daily stock scan at 10:00 AM ET
SCAN_MINUTE = 0
CHECK_INTERVAL_MINUTES = 30   # Check open positions every 30 min
EOD_HOUR    = 16          # End-of-day snapshot at 4:00 PM ET
EOD_MINUTE  = 15

# ── App ───────────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = "options-paper-trading-secret"
DEBUG = False
PORT  = 5050

# ── Sentiment sources ─────────────────────────────────────────────────────────
REDDIT_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "options"]
NEWS_SOURCES = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
    "https://finviz.com/quote.ashx?t={ticker}",
]
