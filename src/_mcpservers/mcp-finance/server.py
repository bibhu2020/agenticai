"""MCP Finance Server — comprehensive financial data and analysis via Yahoo Finance."""
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# Log to stderr — stdout is reserved for the stdio JSON-RPC channel
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] mcp-finance: %(message)s",
)
log = logging.getLogger("mcp-finance")

mcp = FastMCP("Finance MCP", host="0.0.0.0", port=8003)


# ---------------------------------------------------------------------------
# Predefined large-cap universe used by get_upcoming_earnings / screen
# ---------------------------------------------------------------------------
_LARGE_CAPS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "META", "AMZN", "TSLA", "AVGO", "ORCL",
    "ADBE", "CRM", "AMD", "INTC", "QCOM",
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "C", "AXP", "V", "MA",
    "JNJ", "LLY", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "AMGN",
    "XOM", "CVX", "COP", "SLB",
    "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST", "AMZN",
    "CAT", "BA", "GE", "HON", "RTX", "UPS", "DE",
    "T", "VZ", "DIS", "NFLX", "CMCSA",
    "SPY", "QQQ",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _date_range(period: str) -> tuple[str, str]:
    """Convert a period string (e.g. '1mo') into (start_date, end_date) strings."""
    end = datetime.today()
    if period.endswith("d"):
        days = int(period[:-1])
    elif period.endswith("mo"):
        days = int(period[:-2]) * 30
    elif period.endswith("y"):
        days = int(period[:-1]) * 365
    else:
        days = 30
    return (end - timedelta(days=days)).strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _history(symbol: str, period: str):
    """Fetch a Close-price history DataFrame for the given period."""
    ticker = yf.Ticker(symbol)
    start, end = _date_range(period)
    return ticker.history(start=start, end=end)


def _fmt_large(value) -> str:
    """Format large numbers as $1.23T / $456.78B / $789.01M."""
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    if value >= 1e6:
        return f"${value/1e6:.2f}M"
    return f"${value:,.0f}"


# ===========================================================================
# Existing tools
# ===========================================================================

@mcp.tool()
def get_stock_summary(symbol: str, period: str = "1d", interval: str = "1h") -> str:
    """
    Fetch the latest price summary for a stock or index.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'GOOG', 'BTC-USD').
        period: Lookback window — '1d', '5d', '1mo', '3mo' (default '1d').
        interval: Data granularity — '1m', '5m', '1h', '1d' (default '1h').
    """
    try:
        ticker = yf.Ticker(symbol)
        start, end = _date_range(period)
        data = ticker.history(start=start, end=end, interval=interval)
        if data.empty:
            return f"No data found for '{symbol}'."
        latest = data.iloc[-1]
        price = round(latest["Close"], 2)
        open_p = round(latest["Open"], 2)
        change = round(price - open_p, 2)
        pct = round((change / open_p) * 100, 2)
        info = ticker.info
        name = info.get("longName", symbol)
        currency = info.get("currency", "USD")
        return (
            f"📈 {name} ({symbol})\n"
            f"Price: {price} {currency}  |  Change: {change} ({pct}%)\n"
            f"Open: {open_p}  High: {round(latest['High'], 2)}  Low: {round(latest['Low'], 2)}\n"
            f"Volume: {int(latest['Volume'])}  |  Period: {period} @ {interval}"
        )
    except Exception as e:
        return f"Error fetching data for '{symbol}': {e}"


@mcp.tool()
def get_market_sentiment(symbol: str, period: str = "1mo") -> str:
    """
    Analyse price movement and return a Bullish / Bearish / Neutral verdict.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
        period: Lookback window — '7d', '1mo', '3mo' (default '1mo').
    """
    try:
        data = _history(symbol, period)
        if data.empty:
            return f"No data for '{symbol}'."
        pct = (data["Close"].iloc[-1] - data["Close"].iloc[0]) / data["Close"].iloc[0] * 100
        verdict = "Bullish" if pct > 2 else ("Bearish" if pct < -2 else "Neutral")
        return f"{symbol} sentiment over {period}: {verdict} ({pct:.2f}% change)"
    except Exception as e:
        return f"Error fetching sentiment for '{symbol}': {e}"


