from ddgs import DDGS
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel, Field
import concurrent.futures

# Global variable for lazy loading
_sentiment_pipeline = None

def get_sentiment_pipeline():
    """
    Lazy loads the FinBERT pipeline.
    """
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            print("Loading FinBERT model...")
            _sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        except Exception as e:
            print(f"Failed to load FinBERT: {e}")
            return None
    return _sentiment_pipeline

def _fetch_page_content(url: str, timeout: int = 5) -> Optional[str]:
    """Fetch and extract text content from a web page."""
    try:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator='\n', strip=True)
        return text
    except Exception:
        return None

class NewsArticle(BaseModel):
    title: str
    link: str
    snippet: str
    datetime: Optional[str]

def get_news_sentiment(ticker: str) -> dict:
    """
    Fetches news and returns a structured sentiment summary.
    """
    if not ticker:
        return {"sentiment": "Neutral", "score": 0.0, "summary": "No ticker provided."}
        
    ticker = ticker.upper().strip()
    query = f"{ticker} stock news financial"
    
    sentiment_pipe = get_sentiment_pipeline()
    
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.news(query, max_results=5))
            
        if not raw_results:
             return {"sentiment": "Neutral", "score": 0.5, "summary": f"No recent news found for {ticker}."}
        
        # Determine overall sentiment
        # Simplified logic: Average score of headlines
        total_score = 0
        count = 0
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        summaries = []
        
        for item in raw_results:
            title = item.get('title', '')
            link = item.get('url', '')
            
            # Init score
            score_val = 0 # Neutral
            label = "neutral"
            
            if sentiment_pipe:
                try:
                    res = sentiment_pipe(title[:512])[0]
                    label = res['label'] # positive, negative, neutral
                    conf = res['score']
                    
                    if label == 'positive': 
                        score_val = 1 * conf
                        sentiment_counts["positive"] += 1
                    elif label == 'negative': 
                        score_val = -1 * conf
                        sentiment_counts["negative"] += 1
                    else:
                        sentiment_counts["neutral"] += 1
                        
                except Exception:
                    pass
            
            total_score += score_val
            count += 1
            summaries.append(f"- {title} [{label}]")

        # Aggregate
        final_score = total_score / count if count > 0 else 0
        
        overall_sentiment = "Neutral"
        if final_score > 0.1: overall_sentiment = "Bullish"
        elif final_score < -0.1: overall_sentiment = "Bearish"
        
        return {
            "sentiment": overall_sentiment,
            "score": round(0.5 + (final_score / 2), 2), # Normalize -1..1 to 0..1
            "summary": "\n".join(summaries)
        }

    except Exception as e:
        return {"sentiment": "Neutral", "score": 0.0, "summary": f"Error: {str(e)}"}
