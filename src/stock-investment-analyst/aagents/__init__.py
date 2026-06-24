from .stock_trends_agent import get_stock_trends_agent
from .news_agent import get_news_agent
from .sentiment_agent import get_sentiment_agent
from .decision_agent import get_decision_agent
from pydantic import BaseModel

class StockTrend(BaseModel):
    stock_name: str
    trade_date: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

__all__ = ["get_stock_trends_agent", "get_news_agent", "get_sentiment_agent", "get_decision_agent", "StockTrend"]