@mcp.tool()
def get_price_history(symbol: str, period: str = "1mo") -> str:
    """
    Fetch historical OHLCV price data for a ticker (last 5 rows).

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
        period: Lookback window — '1d', '5d', '1mo', '3mo', '1y' (default '1mo').
    """
    try:
        data = _history(symbol, period)
        if data.empty:
            return f"No historical data for '{symbol}'."
        return f"Price history for {symbol} ({period}):\n{data.tail(5).to_string()}"
    except Exception as e:
        return f"Error fetching history for '{symbol}': {e}"


@mcp.tool()
def get_analyst_recommendations(symbol: str) -> str:
    """
    Fetch the most recent analyst Buy/Sell/Hold ratings for a ticker.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
    """
    try:
        ticker = yf.Ticker(symbol)
        recs = ticker.recommendations
        if recs is None or recs.empty:
            return f"No analyst recommendations found for '{symbol}'."
        return f"Analyst recommendations for {symbol}:\n{recs.tail(5).to_string()}"
    except Exception as e:
        return f"Error fetching recommendations for '{symbol}': {e}"


@mcp.tool()
def get_earnings_calendar(symbol: str) -> str:
    """
    Fetch the upcoming earnings date for a ticker.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
    """
    try:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar
        if not calendar:
            return f"No earnings calendar found for '{symbol}'."
        return f"Earnings calendar for {symbol}:\n{calendar}"
    except Exception as e:
        return f"Error fetching earnings calendar for '{symbol}': {e}"


# ===========================================================================
# New tools
# ===========================================================================

