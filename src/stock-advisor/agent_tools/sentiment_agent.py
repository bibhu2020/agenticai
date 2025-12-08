# agents/sentiment_agent.py
import os
from dotenv import load_dotenv
import requests
from textblob import TextBlob
import logging

load_dotenv()  # load API_KEY from .env

logger = logging.getLogger(__name__)

class SentimentAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Sentiment analysis will use TextBlob fallback.")

    def fetch_news(self, symbol: str):
        # Dummy fetch from a public endpoint or mock
        logger.info(f"Fetching news for {symbol}")
        # Replace with your actual news fetch logic or mock in tests
        return [
            "Company beats earnings estimates!",
            "Stock sees strong growth this quarter."
        ]

    def analyze_sentiment(self, texts):
        if not texts:
            return "Neutral"
        if self.api_key:
            # Use OpenAI API here if key exists (optional)
            # openai_client = OpenAI(api_key=self.api_key)
            # return openai_client.sentiment_analysis(texts)
            return "Positive"  # dummy return for now
        else:
            # fallback to TextBlob if no API key
            sentiments = [TextBlob(t).sentiment.polarity for t in texts]
            avg_sentiment = sum(sentiments) / len(sentiments)
            if avg_sentiment > 0.1:
                return "Positive"
            elif avg_sentiment < -0.1:
                return "Negative"
            else:
                return "Neutral"
