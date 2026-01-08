from typing import Any, Dict, List, Callable
from agents import function_tool

# --- Tool Definitions ---

@function_tool
def calculate(expression: str) -> str:
    """
    Evaluates a mathematical expression (e.g., "120 + 25").
    """
    try:
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
        return str(eval(expression))
    except Exception:
        return "Error in calculation"

@function_tool
def save_note(filename: str, content: str) -> str:
    """
    Saves text to a file.
    """
    with open(filename, 'w') as f:
        f.write(content)
    return f"File {filename} saved successfully."

@function_tool
def read_note(filename: str) -> str:
    """
    Reads the content of a file.
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: File not found."

@function_tool
def mock_search_web(query: str) -> str:
    """
    Simulates a web search engine. Use this for general knowledge questions.
    Returns simulated search results.
    """
    print(f"\n[WebTool] Searching for: {query}\n")
    # Simulating simple responses
    if "weather" in query.lower():
        if "dallas" in query.lower():
            return "Search Result: The current weather in Dallas, TX is 75F and Sunny."
        return "Search Result: Standard weather patterns indicate mostly sunny skies with a chance of rain in the evening."
    elif "news" in query.lower():
        return "Search Result: Breaking News - AI Agent architecture is evolving rapidly."
    return f"Search Result: Some general information about '{query}' found on multiple websites."

@function_tool
def mock_get_stock_price(symbol: str) -> str:
    """
    Fetches the current stock price for a given symbol from Yahoo Finance (Simulated).
    """
    print(f"[FinanceTool] Getting price for: {symbol}")
    symbol = symbol.upper()
    # Mock data
    prices = {
        "AAPL": "150.25 USD",
        "MSFT": "310.50 USD",
        "GOOGL": "140.00 USD",
        "NVDA": "450.75 USD",
        "TSLA": "240.20 USD"
    }
    return prices.get(symbol, f"Price for {symbol} not found.")

# --- Layer Definition ---

class ActionLayer:
    """
    The 'Hands' of the agent.
    Responsibility: Expose specific, tools arranged by domain.
    """
    
    def __init__(self):
        pass # No default tools
    
    def get_common_tools(self) -> List[Callable]:
        return [calculate, save_note, read_note]
        
    def get_web_tools(self) -> List[Callable]:
        return [mock_search_web]
        
    def get_finance_tools(self) -> List[Callable]:
        return [mock_get_stock_price]
