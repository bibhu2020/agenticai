from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import FunctionTool 
from tools.yf_tools import _get_history
from core.model import get_model_client
    
def get_stock_trends_agent():
    model_client = get_model_client()
    
    async def fetch_stock_history(symbol: str, period: str) -> str:
        """
        Gets real-time stock prices and changes over the last few months for the given stock name.
        
        Args:
            symbol: The stock ticker symbol (e.g., 'TSLA', 'AAPL').
            period: The period to fetch data for (e.g., '1mo', '3mo').
        
        Returns:
            str: A formatted string showing the historical prices.
        """
        return _get_history(symbol, period)
    
    get_history_tool = FunctionTool(fetch_stock_history, description="Gets real-time stock prices, changes over the last few months for 'stock_name'", strict=True)
    
    stock_trends_agent_assistant = AssistantAgent(
        name="stock_trends_agent",
        model_client=model_client,
        tools=[get_history_tool],
        system_message=(
            "You are the Stock Price Trends Agent practicing in India and USA stock markets. "
            "You fetch and summarize stock prices, changes over the last 3 months, and general market trends. "
            "Do NOT provide any final investment decision."
        ),
    )
    return stock_trends_agent_assistant
