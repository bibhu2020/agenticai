from langchain_core.tools import tool
import random

class ActionLayer:
    """
    Defines the 'Hands' of the agent (Tools) using LangChain @tool decorator.
    """
    
    @staticmethod
    @tool
    def mock_search_web(query: str) -> str:
        """
        Simulates a web search engine. Use this when you need to find current information,
        news, or weather.
        """
        print(f"\n[WebTool] Searching for: {query}\n")
        
        # Scenario 2 Simulation
        if "weather" in query.lower() and "dallas" in query.lower():
            return "The current weather in Dallas, TX is 75F and Sunny."
            
        return f"Results for {query}: The world is full of agentic possibilities."

    @staticmethod
    @tool
    def mock_get_stock_price(symbol: str) -> str:
        """
        Retrieves the current stock price for a given symbol.
        """
        print(f"\n[FinanceTool] Getting price for: {symbol}\n")
        
        # Scenario 1 Simulation
        prices = {
            "AAPL": "150.00",
            "GOOGL": "2800.00",
            "TSLA": "750.00",
            "NVDA": "450.00"
        }
        price = prices.get(symbol.upper(), "Unknown")
        return f"The current price of {symbol} is ${price}."

    def get_common_tools(self):
        return []
        
    def get_finance_tools(self):
        return [self.mock_get_stock_price]
        
    def get_web_tools(self):
        return [self.mock_search_web]
