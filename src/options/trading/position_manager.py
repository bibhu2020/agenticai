"""
Position manager — checks all open positions and closes/manages them
according to profit/loss targets and expiry rules.
"""
import logging
from datetime import datetime, date

import config
from database.models import (
    get_open_positions, get_algo_params, update_portfolio,
    get_portfolio, log_event
)
from data.fetcher import get_current_price, get_options_chain
from .paper_broker import PaperBroker

logger = logging.getLogger(__name__)
broker = PaperBroker()


def _get_current_option_price(ticker: str, strike: float, expiry: str,
                               opt_type: str = "put") -> float:
    """Look up current mid price for a specific option contract."""
    try:
        from datetime import datetime
        today = date.today()
        exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        dte = (exp_date - today).days

        if dte < 0:
            return 0.0    # expired worthless

        chain = get_options_chain(ticker, min_dte=max(dte - 3, 0), max_dte=dte + 3)
        for opt in chain:
            if abs(opt["strike"] - strike) < 0.01:
                return opt["mid"]
    except Exception as e:
        logger.warning("Could not get option price for %s %.1f %s: %s", ticker, strike, expiry, e)
    return None


def _handle_sell_put_position(pos: dict, params: dict) -> str:
    """Check and manage a SELL_PUT position. Returns action taken."""
    position_id  = pos["id"]
    ticker       = pos["ticker"]
    strike       = pos["strike"]
    expiry       = pos["expiry"]
    orig_premium = pos["premium_collected"]
    contracts    = pos["contracts"]

    # Check expiry
    exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today    = date.today()
    dte      = (exp_date - today).days

    if dte < 0:
        # Already expired — check if ITM
        price = get_current_price(ticker)
        if price and price < strike:
            # ITM at expiry → assignment
            log_event("position_mgr", f"{ticker}: put EXPIRED ITM — assigning stock")
            broker.assign_stock(position_id)
            _handle_assignment(pos, price, params)
            return "ASSIGNED"
        else:
            # OTM at expiry → expires worthless, max profit
            result = broker.close_put(position_id, 0.0, reason="EXPIRY")
            log_event("position_mgr", f"{ticker}: put EXPIRED OTM — full profit ${orig_premium:.2f}")
            return "EXPIRED_OTM"

    # Get current option price
    current_price = _get_current_option_price(ticker, strike, expiry, "put")
    if current_price is None:
        return "NO_DATA"

    # P&L calculation
    pnl     = orig_premium - current_price * contracts * 100
    pnl_pct = pnl / orig_premium if orig_premium > 0 else 0

    profit_target = params.get("profit_target_pct", config.PROFIT_TARGET_PCT)
    stop_loss     = params.get("stop_loss_pct",     config.STOP_LOSS_PCT)

    if pnl_pct >= profit_target:
        result = broker.close_put(position_id, current_price, reason="PROFIT_TARGET")
        log_event("position_mgr",
                  f"{ticker}: PROFIT TARGET hit P&L=${pnl:.2f} ({pnl_pct*100:.1f}%)")
        return "PROFIT_TARGET"

    if pnl_pct <= -stop_loss:
        result = broker.close_put(position_id, current_price, reason="STOP_LOSS")
        log_event("position_mgr",
                  f"{ticker}: STOP LOSS hit P&L=${pnl:.2f} ({pnl_pct*100:.1f}%)")
        return "STOP_LOSS"

    # Update current premium in DB for dashboard display
    from database.models import update_position
    update_position(position_id, current_premium=current_price * contracts * 100)
    return "HOLDING"


def _handle_sell_call_position(pos: dict, params: dict) -> str:
    """Check and manage a SELL_CALL position."""
    position_id  = pos["id"]
    ticker       = pos["ticker"]
    strike       = pos["strike"]
    expiry       = pos["expiry"]
    orig_premium = pos["premium_collected"]
    contracts    = pos["contracts"]

    exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today    = date.today()
    dte      = (exp_date - today).days

    if dte < 0:
        # Expired worthless → full profit
        result = broker.close_call(position_id, 0.0, reason="EXPIRY")
        log_event("position_mgr", f"{ticker}: call EXPIRED OTM — full profit")
        return "EXPIRED_OTM"

    current_price = _get_current_option_price(ticker, strike, expiry, "call")
    if current_price is None:
        return "NO_DATA"

    pnl     = orig_premium - current_price * contracts * 100
    pnl_pct = pnl / orig_premium if orig_premium > 0 else 0

    profit_target = params.get("profit_target_pct", config.PROFIT_TARGET_PCT)
    stop_loss     = params.get("stop_loss_pct",     config.STOP_LOSS_PCT)

    if pnl_pct >= profit_target:
        broker.close_call(position_id, current_price, reason="PROFIT_TARGET")
        log_event("position_mgr", f"{ticker}: call PROFIT TARGET P&L=${pnl:.2f}")
        return "PROFIT_TARGET"

    if pnl_pct <= -stop_loss:
        broker.close_call(position_id, current_price, reason="STOP_LOSS")
        log_event("position_mgr", f"{ticker}: call STOP LOSS P&L=${pnl:.2f}")
        return "STOP_LOSS"

    from database.models import update_position
    update_position(position_id, current_premium=current_price * contracts * 100)
    return "HOLDING"


