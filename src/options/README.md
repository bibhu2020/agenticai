---
title: Options Paper Trader
emoji: 📈
colorFrom: green
colorTo: gray
sdk: docker
app_port: 5050
pinned: false
license: mit
short_description: Automated options-selling paper tradedr
---

# Options Paper Trader

An automated paper-trading dashboard that scans a stock universe for cash-secured put opportunities, scores them on technical, fundamental, and sentiment signals, and manages positions against profit-target and stop-loss rules — all with real money never at risk.

## What it does

- **Scan** — screens a configurable stock universe for put-selling candidates within a target delta/DTE band
- **Score** — weighs technical, fundamental, and sentiment signals into a single composite score
- **Trade** — paper-executes the highest-scoring trades within position-size and portfolio limits
- **Manage** — closes positions automatically at profit target or stop loss, on a recurring schedule
- **Self-tune** — periodically re-evaluates its own scoring weights based on realized win rate and P&L
- **Dashboard** — live portfolio value, open positions, signals, and trade log over Flask + SocketIO

## Stack

Flask · Flask-SocketIO · APScheduler · yfinance · vaderSentiment · scikit-learn · Postgres (Neon)
