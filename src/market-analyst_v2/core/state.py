from typing import TypedDict, List, Annotated, Optional
import operator
from pydantic import BaseModel, Field

class MarketData(TypedDict):
    ticker: str
    price: float
    technicals: str

class SentimentData(TypedDict):
    sentiment: str
    score: float
    summary: str

class StrategyData(TypedDict):
    action: str
    confidence: float
    entry: float
    exit: float
    stop_loss: float
    reasoning: str

class AgentState(TypedDict):
    ticker: str
    messages: Annotated[List[str], operator.add]
    market_data: Optional[MarketData]
    sentiment_data: Optional[SentimentData]
    strategy_data: Optional[StrategyData]
    final_report: str