@mcp.tool()
def get_valuation_metrics(symbol: str) -> str:
    """
    Fetch key valuation and fundamental metrics for a stock.

    Includes market cap, P/E ratios, EPS, revenue, profit margin,
    dividend yield, beta, and 52-week range.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'MSFT').
    """
    try:
        info = yf.Ticker(symbol).info
        name = info.get("longName", symbol)
        rows = [
            ("Market Cap",        _fmt_large(info.get("marketCap"))),
            ("Revenue (TTM)",     _fmt_large(info.get("totalRevenue"))),
            ("P/E Ratio (TTM)",   f"{info['trailingPE']:.2f}" if info.get("trailingPE") else "N/A"),
            ("Forward P/E",       f"{info['forwardPE']:.2f}" if info.get("forwardPE") else "N/A"),
            ("P/B Ratio",         f"{info['priceToBook']:.2f}" if info.get("priceToBook") else "N/A"),
            ("EPS (TTM)",         f"${info['trailingEps']:.2f}" if info.get("trailingEps") else "N/A"),
            ("Profit Margin",     f"{info['profitMargins']*100:.2f}%" if info.get("profitMargins") else "N/A"),
            ("Dividend Yield",    f"{info['dividendYield']*100:.2f}%" if info.get("dividendYield") else "N/A"),
            ("Beta",              f"{info['beta']:.2f}" if info.get("beta") else "N/A"),
            ("52-Week High",      f"${info['fiftyTwoWeekHigh']:.2f}" if info.get("fiftyTwoWeekHigh") else "N/A"),
            ("52-Week Low",       f"${info['fiftyTwoWeekLow']:.2f}" if info.get("fiftyTwoWeekLow") else "N/A"),
        ]
        lines = [f"📊 Valuation Metrics — {name} ({symbol})\n"]
        width = max(len(k) for k, _ in rows)
        for k, v in rows:
            lines.append(f"  {k:<{width}} : {v}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching valuation metrics for '{symbol}': {e}"


@mcp.tool()
def get_financial_statements(symbol: str, statement: str = "income") -> str:
    """
    Fetch annual financial statements for a stock.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
        statement: Which statement to return —
            'income'   → Income Statement (revenue, gross profit, net income, EBITDA)
            'balance'  → Balance Sheet (assets, liabilities, equity)
            'cashflow' → Cash Flow Statement (operating, investing, financing)
    """
    try:
        ticker = yf.Ticker(symbol)
        if statement == "income":
            df = ticker.income_stmt
            label = "Income Statement"
        elif statement == "balance":
            df = ticker.balance_sheet
            label = "Balance Sheet"
        elif statement == "cashflow":
            df = ticker.cashflow
            label = "Cash Flow Statement"
        else:
            return (
                f"Unknown statement type '{statement}'. "
                "Use 'income', 'balance', or 'cashflow'."
            )
        if df is None or df.empty:
            return f"No {label} data available for '{symbol}'."
        return f"📋 {label} — {symbol}\n\n{df.head(12).to_string()}"
    except Exception as e:
        return f"Error fetching {statement} statement for '{symbol}': {e}"


@mcp.tool()
def get_dividends(symbol: str, years: int = 3) -> str:
    """
    Fetch dividend payment history and yield for a stock.

    Args:
        symbol: Ticker symbol (e.g. 'JNJ', 'KO').
        years: How many years of history to show (default 3).
    """
    try:
        ticker = yf.Ticker(symbol)
        divs = ticker.dividends
        if divs is None or divs.empty:
            return f"'{symbol}' pays no dividends (or data is unavailable)."

        # Normalise timezone before date filtering
        idx = divs.index.tz_localize(None) if divs.index.tz is None else divs.index.tz_convert(None)
        cutoff = datetime.now() - timedelta(days=365 * years)
        recent = divs[idx >= cutoff]
        if recent.empty:
            return f"No dividends paid in the last {years} year(s) for '{symbol}'."

        annual = recent.resample("YE").sum()
        info = ticker.info
        yield_pct = info.get("dividendYield")

        lines = [f"💰 Dividend History — {symbol} (last {years} year(s))\n"]
        if yield_pct:
            lines.append(f"  Current Yield  : {yield_pct * 100:.2f}%")
        lines.append("  Annual totals  :")
        for date, amount in annual.items():
            lines.append(f"    {date.year} : ${amount:.4f}")
        lines.append(
            f"\n  Last payment   : ${recent.iloc[-1]:.4f} "
            f"on {idx[-1].strftime('%Y-%m-%d')}"
        )
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching dividends for '{symbol}': {e}"


@mcp.tool()
def get_technical_indicators(symbol: str, period: str = "6mo") -> str:
    """
    Compute SMA(20/50/200), RSI(14), and MACD(12,26,9) from price history.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL').
        period: Lookback window for calculations — '3mo', '6mo', '1y', '2y'
                (default '6mo'; use '2y' to get SMA-200).
    """
    try:
        data = _history(symbol, period)
        if data.empty or len(data) < 20:
            return (
                f"Insufficient price history for '{symbol}'. "
                "Try a longer period (e.g. '1y')."
            )
        close = data["Close"]
        price = round(close.iloc[-1], 2)

        def _sma(n):
            return round(close.rolling(n).mean().iloc[-1], 2) if len(close) >= n else None

        sma20, sma50, sma200 = _sma(20), _sma(50), _sma(200)

        # RSI-14
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = round((100 - 100 / (1 + rs)).iloc[-1], 2)
        rsi_label = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")

        # MACD (12, 26, 9)
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        macd_label = "Bullish" if hist.iloc[-1] > 0 else "Bearish"

        def _sma_line(n, val):
            if val is None:
                return f"  SMA({n:3d})   : N/A (need more history)"
            arrow = "↑" if price > val else "↓"
            return f"  SMA({n:3d})   : ${val}  {arrow}"

        lines = [
            f"📉 Technical Indicators — {symbol}  (period: {period})\n",
            f"  Price      : ${price}",
            _sma_line(20, sma20),
            _sma_line(50, sma50),
            _sma_line(200, sma200),
            f"  RSI(14)    : {rsi}  →  {rsi_label}",
            f"  MACD line  : {round(macd.iloc[-1], 4)}",
            f"  Signal     : {round(signal.iloc[-1], 4)}",
            f"  Histogram  : {round(hist.iloc[-1], 4)}  →  {macd_label} momentum",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error computing technical indicators for '{symbol}': {e}"


@mcp.tool()
def compare_stocks(symbols: str, period: str = "1y") -> str:
    """
    Compare the price performance of multiple stocks side-by-side.

    Args:
        symbols: Comma-separated ticker symbols, e.g. 'AAPL,MSFT,GOOG' (max 6).
        period: Comparison window — '1mo', '3mo', '6mo', '1y', '3y' (default '1y').
    """
    try:
        tickers = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not tickers:
            return "No valid ticker symbols provided."
        if len(tickers) > 6:
            return "Maximum 6 tickers supported for a single comparison."

        rows = []
        for sym in tickers:
            try:
                data = _history(sym, period)
                if data.empty:
                    rows.append((sym, None, None, None, None))
                    continue
                close = data["Close"]
                ret = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
                rows.append((sym, ret, close.iloc[-1], close.max(), close.min()))
            except Exception:
                rows.append((sym, None, None, None, None))

        lines = [
            f"📊 Stock Comparison — {period}\n",
            f"  {'Symbol':<8}  {'Return':>8}   {'Price':>9}   {'52W High':>10}   {'52W Low':>9}",
            f"  {'-'*57}",
        ]
        for sym, ret, price, high, low in rows:
            if ret is None:
                lines.append(f"  {sym:<8}  {'N/A':>8}   {'N/A':>9}   {'N/A':>10}   {'N/A':>9}")
            else:
                lines.append(
                    f"  {sym:<8}  {ret:>+7.2f}%   ${price:>8.2f}   ${high:>9.2f}   ${low:>8.2f}"
                )
        return "\n".join(lines)
    except Exception as e:
        return f"Error comparing stocks: {e}"


@mcp.tool()
def get_options_chain(symbol: str, expiry_index: int = 0) -> str:
    """
    Fetch the top calls and puts for a given options expiry date.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'SPY').
        expiry_index: Which expiry to use — 0 = nearest, 1 = next, etc. (default 0).
    """
    try:
        ticker = yf.Ticker(symbol)
        expiry_dates = ticker.options
        if not expiry_dates:
            return f"No options data available for '{symbol}'."

        idx = min(expiry_index, len(expiry_dates) - 1)
        expiry = expiry_dates[idx]
        chain = ticker.option_chain(expiry)

        def _fmt_contracts(df, kind):
            top = df.sort_values("openInterest", ascending=False).head(5)
            lines = [f"\n{'📗' if kind == 'Calls' else '📕'} Top {kind} (by open interest):"]
            for _, row in top.iterrows():
                iv = row.get("impliedVolatility", 0) * 100
                oi = int(row.get("openInterest", 0))
                lines.append(
                    f"  Strike ${row['strike']:.2f}  |  "
                    f"Last ${row['lastPrice']:.2f}  |  "
                    f"IV {iv:.1f}%  |  OI {oi:,}"
                )
            return "\n".join(lines)

        header = (
            f"⚙️  Options Chain — {symbol}  |  Expiry: {expiry}\n"
            f"All expiries: {', '.join(expiry_dates[:6])}"
            f"{'…' if len(expiry_dates) > 6 else ''}"
        )
        return header + _fmt_contracts(chain.calls, "Calls") + _fmt_contracts(chain.puts, "Puts")
    except Exception as e:
        return f"Error fetching options chain for '{symbol}': {e}"


@mcp.tool()
def get_institutional_holdings(symbol: str) -> str:
    """
    Fetch the top institutional holders and ownership breakdown for a stock.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'TSLA').
    """
    try:
        ticker = yf.Ticker(symbol)
        major = ticker.major_holders
        inst = ticker.institutional_holders

        lines = [f"🏦 Institutional Holdings — {symbol}\n"]

        if major is not None and not major.empty:
            lines.append("  Ownership breakdown:")
            for _, row in major.iterrows():
                lines.append(f"    {row.iloc[1]}: {row.iloc[0]}")
            lines.append("")

        if inst is not None and not inst.empty:
            lines.append("  Top institutional holders:")
            for _, row in inst.head(8).iterrows():
                name = row.get("Holder", str(row.iloc[0]))
                pct = row.get("pctHeld") or row.get("% Out")
                shares = row.get("Shares")
                pct_str = f"  ({pct*100:.2f}%)" if pct else ""
                shares_str = f"  {int(shares):,} shares" if shares else ""
                lines.append(f"    {name}{pct_str}{shares_str}")
        else:
            lines.append("  No institutional holder data available.")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching institutional holdings for '{symbol}': {e}"


@mcp.tool()
def get_stock_news(symbol: str, max_results: int = 5) -> str:
    """
    Fetch recent news articles about a specific stock from Yahoo Finance.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'TSLA').
        max_results: Number of articles to return, 1–10 (default 5).
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if not news:
            return f"No recent news found for '{symbol}'."
        lines = [f"📰 Recent News — {symbol}\n"]
        for item in news[:min(max_results, 10)]:
            pub_ts = item.get("providerPublishTime", 0)
            pub_date = (
                datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M")
                if pub_ts else "N/A"
            )
            lines.append(
                f"  📌 {item.get('title', 'No title')}\n"
                f"     {item.get('publisher', 'Unknown')}  |  {pub_date}\n"
                f"     {item.get('link', '')}\n"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching news for '{symbol}': {e}"


@mcp.tool()
def current_datetime(format: str = "natural") -> str:
    """
    Return the current date and time.  Call this first to anchor temporal context.

    Args:
        format: 'natural' → 'Saturday, June 07, 2025 at 3:59 PM'
                'natural_short' → 'Jun 07, 2025 at 3:59 PM'
                Or any strftime format string (e.g. '%Y-%m-%d').
    """
    now = datetime.now()
    if format == "natural":
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    if format == "natural_short":
        return now.strftime("%b %d, %Y at %I:%M %p")
    return now.strftime(format)


@mcp.tool()
def get_earnings_estimates(symbol: str) -> str:
    """
    Get EPS and revenue consensus estimates plus recent historical actuals for a stock.

    Returns forward EPS estimate, revenue estimate (low/avg/high), trailing EPS,
    and the last four quarters of reported EPS vs estimate with surprise %.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'MSFT').
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        name = info.get("longName", symbol)

        lines = [f"📊 Earnings Estimates — {name} ({symbol})\n"]

        # Near-term consensus from calendar
        try:
            cal = ticker.calendar or {}
            if cal:
                lines.append("  ── Next Earnings ──")
                earn_date = cal.get("Earnings Date")
                if earn_date:
                    dates = earn_date if isinstance(earn_date, list) else [earn_date]
                    lines.append(f"  Date              : {', '.join(str(d)[:10] for d in dates)}")
                for key, label in [
                    ("Earnings Average",  "EPS Estimate (avg)"),
                    ("Earnings Low",      "EPS Estimate (low)"),
                    ("Earnings High",     "EPS Estimate (high)"),
                    ("Revenue Average",   "Revenue Estimate"),
                    ("Revenue Low",       "Revenue Low"),
                    ("Revenue High",      "Revenue High"),
                ]:
                    val = cal.get(key)
                    if val is not None:
                        if "Revenue" in key:
                            lines.append(f"  {label:<20}: {_fmt_large(val)}")
                        else:
                            lines.append(f"  {label:<20}: ${val:.2f}")
        except Exception as e:
            log.warning("calendar fetch failed for %s: %s", symbol, e)

        # Forward EPS / PE from info
        lines.append("\n  ── Analyst Consensus ──")
        for key, label in [
            ("forwardEps",    "Forward EPS"),
            ("trailingEps",   "Trailing EPS (TTM)"),
            ("forwardPE",     "Forward P/E"),
            ("trailingPE",    "Trailing P/E"),
        ]:
            val = info.get(key)
            lines.append(f"  {label:<22}: {'N/A' if val is None else f'${val:.2f}' if 'EPS' in label else f'{val:.2f}'}")

        # Historical quarterly actuals from earnings_dates
        try:
            edates = ticker.earnings_dates
            if edates is not None and not edates.empty:
                past = edates[edates.index < datetime.now().strftime("%Y-%m-%d")].head(4)
                if not past.empty:
                    lines.append("\n  ── Recent Quarterly Actuals ──")
                    for dt, row in past.iterrows():
                        est = row.get("EPS Estimate")
                        rep = row.get("Reported EPS")
                        sur = row.get("Surprise(%)")
                        est_s = f"${est:.2f}" if est is not None and est == est else "N/A"
                        rep_s = f"${rep:.2f}" if rep is not None and rep == rep else "N/A"
                        sur_s = f"{sur:.1f}%" if sur is not None and sur == sur else "N/A"
                        lines.append(
                            f"  {str(dt)[:10]}  Est {est_s:<8} Actual {rep_s:<8} Surprise {sur_s}"
                        )
        except Exception as e:
            log.warning("earnings_dates fetch failed for %s: %s", symbol, e)

        return "\n".join(lines)
    except Exception as e:
        log.error("get_earnings_estimates failed for %s: %s", symbol, e)
        return f"Error fetching earnings estimates for '{symbol}': {e}"


@mcp.tool()
def get_upcoming_earnings(tickers: str = "", days_ahead: int = 14) -> str:
    """
    List upcoming earnings dates for multiple companies within a date window.

    If no tickers are provided, scans the built-in large-cap universe (~60 names
    covering tech, finance, healthcare, energy, consumer, and industrial sectors).

    Args:
        tickers: Comma-separated symbols, e.g. 'AAPL,MSFT,GOOG'. Leave blank to
                 scan the default large-cap list.
        days_ahead: How many calendar days ahead to look (default 14).
    """
    try:
        symbols = (
            [s.strip().upper() for s in tickers.split(",") if s.strip()]
            if tickers.strip()
            else _LARGE_CAPS
        )
        today = datetime.today().date()
        cutoff = today + timedelta(days=days_ahead)

        hits: list[tuple] = []
        for sym in symbols:
            try:
                cal = yf.Ticker(sym).calendar or {}
                earn_date = cal.get("Earnings Date")
                if not earn_date:
                    continue
                dates = earn_date if isinstance(earn_date, list) else [earn_date]
                for d in dates:
                    d_date = d.date() if hasattr(d, "date") else d
                    if today <= d_date <= cutoff:
                        eps_est = cal.get("Earnings Average")
                        rev_est = cal.get("Revenue Average")
                        hits.append((d_date, sym, eps_est, rev_est))
                        break
            except Exception as e:
                log.debug("skip %s in upcoming_earnings: %s", sym, e)

        if not hits:
            return f"No earnings found in the next {days_ahead} days for the scanned tickers."

        hits.sort()
        lines = [f"📅 Upcoming Earnings — next {days_ahead} days\n"]
        lines.append(f"  {'Date':<12} {'Symbol':<8} {'EPS Est':>9} {'Rev Est':>12}")
        lines.append(f"  {'-'*45}")
        for d, sym, eps, rev in hits:
            eps_s = f"${eps:.2f}" if eps is not None else "N/A"
            rev_s = _fmt_large(rev) if rev is not None else "N/A"
            lines.append(f"  {str(d):<12} {sym:<8} {eps_s:>9} {rev_s:>12}")
        return "\n".join(lines)
    except Exception as e:
        log.error("get_upcoming_earnings failed: %s", e)
        return f"Error fetching upcoming earnings: {e}"


@mcp.tool()
def get_iv_summary(symbol: str) -> str:
    """
    Summarise implied volatility (IV) across the nearest option expiry dates.

    Shows average IV for calls and puts per expiry, plus a trend direction
    (rising / falling / flat) — useful for gauging market uncertainty ahead
    of earnings or macro events.

    Args:
        symbol: Ticker symbol (e.g. 'AAPL', 'SPY').
    """
    try:
        ticker = yf.Ticker(symbol)
        expiries = ticker.options
        if not expiries:
            return f"No options data available for '{symbol}'."

        lines = [f"📊 Implied Volatility Summary — {symbol}\n"]
        lines.append(f"  {'Expiry':<14} {'Avg Call IV':>12} {'Avg Put IV':>12}")
        lines.append(f"  {'-'*40}")

        iv_series: list[float] = []
        for exp in expiries[:6]:
            try:
                chain = ticker.option_chain(exp)
                call_iv = chain.calls["impliedVolatility"].dropna().mean()
                put_iv = chain.puts["impliedVolatility"].dropna().mean()
                iv_series.append((call_iv + put_iv) / 2)
                lines.append(
                    f"  {exp:<14} {call_iv*100:>11.1f}% {put_iv*100:>11.1f}%"
                )
            except Exception as e:
                log.debug("IV fetch failed for %s expiry %s: %s", symbol, exp, e)
                lines.append(f"  {exp:<14} {'N/A':>12} {'N/A':>12}")

        if len(iv_series) >= 2:
            trend = (
                "📈 Rising IV (increasing uncertainty)"
                if iv_series[-1] > iv_series[0] * 1.05
                else "📉 Falling IV (uncertainty decreasing)"
                if iv_series[-1] < iv_series[0] * 0.95
                else "➡️  Flat IV"
            )
            lines.append(f"\n  Trend: {trend}")

        return "\n".join(lines)
    except Exception as e:
        log.error("get_iv_summary failed for %s: %s", symbol, e)
        return f"Error fetching IV summary for '{symbol}': {e}"


@mcp.tool()
def screen_large_caps(
    sector: str = "",
    min_market_cap_b: float = 10.0,
    sort_by: str = "market_cap",
    top_n: int = 10,
) -> str:
    """
    Screen the large-cap universe for stocks meeting basic criteria.

    Useful for finding sector leaders, high-volume names, or high-market-cap
    stocks ahead of earnings season.

    Args:
        sector: Filter by sector keyword, e.g. 'Technology', 'Healthcare',
                'Financial', 'Energy', 'Consumer'. Leave blank for all sectors.
        min_market_cap_b: Minimum market cap in billions (default 10).
        sort_by: Rank by 'market_cap', 'volume', or 'pe_ratio' (default 'market_cap').
        top_n: Number of results to return (default 10, max 20).
    """
    try:
        rows: list[dict] = []
        for sym in _LARGE_CAPS:
            try:
                info = yf.Ticker(sym).info
                mcap = info.get("marketCap") or 0
                if mcap < min_market_cap_b * 1e9:
                    continue
                sym_sector = info.get("sector", "")
                if sector and sector.lower() not in sym_sector.lower():
                    continue
                rows.append({
                    "symbol":     sym,
                    "name":       info.get("shortName", sym)[:22],
                    "sector":     sym_sector[:18],
                    "market_cap": mcap,
                    "volume":     info.get("averageVolume") or 0,
                    "pe_ratio":   info.get("trailingPE") or 0,
                })
            except Exception as e:
                log.debug("screen skip %s: %s", sym, e)

        if not rows:
            return "No stocks matched the given criteria."

        sort_key = {"market_cap": "market_cap", "volume": "volume", "pe_ratio": "pe_ratio"}.get(
            sort_by, "market_cap"
        )
        rows.sort(key=lambda r: r[sort_key], reverse=True)
        rows = rows[: min(top_n, 20)]

        lines = [
            f"🔍 Large-Cap Screen — sector='{sector or 'All'}' "
            f"min_cap=${min_market_cap_b:.0f}B sort={sort_by}\n"
        ]
        lines.append(
            f"  {'Symbol':<7} {'Name':<24} {'Sector':<20} {'Mkt Cap':>9} {'Avg Vol':>10} {'P/E':>6}"
        )
        lines.append(f"  {'-'*78}")
        for r in rows:
            lines.append(
                f"  {r['symbol']:<7} {r['name']:<24} {r['sector']:<20} "
                f"{_fmt_large(r['market_cap']):>9} {r['volume']:>10,} "
                f"{r['pe_ratio']:>6.1f}" if r["pe_ratio"] else
                f"  {r['symbol']:<7} {r['name']:<24} {r['sector']:<20} "
                f"{_fmt_large(r['market_cap']):>9} {r['volume']:>10,} {'N/A':>6}"
            )
        return "\n".join(lines)
    except Exception as e:
        log.error("screen_large_caps failed: %s", e)
        return f"Error running large-cap screen: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
