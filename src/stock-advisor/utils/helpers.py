# utils/helpers.py
import datetime
from typing import List, Optional, Dict
import logging

# -----------------------
# Logging Setup
# -----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------
# Date / Time Utilities
# -----------------------
def get_today_date() -> str:
    """Return today's date in YYYY-MM-DD format."""
    return datetime.datetime.today().strftime("%Y-%m-%d")

def format_date(dt: datetime.datetime) -> str:
    """Format a datetime object to YYYY-MM-DD string."""
    return dt.strftime("%Y-%m-%d")

def parse_date(date_str: str) -> datetime.datetime:
    """Parse a YYYY-MM-DD string into a datetime object."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")

def daterange(start_date: str, end_date: str) -> list[str]:
    """Return list of date strings from start to end inclusive."""
    start = parse_date(start_date)
    end = parse_date(end_date)
    return [(start + datetime.timedelta(days=i)).strftime("%Y-%m-%d") 
            for i in range((end - start).days + 1)]


# -----------------------
# Data Utilities
# -----------------------
def safe_get(d: Dict, key: str, default=None):
    """Safely get a value from a dictionary."""
    return d.get(key, default)

def normalize_text(text: str) -> str:
    """Lowercase and strip whitespace from text."""
    return text.strip().lower()

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value between min_value and max_value."""
    return max(min_value, min(value, max_value))

# -----------------------
# Logging Utilities
# -----------------------
def log_info(message: str):
    logger.info(message)

def log_warning(message: str):
    logger.warning(message)

def log_error(message: str):
    logger.error(message)
