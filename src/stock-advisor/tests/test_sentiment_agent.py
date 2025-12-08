# tests/test_sentiment_agent.py
import pytest
from agents.sentiment_agent import SentimentAgent
from unittest.mock import patch

@pytest.fixture
def agent():
    return SentimentAgent()

def test_analyze_sentiment_empty(agent):
    result = agent.analyze_sentiment([])
    assert result == "Neutral"

def test_analyze_sentiment_no_api_key(monkeypatch):
    # Temporarily remove API key
    monkeypatch.setenv("OPENAI_API_KEY", "")
    agent = SentimentAgent()
    texts = ["Good news for the company"]
    result = agent.analyze_sentiment(texts)
    # Should fallback to TextBlob
    assert result in ["Positive", "Neutral", "Negative"]

def test_analyze_sentiment_mocked_api(agent):
    texts = ["Great earnings report!"]
    with patch.object(agent, "analyze_sentiment", return_value="Positive") as mock_method:
        result = agent.analyze_sentiment(texts)
        mock_method.assert_called_once_with(texts)
        assert result == "Positive"

def test_analyze_sentiment_invalid_response(agent):
    texts = ["Some neutral news."]
    with patch.object(agent, "analyze_sentiment", return_value="Unknown") as mock_method:
        result = agent.analyze_sentiment(texts)
        mock_method.assert_called_once_with(texts)
        assert result == "Unknown"

def test_fetch_news(agent):
    # We can patch this to avoid real API calls
    with patch.object(agent, "fetch_news", return_value=["News 1", "News 2"]) as mock_news:
        news = agent.fetch_news("AAPL")
        mock_news.assert_called_once_with("AAPL")
        assert news == ["News 1", "News 2"]
