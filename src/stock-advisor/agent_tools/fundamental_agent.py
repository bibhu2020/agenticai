# agents/fundamental_agent.py
"""
Fundamental Agent
-----------------
Responsible for analyzing company fundamentals.
Features:
- Fetch financial statements (income, balance sheet, cashflow)
- Compute key ratios (P/E, Debt/Equity, ROE, etc.)
- Provide a simple fundamental signal (Strong/Neutral/Weak)
"""

import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FundamentalAgent:
    def __init__(self):
        self.name = "FundamentalAgent"

    def fetch_financials(self, symbol: str) -> dict:
        """
        Fetch financial statements from Yahoo Finance.
        Returns a dictionary with income, balance sheet, cashflow, and earnings.
        """
        try:
            ticker = yf.Ticker(symbol)
            financials = {
                "financials": ticker.financials,
                "balance_sheet": ticker.balance_sheet,
                "cashflow": ticker.cashflow,
                "earnings": ticker.income_stmt if hasattr(ticker, "income_stmt") else pd.DataFrame()
            }
            logger.info("Fetched financials for %s", symbol)
            return financials
        except Exception as e:
            logger.exception("Failed to fetch financials for %s: %s", symbol, e)
            return {}

    def calculate_ratios(self, financials: dict) -> dict:
        """
        Compute key financial ratios from fetched data.
        """
        ratios = {}
        try:
            bs = financials.get("balance_sheet", pd.DataFrame())
            fs = financials.get("financials", pd.DataFrame())

            if not bs.empty and not fs.empty:
                # Example ratios
                ratios["debt_to_equity"] = bs.loc["Total Liab"].iloc[0] / bs.loc["Total Stockholder Equity"].iloc[0]
                ratios["roe"] = fs.loc["Net Income"].iloc[0] / bs.loc["Total Stockholder Equity"].iloc[0]
                ratios["profit_margin"] = fs.loc["Net Income"].iloc[0] / fs.loc["Total Revenue"].iloc[0]
            else:
                logger.warning("Insufficient financial data to compute ratios")
        except Exception as e:
            logger.exception("Error calculating financial ratios: %s", e)
        return ratios

    def analyze(self, symbol: str) -> dict:
        """
        Perform full fundamental analysis: fetch financials, compute ratios, generate signal.
        """
        financials = self.fetch_financials(symbol)
        if not financials:
            return {"signal": "Data Unavailable", "ratios": {}, "financials": {}}

        ratios = self.calculate_ratios(financials)

        # Simple signal logic
        signal = "Neutral"
        try:
            if ratios:
                if ratios.get("roe", 0) > 0.15 and ratios.get("debt_to_equity", 0) < 1:
                    signal = "Strong"
                elif ratios.get("roe", 0) < 0.05:
                    signal = "Weak"
        except Exception as e:
            logger.exception("Error generating fundamental signal: %s", e)

        analysis = {
            "signal": signal,
            "ratios": ratios,
            "financials": financials
        }
        logger.info("Fundamental analysis for %s complete. Signal: %s", symbol, signal)
        return analysis


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    agent = FundamentalAgent()
    symbol = "AAPL"
    result = agent.analyze(symbol)
    print("Fundamental Analysis Result:")
    print(result)
