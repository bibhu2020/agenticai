# core/orchestrator.py
import logging
import pandas as pd
from agents.data_agent import DataAgent
from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent import StrategyAgent
from agents.portfolio_agent import PortfolioAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.data_agent = DataAgent()
        self.technical_agent = TechnicalAgent()
        self.fundamental_agent = FundamentalAgent()
        self.sentiment_agent = SentimentAgent()
        self.strategy_agent = StrategyAgent()
        self.portfolio_agent = PortfolioAgent()

    def analyze_stock(self, symbol: str) -> dict:
        """Main orchestrator function to analyze a stock and generate strategy"""
        logger.info("Starting analysis for: %s", symbol)

        # Step 1: Fetch data
        latest_price = self.data_agent.latest_price(symbol)
        financials = self.data_agent.financials(symbol)
        ohlcv = self.data_agent.ohlcv(symbol)  # Pass DataFrame to TechnicalAgent

        # Step 2: Technical Analysis
        tech_signal = self.technical_agent.analyze(ohlcv)

        # Step 3: Fundamental Analysis
        fund_signal = self.fundamental_agent.analyze(financials)

        # Step 4: Sentiment Analysis
        news_headlines = self.sentiment_agent.fetch_news(symbol)
        sentiment_signal = self.sentiment_agent.analyze_sentiment(" ".join(news_headlines))

        # Step 5: Strategy
        strategy = self.strategy_agent.generate_strategy(
            tech_signal, fund_signal, sentiment_signal
        )

        # Step 6: Portfolio info
        portfolio_value = self.portfolio_agent.get_portfolio_value()

        result = {
            "symbol": symbol,
            "latest_price": latest_price,
            "technical": tech_signal,
            "fundamental": fund_signal,
            "sentiment": sentiment_signal,
            "strategy": strategy,
            "portfolio_value": portfolio_value,
            "news_headlines": news_headlines,
        }

        logger.info("Analysis complete for %s: %s", symbol, result)
        return result


def main():
    orchestrator = Orchestrator()
    symbol = input("Enter stock symbol to analyze: ").strip().upper()
    result = orchestrator.analyze_stock(symbol)
    
    print("\n--- Stock Analysis Result ---")
    print(f"Symbol: {result['symbol']}")
    print(f"Latest Price: {result['latest_price']}")
    print(f"Technical Signal: {result['technical']}")
    print(f"Fundamental Signal: {result['fundamental']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Portfolio Value: {result['portfolio_value']}")
    print("News Headlines:")
    for i, headline in enumerate(result['news_headlines'], 1):
        print(f"{i}. {headline}")


if __name__ == "__main__":
    main()
