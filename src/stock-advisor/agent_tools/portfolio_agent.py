# agents/portfolio_agent.py
"""
Portfolio Agent
---------------
Responsible for managing stock positions, portfolio value, and tracking performance.
Features:
- Add/remove positions
- Update stock prices
- Calculate portfolio value and allocation
- Track historical performance
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PortfolioAgent:
    def __init__(self):
        self.name = "PortfolioAgent"
        self.positions: Dict[str, Dict] = {}  # {symbol: {"shares": int, "price": float}}

    def add_position(self, symbol: str, shares: int, price: float):
        """Add new position or update existing one"""
        if symbol in self.positions:
            self.positions[symbol]["shares"] += shares
            self.positions[symbol]["price"] = price  # Update latest price
        else:
            self.positions[symbol] = {"shares": shares, "price": price}
        logger.info("Added/Updated position: %s", self.positions[symbol])

    def remove_position(self, symbol: str, shares: int):
        """Remove shares from a position; delete if zero"""
        if symbol in self.positions:
            self.positions[symbol]["shares"] -= shares
            if self.positions[symbol]["shares"] <= 0:
                del self.positions[symbol]
                logger.info("Position %s removed from portfolio", symbol)
            else:
                logger.info("Updated position: %s", self.positions[symbol])
        else:
            logger.warning("Cannot remove position; %s not in portfolio", symbol)

    def update_price(self, symbol: str, price: float):
        """Update price of a position"""
        if symbol in self.positions:
            self.positions[symbol]["price"] = price
            logger.info("Updated price for %s: %s", symbol, price)
        else:
            logger.warning("Cannot update price; %s not in portfolio", symbol)

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        total = sum(pos["shares"] * pos["price"] for pos in self.positions.values())
        logger.info("Total portfolio value: %s", total)
        return total

    def get_positions(self) -> Dict[str, Dict]:
        """Return current positions"""
        return self.positions.copy()


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    portfolio = PortfolioAgent()
    portfolio.add_position("AAPL", 10, 175.0)
    portfolio.add_position("TSLA", 5, 900.0)
    portfolio.update_price("AAPL", 180.0)
    portfolio.remove_position("TSLA", 2)

    print("Portfolio value:", portfolio.get_portfolio_value())
    print("Positions:", portfolio.get_positions())
