from ddgs import DDGS
from transformers import pipeline
import torch
from curl_cffi import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime
import time
from typing import Optional
from pydantic import BaseModel, Field
import concurrent.futures

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

def _fetch_page_content(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch and extract text content from a web page."""
    print(f"[DEBUG] Fetching: {url}")
    start_time = time.time()
    try:
        # Use curl_cffi to impersonate Chrome 110 (Bypasses TLS Fingerprinting)
        # Headers are auto-managed by impersonate
        response = requests.get(url, timeout=timeout, impersonate="chrome110")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove ads, popups, and non-content elements
        # Targeted classes: .ad, .popup, .modal, .cookie-banner, etc.
        for tag in soup.select("script, style, nav, footer, header, aside, form, iframe, .ad, .popup, .modal, .cookie-banner, [id*='popup'], [class*='popup'], [class*='ad-'], [class*='banner']"):
            tag.decompose()
            
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        duration = round(time.time() - start_time, 2)
        print(f"[DEBUG] Fetch success ({duration}s): {url}")
        return text
    except Exception as e:
        msg = str(e)
        if "403" in msg:
             print(f"[INFO] Access denied (403) for {url}. Falling back to snippet.")
        else:
             print(f"[WARNING] Failed to fetch content from {url}: {msg}")
        return None

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
        articles_pool = []
        
        # 1. Fetch from Yahoo Finance API (Reliable)
        try:
             print("[DEBUG] Fetching YF API news...")
             yf_ticker = yf.Ticker(ticker)
             yf_raw = yf_ticker.news
             if yf_raw:
                 for item in yf_raw:
                     ts = item.get('providerPublishTime')
                     date_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d') if ts else 'Unknown'
                     articles_pool.append(NewsArticle(
                         title=item.get('title', 'No Title'),
                         link=item.get('link', ''),
                         snippet=f"Source: {item.get('publisher')} - {date_str}",
                         datetime=date_str
                     ))
        except Exception as e:
             print(f"[WARNING] YF API failed: {e}")
             
        # 2. Add DuckDuckGo Targeted Search (Secondary)
        # Targeted sites: CNBC, Bloomberg, Investing.com, MarketWatch
        query = f"{ticker} stock news (site:cnbc.com OR site:bloomberg.com OR site:investing.com OR site:marketwatch.com)"
        
        with DDGS() as ddgs:
            raw_results = list(ddgs.news(query, max_results=10))
            for raw_item in raw_results:
                try:
                    articles_pool.append(NewsArticle(
                        title=raw_item.get('title', 'No Title'),
                        link=raw_item.get('url', ''),
                        snippet=raw_item.get('body', ''),
                        datetime=raw_item.get('date', 'Unknown')
                    ))
                except: continue

        if not articles_pool:
             return f"No recent news found for {ticker}."
             
        # Deduplicate by Title
        seen_titles = set()
        unique_articles = []
        for a in articles_pool:
            if a.title not in seen_titles:
                seen_titles.add(a.title)
                unique_articles.append(a)
        
        # Analyze Top 5
        top_articles = unique_articles[:5]
        sentiment_pipe = get_sentiment_pipeline()
        
        results = []
        
        # Helper to process
        def process_article(article):
            # FinBERT Analysis
            sentiment_tag = ""
            if sentiment_pipe:
                try:
                    # Prefer full text fetch, fallback to Snippet
                    content = article.snippet if article.snippet else article.title
                    analysis_type = "Snippet" if article.snippet else "Headline"
                    
                    
                    # Try fetch full text with improved headers
                    if article.link:
                        full_text = _fetch_page_content(article.link)
                        if full_text and len(full_text) > 100:
                             content = full_text
                             analysis_type = "Full Text"
                        else:
                             # Fallback log
                             print(f"[DEBUG] Content too short/failed for {article.title[:30]}... using Snippet.")
                    
                    # Truncate for BERT
                    score = sentiment_pipe(content[:2000])[0]
                    label = score['label']
                    conf = round(score['score'], 2)
                    sentiment_tag = f" [FinBERT ({analysis_type}): {label} ({conf})]"
                except Exception as e:
                    sentiment_tag = f" [FinBERT: Error]"
            
            return f"- [{article.datetime}] {article.title}{sentiment_tag}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(process_article, top_articles))
            
        return f"Recent News for {ticker} (Sources: YF, CNBC, Bloomberg, Investing):\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"
