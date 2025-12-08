# tests/test_news_agent.py
import pytest
from unittest.mock import patch, MagicMock
from agents.news_agent import NewsAgent

@pytest.fixture
def agent():
    """Return a reusable NewsAgent instance"""
    return NewsAgent()

def mock_fetch_news(*args, **kwargs):
    """Mocked news data"""
    return [
        {
            "title": "Apple releases new iPhone",
            "description": "The new iPhone 16 is out now",
            "url": "http://example.com/iphone16",
            "publishedAt": "2025-10-20T10:00:00Z"
        },
        {
            "title": "Apple stock hits record high",
            "description": "Investors are bullish on Apple",
            "url": "http://example.com/apple-stock",
            "publishedAt": "2025-10-19T09:00:00Z"
        }
    ]

def mock_analyze_sentiment(text):
    """Return fake sentiment based on keyword"""
    if "record high" in text:
        return "Positive"
    elif "releases new iPhone" in text:
        return "Neutral"
    return "Negative"

@patch.object(NewsAgent, 'fetch_news', side_effect=mock_fetch_news)
@patch.object(NewsAgent, 'analyze_sentiment', side_effect=mock_analyze_sentiment)
def test_fetch_and_analyze(mock_sentiment, mock_fetch, agent):
    """Test fetch_and_analyze returns news with sentiment"""
    result = agent.fetch_and_analyze("Apple", limit=2)
    
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 2, "Should return two articles"
    
    for article in result:
        assert "title" in article, "Article must have title"
        assert "sentiment" in article, "Article must have sentiment"
        assert article["sentiment"] in ["Positive", "Neutral", "Negative"], "Invalid sentiment"

def test_analyze_sentiment_without_api_key(agent):
    """Test that sentiment returns 'Neutral' if OPENAI_API_KEY is missing"""
    agent.OPENAI_API_KEY = None
    sentiment = agent.analyze_sentiment("Any headline")
    assert sentiment == "Neutral"

def test_fetch_news_without_api_key(agent):
    """Test that fetch_news returns empty list if NEWS_API_KEY is missing"""
    agent.NEWS_API_KEY = None
    news = agent.fetch_news("Apple")
    assert news == []
