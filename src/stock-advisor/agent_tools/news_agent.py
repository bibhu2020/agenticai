# agents/news_agent.py
"""
News Agent
----------
Responsible for fetching the latest financial news and analyzing sentiment.

Features:
- Fetch news by company name or ticker
- Analyze sentiment using OpenAI LLM (or another sentiment model)
- Return structured news + sentiment

Notes:
- Requires .env file with OPENAI_API_KEY and NEWS_API_KEY
- Can be extended to fetch RSS feeds, Yahoo Finance news, or web scraping
"""

import os
import logging
from typing import List, Dict
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class NewsAgent:
    def __init__(self):
        self.name = "NewsAgent"
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.client = OpenAI(api_key=self.OPENAI_API_KEY) if self.OPENAI_API_KEY else None

        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Sentiment analysis will return 'Neutral'.")
        if not self.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not set. News fetching will return empty list.")

        self.NEWS_API_URL = "https://newsapi.org/v2/everything"

    def fetch_news(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Fetch the latest news articles for a query (company or ticker)
        Returns a list of dicts: {title, description, url, publishedAt}
        """
        if not self.NEWS_API_KEY:
            logger.error("NEWS_API_KEY not set. Cannot fetch news.")
            return []

        params = {
            "q": query,
            "apiKey": self.NEWS_API_KEY,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "language": "en"
        }

        try:
            response = requests.get(self.NEWS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            news_list = [
                {
                    "title": a.get("title"),
                    "description": a.get("description"),
                    "url": a.get("url"),
                    "publishedAt": a.get("publishedAt")
                }
                for a in articles
            ]
            logger.info("Fetched %d articles for query '%s'", len(news_list), query)
            return news_list
        except Exception as e:
            logger.exception("Failed to fetch news: %s", e)
            return []

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of a text using OpenAI.
        Returns: "Positive", "Neutral", or "Negative"
        """
        if not self.OPENAI_API_KEY:
            return "Neutral"

        if not text.strip():
            return "Neutral"

        try:
            prompt = f"Classify the sentiment of the following financial news headline into Positive, Neutral, or Negative:\n\n{text}\n\nSentiment:"
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            sentiment = response.choices[0].message.content.strip()
            return sentiment
        except Exception as e:
            logger.exception("Failed to analyze sentiment: %s", e)
            return "Neutral"

    def fetch_and_analyze(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Fetch news and attach sentiment analysis
        """
        articles = self.fetch_news(query, limit)
        for article in articles:
            headline = article.get("title") or ""
            article["sentiment"] = self.analyze_sentiment(headline)
        return articles


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    agent = NewsAgent()
    news = agent.fetch_and_analyze("Apple", limit=3)
    for n in news:
        print(f"{n['publishedAt']}: {n['title']} [{n['sentiment']}]")
