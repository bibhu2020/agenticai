
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class OHLC(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockData(BaseModel):
    symbol: str
    interval: str
    data: List[OHLC]

class IndicatorRequest(BaseModel):
    symbol: str
    interval: str = "1d"
    period: int = 14

class IndicatorResponse(BaseModel):
    symbol: str
    indicator: str
    value: float
    signal: str  # BUY, SELL, NEUTRAL

class StrategyResult(BaseModel):
    strategy: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    reasoning: str
