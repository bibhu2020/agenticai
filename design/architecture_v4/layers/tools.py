import os
from typing import TypedDict, Annotated, Literal

# Define Tools
# AutoGen tools are just Python functions that are registered with agents.

def mock_search_web(query: Annotated[str, "The query to search for weather or news"]) -> str:
    """
    Simulates a web search engine. Use this when you need to find current information,
    news, or weather.
    """
    print(f"\n[WebTool] Searching for: {query}\n")
    if "weather" in query.lower() and "dallas" in query.lower():
        return "The current weather in Dallas, TX is 75F and Sunny."
    return f"Results for {query}: The world is full of agentic possibilities."

def mock_get_stock_price(symbol: Annotated[str, "The stock symbol to check"]) -> str:
    """
    Retrieves the current stock price for a given symbol.
    """
    print(f"\n[FinanceTool] Getting price for: {symbol}\n")
    prices = {
        "AAPL": "150.00",
        "GOOGL": "2800.00",
        "TSLA": "750.00",
        "NVDA": "450.00"
    }
    price = prices.get(symbol.upper(), "Unknown")
    return f"The current price of {symbol} is ${price}."
