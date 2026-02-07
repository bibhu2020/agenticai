
"""
Trading Research MCP Server
"""
import sys
import os
import yfinance as yf
from textblob import TextBlob
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize FastMCP Server
mcp = FastMCP("Trading Research")

@mcp.tool()
def get_news_sentiment(symbol: str) -> List[Dict[str, Any]]:
    """
    Get recent news and analyze sentiment for a stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        
        results = []
        for item in news:
            title = item.get("title", "")
            if not title:
                continue
                
            blob = TextBlob(title)
            sentiment = blob.sentiment.polarity
            
            sentiment_label = "NEUTRAL"
            if sentiment > 0.1:
                sentiment_label = "POSITIVE"
            elif sentiment < -0.1:
                sentiment_label = "NEGATIVE"
                
            results.append({
                "title": title,
                "publisher": item.get("publisher", "Unknown"),
                "link": item.get("link", ""),
                "published": item.get("providerPublishTime", ""),
                "sentiment_score": round(sentiment, 2),
                "sentiment_label": sentiment_label
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_insider_trades(symbol: str) -> List[Dict[str, Any]]:
    """
    Get recent insider trading activity.
    """
    try:
        ticker = yf.Ticker(symbol)
        insider = ticker.insider_transactions
        
        if insider is None or insider.empty:
            return []
            
        # Convert top 5 recent trades to dict
        recent = insider.head(5).reset_index()
        # Handle potential date columns and serialization
        recent = recent.astype(str) # Simplest way to ensure JSON serializable
        return recent.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_analyst_ratings(symbol: str) -> List[Dict[str, Any]]:
    """
    Get recent analyst recommendations.
    """
    try:
        ticker = yf.Ticker(symbol)
        recs = ticker.recommendations
        
        if recs is None or recs.empty:
            return []
            
        # Recent recommendations
        recent = recs.tail(5).reset_index()
        recent = recent.astype(str)
        return recent.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_sec_filings(symbol: str) -> List[Dict[str, Any]]:
    """
    Get recent SEC filing links (10-K, 10-Q).
    Note: yfinance might not support this reliably, falling back to mock if needed or using news.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Some versions have .sec_filings, others don't.
        # Fallback: Search news for "Filing" or check .news
        # Or simple mock for now if API not available
        return [{"info": "SEC Filings retrieval requires EDGAR API key or advanced scraping. Showing placeholder."}]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    mcp.run()
