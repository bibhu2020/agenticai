from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from tools.yf_tools import _get_history, _get_analyst_recommendations
from tools.search_tools import _fetch_page_content, _duckduckgo_search, searchQuery, searchResult
from autogen_core.tools import FunctionTool 
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")
# os.environ["GEMINI_API_KEY"] = gemini_api_key

class StockTrend(BaseModel):
    stock_name: str
    trade_date: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

def get_stock_trends_agent():
    model_client = OpenAIChatCompletionClient( model="gemini-flash-latest",
                                                model_info={
                                                    "family": "gemini",
                                                    "vision": True,
                                                    "function_calling": True,
                                                    "json_output": True,
                                                },
                                                api_key=gemini_api_key,
                                                temperature=0)
    
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
        # output_content_type=StockTrend, 
    )
    return stock_trends_agent_assistant

def get_news_agent():
    model_client = OpenAIChatCompletionClient( model="gemini-flash-latest",
                                                model_info={
                                                    "family": "gemini",
                                                    "vision": True,
                                                    "function_calling": True,
                                                    "json_output": True,
                                                },
                                                api_key=gemini_api_key,
                                                temperature=0)

    async def news_search(query: str) -> str:
        """
        Search for latest news regarding a topic or stock.
        """
        # Use underlying function with proper params
        params = searchQuery(query=query, search_type="news", timelimit="d", max_results=5)
        # _duckduckgo_search returns list[dict], convert to str
        results = _duckduckgo_search(params)
        return str(results)

    news_tool = FunctionTool(news_search, description="Search for latest top 5 news for a given stock or topic. Returns headlines and snippets only.")

    # async def fetch_page_detail(url: str) -> str:
    #     """
    #     Fetch the content of a web page given its URL.
    #     """
    #     content = _fetch_page_content(url)
    #     return str(content) if content else "Failed to fetch content."

    # fetch_page_content_tool = FunctionTool(fetch_page_detail, description="MANDATORY: Fetch full article text from a URL. Use this to get details missing from snippets.") 

    news_agent = AssistantAgent(
        name="news_agent",
        model_client=model_client,
        tools=[news_tool],
        system_message=(
            "You are the News Agent. "
            "1. Search for the latest top 5 news stories related to the given stock using `news_tool`. "
            "2. Summarize the key insights from the news stories. "
            "Do NOT provide any final investment decision."
        )
    )
    return news_agent

def get_sentiment_agent():
    model_client = OpenAIChatCompletionClient( model="gemini-flash-latest",
                                                model_info={
                                                    "family": "gemini",
                                                    "vision": True,
                                                    "function_calling": True,
                                                    "json_output": True,
                                                },
                                                api_key=gemini_api_key,
                                                temperature=0)

    
    # We need to import these if not already available in the scope, 
    # but based on file viewing, we might need to add imports at the top.
    # Assuming imports are fixed in a separate step or I will import inside?
    # Better to fix imports globally.

    async def get_market_sentiment(symbol: str, period: str) -> str:
        """Get market sentiment for a stock."""
        from tools.yf_tools import _get_market_sentiment
        return _get_market_sentiment(symbol, period)

    async def get_analyst_recs(symbol: str) -> str:
        """Get analyst recommendations for a stock."""
        # _get_analyst_recommendations is already imported
        return _get_analyst_recommendations(symbol)

    sentiment_tool = FunctionTool(get_market_sentiment, description="Get market sentiment")
    analyst_tool = FunctionTool(get_analyst_recs, description="Get analyst recommendations")

    sentiment_agent = AssistantAgent(
        name="sentiment_agent",
        model_client=model_client,
        tools=[sentiment_tool, analyst_tool],
        system_message=(
            "You are the Market Sentiment Agent. "
            "You gather overall market sentiment, relevant analyst reports, and expert opinions. "
            "Do NOT provide any final investment decision."
        )
    )
    return sentiment_agent

def get_decision_agent():
    model_client = OpenAIChatCompletionClient( model="gemini-flash-latest",
                                                model_info={
                                                    "family": "gemini",
                                                    "vision": True,
                                                    "function_calling": True,
                                                    "json_output": True,
                                                },
                                                api_key=gemini_api_key,
                                                temperature=0)

    decision_agent = AssistantAgent(
        name="decision_agent",
        model_client=model_client,
        tools=[], # Decision agent usually synthesizes info, might not need tools if it consumes chat history
        system_message=(
            "You are the Decision Agent. After reviewing the stock data, news, sentiment, analyst reports, "
            "and expert opinions from the other agents, you provide the final investment decision. In the final decision make a call to either Invest or Not. Also provide the current stock price. "
            "End your response with 'Decision Made' once you finalize the decision."

        )
    )
    return decision_agent