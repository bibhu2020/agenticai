from ddgs import DDGS
from transformers import pipeline
import torch
import requests
from bs4 import BeautifulSoup
from typing import Optional

# Global variable for lazy loading
_sentiment_pipeline = None

def get_sentiment_pipeline():
    """
    Lazy loads the FinBERT pipeline.
    """
    print(f"[DEBUG] get_sentiment_pipeline called")
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            print("Loading FinBERT model...")
            # Use CPU to avoid CUDA complexity if not needed, or let torch decide if fast
            _sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        except Exception as e:
            print(f"Failed to load FinBERT: {e}")
            return None
    return _sentiment_pipeline

def _fetch_page_content(url: str, timeout: int = 5) -> Optional[str]:
    """Fetch and extract text content from a web page."""
    print(f"[DEBUG] fetch_page_content called with: {url} - timeout: {timeout}")
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove irrelevant elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"[WARNING] Failed to fetch content from {url}: {str(e)}")
        return None

from pydantic import BaseModel, Field
from typing import Optional
import concurrent.futures

# Validation Model
class NewsArticle(BaseModel):
    title: str = Field(..., description="The headline of the news article.")
    link: str = Field(..., description="The direct URL to the full article.")
    snippet: str = Field(..., description="A brief summary or body text.")
    datetime: Optional[str] = Field(None, description="Publication date if available.")

def search_news(ticker: str) -> str:
    """
    Searches for the latest news regarding the stock ticker using DuckDuckGo.
    Analyzes each headline with FinBERT for sentiment.
    Returns a summary string of the top 5 results with sentiment scores.
    """
    print(f"[DEBUG] search_news called with: {ticker}")
    try:
        if not ticker:
            return "No ticker provided for news search."
            
        ticker = ticker.upper().strip()
        query = f"{ticker} stock news financial"
        
        results = []
        sentiment_pipe = get_sentiment_pipeline()
        
        with DDGS() as ddgs:
            # Use 'news' backend
            raw_results = list(ddgs.news(query, max_results=5))
            
            if not raw_results:
                 return f"No recent news found for {ticker}."
            
            # Helper to process one item (fetch + analyze)
            def process_news_item(raw_item):
                try:
                    # Validate / Map Raw Dict to Pydantic Model
                    # DDGS returns: 'title', 'url', 'body', 'date', 'source'
                    # We map them to our requested schema
                    article = NewsArticle(
                        title=raw_item.get('title', 'No Title'),
                        link=raw_item.get('url', ''),
                        snippet=raw_item.get('body', ''),
                        datetime=raw_item.get('date', 'Unknown Date')
                    )
                except Exception as validation_err:
                    print(f"[WARNING] Skipping invalid news item: {validation_err}")
                    return None

                # Processing using Validated Object
                source = raw_item.get('source', 'Unknown Source') # Keep source for display
                
                # FinBERT Analysis
                sentiment_tag = ""
                if sentiment_pipe:
                    try:
                        # 1. Try to fetch full content
                        content_to_analyze = article.title
                        analysis_type = "Headline"
                        
                        if article.link:
                            full_text = _fetch_page_content(article.link)
                            if full_text and len(full_text) > 100:
                                content_to_analyze = full_text
                                analysis_type = "Full Text"
                        
                        # 2. Truncate for FinBERT
                        score = sentiment_pipe(content_to_analyze[:2000])[0]
                        label = score['label']
                        conf = round(score['score'], 2)
                        
                        sentiment_tag = f" [FinBERT ({analysis_type}): {label} ({conf})]"
                        print(f"[DEBUG] FinBERT analysis for {article.title}: {sentiment_tag}")
                    except Exception as e:
                        sentiment_tag = f" [FinBERT: Error ({str(e)[:50]})]"

                return f"- [{source} | {article.datetime}] {article.title}{sentiment_tag}"

            # Run in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # filter out None results from validation failures
                results = [r for r in executor.map(process_news_item, raw_results) if r is not None]
        
        if not results:
            return f"No recent news found for {ticker}."
            
        return f"Recent News for {ticker} (with FinBERT Analysis):\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"