def _handle_long_stock_position(pos: dict, params: dict) -> str:
    """
    When we hold assigned stock, sell a covered call if not already done.
    """
    ticker      = pos["ticker"]
    strike_cost = pos["strike"]     # cost basis per share
    shares      = pos["contracts"]  # actual share count
    position_id = pos["id"]

    price = get_current_price(ticker)
    if not price:
        return "NO_DATA"

    # Check if we already have an open call on this ticker
    open_pos = get_open_positions()
    has_call = any(
        p["ticker"] == ticker and p["position_type"] == "SELL_CALL"
        for p in open_pos
    )

    if has_call:
        # Check stock P&L and whether to sell
        unrealised = (price - strike_cost) * shares
        unrealised_pct = (price - strike_cost) / strike_cost

        profit_target = params.get("profit_target_pct", config.PROFIT_TARGET_PCT)
        stop_loss     = params.get("stop_loss_pct",     config.STOP_LOSS_PCT)

        if unrealised_pct >= profit_target:
            _sell_stock(position_id, pos, price, "PROFIT_TARGET")
            return "STOCK_SOLD"
        if unrealised_pct <= -stop_loss * 2:   # wider stop for stock
            _sell_stock(position_id, pos, price, "STOP_LOSS")
            return "STOCK_SOLD"
        return "HOLDING_STOCK"

    # Sell a covered call at/above cost basis
    contracts = max(shares // 100, 1)
    chain = get_options_chain(ticker, min_dte=config.MIN_DTE, max_dte=config.MAX_DTE)
    if not chain:
        return "NO_OPTIONS"

    # Pick OTM call near cost basis or current price (whichever is higher)
    min_call_strike = max(strike_cost, price) * 1.02   # 2% OTM
    call_candidates = [
        o for o in chain
        if o.get("strike", 0) >= min_call_strike and o.get("mid", 0) > 0.05
    ]

    if not call_candidates:
        return "NO_CALL_CANDIDATES"

    best_call = call_candidates[0]
    broker.sell_call(
        stock_position_id = position_id,
        ticker            = ticker,
        strike            = best_call["strike"],
        expiry            = best_call["expiry"],
        premium           = best_call["mid"],
        contracts         = contracts,
        underlying_price  = price,
    )
    log_event("position_mgr",
              f"{ticker}: sold covered call ${best_call['strike']:.0f} exp {best_call['expiry']}")
    return "CALL_OPENED"


def _sell_stock(position_id: int, pos: dict, current_price: float, reason: str):
    """Close a long stock position."""
    shares    = pos["contracts"]
    cost      = pos["strike"]
    proceeds  = round(current_price * shares, 2)
    pnl       = round(proceeds - cost * shares, 2)
    pnl_pct   = round(pnl / (cost * shares), 4)

    from database.models import close_position, record_trade
    close_position(position_id, pnl, pnl_pct, reason, current_price)
    record_trade(
        position_id = position_id,
        ticker      = pos["ticker"],
        action      = "SELL_STOCK",
        strike      = current_price,
        expiry      = None,
        contracts   = shares,
        price       = current_price,
        total_value = proceeds,
        notes       = f"Sold {shares} shares at ${current_price:.2f}, P&L=${pnl:.2f}",
    )
    portfolio = get_portfolio()
    update_portfolio(cash=round(portfolio["cash"] + proceeds, 2))
    log_event("position_mgr",
              f"SOLD STOCK {pos['ticker']} {shares} shares P&L=${pnl:.2f} ({pnl_pct*100:.1f}%)")


def check_and_manage_positions() -> dict:
    """
    Main entry point — called every 30 min during market hours.
    Returns a summary of actions taken.
    """
    params  = get_algo_params()
    pos_list = get_open_positions()

    if not pos_list:
        log_event("position_mgr", "No open positions to manage")
        return {"checked": 0, "actions": []}

    actions = []
    for pos in pos_list:
        ptype  = pos["position_type"]
        ticker = pos["ticker"]

        try:
            if ptype == "SELL_PUT":
                action = _handle_sell_put_position(pos, params)
            elif ptype == "SELL_CALL":
                action = _handle_sell_call_position(pos, params)
            elif ptype == "LONG_STOCK":
                action = _handle_long_stock_position(pos, params)
            else:
                action = "UNKNOWN_TYPE"

            if action != "HOLDING":
                actions.append({"ticker": ticker, "type": ptype, "action": action})

        except Exception as e:
            logger.error("Error managing position %s %s: %s", ticker, ptype, e)
            log_event("position_mgr", f"Error managing {ticker}: {e}", "ERROR")

    # Recompute portfolio total value
    _update_portfolio_value()

    log_event("position_mgr",
              f"Position check done: {len(pos_list)} positions, {len(actions)} actions taken")
    return {"checked": len(pos_list), "actions": actions}


def _update_portfolio_value():
    """Recompute and store total portfolio value (cash + open position values)."""
    portfolio = get_portfolio()
    cash      = portfolio["cash"]
    open_pos  = get_open_positions()

    option_value = 0.0
    stock_value  = 0.0

    for pos in open_pos:
        if pos["position_type"] in ("SELL_PUT", "SELL_CALL"):
            # For short options, value is the net credit still on the table
            option_value += pos.get("current_premium", 0) or 0
        elif pos["position_type"] == "LONG_STOCK":
            price = get_current_price(pos["ticker"])
            if price:
                stock_value += price * pos["contracts"]

    total = round(cash + stock_value, 2)
    update_portfolio(total_value=total)
