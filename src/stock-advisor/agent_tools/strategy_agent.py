# agents/strategy_agent.py
"""
Strategy Agent
--------------
Responsible for generating actionable trading or investment recommendations
by combining signals from other agents (Technical, Fundamental, Sentiment).
"""

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class StrategyAgent:
    def __init__(self):
        self.name = "StrategyAgent"

    def generate_strategy(self, technical_signal: str, fundamental_signal: str, sentiment_signal: str) -> str:
        """
        Generate an overall strategy based on multiple agent signals.
        Logic:
        - Buy if most signals are positive/strong
        - Sell if most signals are negative/weak
        - Hold otherwise
        """
        signals = {
            "Technical": technical_signal,
            "Fundamental": fundamental_signal,
            "Sentiment": sentiment_signal
        }

        logger.info("Received signals: %s", signals)

        positive = ["Buy", "Strong", "Positive"]
        negative = ["Sell", "Weak", "Negative"]

        pos_count = sum(1 for s in signals.values() if s in positive)
        neg_count = sum(1 for s in signals.values() if s in negative)

        if pos_count > neg_count:
            strategy = "Buy"
        elif neg_count > pos_count:
            strategy = "Sell"
        else:
            strategy = "Hold"

        logger.info("Generated strategy: %s", strategy)
        return strategy


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    agent = StrategyAgent()
    technical_signal = "Buy"
    fundamental_signal = "Strong"
    sentiment_signal = "Positive"

    strategy = agent.generate_strategy(technical_signal, fundamental_signal, sentiment_signal)
    print(f"Recommended Strategy: {strategy}")
