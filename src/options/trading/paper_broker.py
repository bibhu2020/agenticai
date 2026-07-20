"""
Paper trading broker — simulates option order execution.
All fills are at the mid price; no slippage model (paper trading).
"""
import logging
from database.models import (
    get_portfolio, update_portfolio, create_position,
    update_position, close_position, record_trade, log_event
)

logger = logging.getLogger(__name__)

CONTRACTS_MULTIPLIER = 100   # 1 contract = 100 shares


class PaperBroker:
    """Stateless broker; reads/writes portfolio state via DB helpers."""

    # ── Sell Put ──────────────────────────────────────────────────────────────

    def sell_put(self, ticker: str, strike: float, expiry: str,
                 premium: float, contracts: int = 1,
                 underlying_price: float = None, signal_id: int = None) -> dict:
        """
        Open a sell-put position.
        Premium collected = premium * contracts * 100
        Margin requirement (cash hold) = strike * contracts * 100 * 0.20
        """
        portfolio = get_portfolio()
        cash = portfolio["cash"]

        credit   = round(premium * contracts * CONTRACTS_MULTIPLIER, 2)
        margin   = round(strike  * contracts * CONTRACTS_MULTIPLIER * 0.20, 2)

        if margin > cash:
            msg = f"Insufficient cash for {ticker} sell-put (need ${margin:.0f}, have ${cash:.0f})"
            log_event("broker", msg, "WARNING")
            return {"success": False, "reason": msg}

        # Collect premium, hold margin
        new_cash = round(cash + credit - margin, 2)
        update_portfolio(cash=new_cash)

        pos_id = create_position(
            ticker            = ticker,
            position_type     = "SELL_PUT",
            strike            = strike,
            expiry            = expiry,
            contracts         = contracts,
            underlying_price  = underlying_price,
            premium_collected = credit,
            signal_id         = signal_id,
        )

        record_trade(
            position_id = pos_id,
            ticker      = ticker,
            action      = "SELL_PUT",
            strike      = strike,
            expiry      = expiry,
            contracts   = contracts,
            price       = premium,
            total_value = credit,
            notes       = f"Premium ${premium:.2f} × {contracts} × 100 = ${credit:.2f} credit",
        )

        # Store margin for later release
        update_position(pos_id, current_premium=credit)

        msg = f"SELL PUT {ticker} ${strike:.0f} exp {expiry} | credit=${credit:.2f}"
        log_event("broker", msg, "INFO")
        return {"success": True, "position_id": pos_id, "credit": credit, "margin": margin}

    # ── Close Put ─────────────────────────────────────────────────────────────

    def close_put(self, position_id: int, current_premium: float,
                  reason: str = "MANUAL") -> dict:
        """
        Buy back the put to close the position.
        Debit = current_premium * contracts * 100
        """
        from database.models import get_position
        pos = get_position(position_id)
        if not pos or pos["status"] != "OPEN":
            return {"success": False, "reason": "Position not found or already closed"}

        contracts   = pos["contracts"]
        orig_credit = pos["premium_collected"]
        strike      = pos["strike"]

        debit  = round(current_premium * contracts * CONTRACTS_MULTIPLIER, 2)
        margin = round(strike * contracts * CONTRACTS_MULTIPLIER * 0.20, 2)

        pnl     = round(orig_credit - debit, 2)
        pnl_pct = round(pnl / orig_credit, 4) if orig_credit else 0

        # Release margin, pay debit
        portfolio = get_portfolio()
        new_cash  = round(portfolio["cash"] + margin - debit, 2)
        update_portfolio(cash=new_cash)

        close_position(position_id, pnl, pnl_pct, reason, current_premium)

        record_trade(
            position_id = position_id,
            ticker      = pos["ticker"],
            action      = "BUY_PUT",
            strike      = pos["strike"],
            expiry      = pos["expiry"],
            contracts   = contracts,
            price       = current_premium,
            total_value = -debit,
            notes       = f"Closed: reason={reason}, P&L=${pnl:.2f} ({pnl_pct*100:.1f}%)",
        )

        msg = (f"CLOSE PUT {pos['ticker']} ${pos['strike']:.0f} | "
               f"P&L=${pnl:.2f} ({pnl_pct*100:.1f}%) reason={reason}")
        log_event("broker", msg, "INFO")
        return {"success": True, "pnl": pnl, "pnl_pct": pnl_pct}

    # ── Stock assignment (put exercised) ──────────────────────────────────────

    def assign_stock(self, position_id: int) -> dict:
        """
        Called when a put is in-the-money at expiry — we get assigned the stock.
        Creates a LONG_STOCK position at the strike price.
        """
        from database.models import get_position, create_position
        pos = get_position(position_id)
        if not pos:
            return {"success": False, "reason": "Position not found"}

        contracts = pos["contracts"]
        strike    = pos["strike"]
        shares    = contracts * CONTRACTS_MULTIPLIER
        cost      = round(shares * strike, 2)

        portfolio = get_portfolio()
        margin    = round(strike * contracts * CONTRACTS_MULTIPLIER * 0.20, 2)

        # Release margin, pay full cost of stock
        new_cash = round(portfolio["cash"] + margin - cost, 2)
        if new_cash < 0:
            # If cash is too low, partial assignment
            new_cash = 0.0
        update_portfolio(cash=new_cash)

        # Close original put as assigned
        orig_premium = pos["premium_collected"]
        pnl     = orig_premium - cost + cost   # P&L realised on put = just the premium
        close_position(position_id, orig_premium, 1.0, "ASSIGNED", 0)

        # Open a stock position
        stock_pos_id = create_position(
            ticker            = pos["ticker"],
            position_type     = "LONG_STOCK",
            strike            = strike,      # cost basis
            expiry            = None,
            contracts         = shares,
            underlying_price  = strike,
            premium_collected = 0,
        )

        record_trade(
            position_id = stock_pos_id,
            ticker      = pos["ticker"],
            action      = "BUY_STOCK",
            strike      = strike,
            expiry      = None,
            contracts   = shares,
            price       = strike,
            total_value = -cost,
            notes       = f"Assigned {shares} shares at ${strike:.2f}",
        )

        msg = f"ASSIGNED {shares} shares of {pos['ticker']} at ${strike:.2f}"
        log_event("broker", msg, "WARNING")
        return {"success": True, "stock_position_id": stock_pos_id, "shares": shares, "cost": cost}

    # ── Sell Call (covered call on assigned stock) ────────────────────────────

    def sell_call(self, stock_position_id: int, ticker: str, strike: float,
                  expiry: str, premium: float, contracts: int = 1,
                  underlying_price: float = None) -> dict:
        """Open a covered call against an assigned stock position."""
        credit = round(premium * contracts * CONTRACTS_MULTIPLIER, 2)

        portfolio = get_portfolio()
        new_cash  = round(portfolio["cash"] + credit, 2)
        update_portfolio(cash=new_cash)

        pos_id = create_position(
            ticker            = ticker,
            position_type     = "SELL_CALL",
            strike            = strike,
            expiry            = expiry,
            contracts         = contracts,
            underlying_price  = underlying_price,
            premium_collected = credit,
        )

        record_trade(
            position_id = pos_id,
            ticker      = ticker,
            action      = "SELL_CALL",
            strike      = strike,
            expiry      = expiry,
            contracts   = contracts,
            price       = premium,
            total_value = credit,
            notes       = f"Covered call against stock pos #{stock_position_id}",
        )

        msg = f"SELL CALL {ticker} ${strike:.0f} exp {expiry} | credit=${credit:.2f}"
        log_event("broker", msg, "INFO")
        return {"success": True, "position_id": pos_id, "credit": credit}

    # ── Close Call ────────────────────────────────────────────────────────────

    def close_call(self, position_id: int, current_premium: float,
                   reason: str = "MANUAL") -> dict:
        """Buy back a short call to close it."""
        from database.models import get_position
        pos = get_position(position_id)
        if not pos or pos["status"] != "OPEN":
            return {"success": False, "reason": "Position not found or closed"}

        contracts   = pos["contracts"]
        orig_credit = pos["premium_collected"]
        debit       = round(current_premium * contracts * CONTRACTS_MULTIPLIER, 2)
        pnl         = round(orig_credit - debit, 2)
        pnl_pct     = round(pnl / orig_credit, 4) if orig_credit else 0

        portfolio = get_portfolio()
        new_cash  = round(portfolio["cash"] - debit, 2)
        update_portfolio(cash=new_cash)

        close_position(position_id, pnl, pnl_pct, reason, current_premium)

        record_trade(
            position_id = position_id,
            ticker      = pos["ticker"],
            action      = "BUY_CALL",
            strike      = pos["strike"],
            expiry      = pos["expiry"],
            contracts   = contracts,
            price       = current_premium,
            total_value = -debit,
            notes       = f"Closed call: reason={reason}, P&L=${pnl:.2f}",
        )

        msg = (f"CLOSE CALL {pos['ticker']} ${pos['strike']:.0f} | "
               f"P&L=${pnl:.2f} ({pnl_pct*100:.1f}%) reason={reason}")
        log_event("broker", msg, "INFO")
        return {"success": True, "pnl": pnl, "pnl_pct": pnl_pct}
