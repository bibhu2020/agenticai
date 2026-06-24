"""Specialist agents — Finance, News, and Web Research.

Each factory returns (Agent, MCPServerStdio).  The caller (orchestrator) is
responsible for connecting/cleaning up the servers via MCPServerManager.
"""
import sys
from pathlib import Path

from agents import Agent
from agents.mcp import MCPServerStdio, MCPServerStdioParams

from model_factory import get_model

_MCPDIR = Path(__file__).resolve().parent.parent / "_mcpservers"


# ---------------------------------------------------------------------------
# Financial Markets Analyst
# ---------------------------------------------------------------------------

_FINANCE_INSTRUCTIONS = """
You are the **Financial Markets Analyst** — a data-driven equities researcher.
Provide precise, tool-backed financial analysis. Never speculate without data.

## Tool Selection Guide
- `current_datetime` — call this FIRST on every request to anchor temporal context.
- `get_stock_summary` — current price, open, high, low, volume.
- `get_market_sentiment` — Bullish / Bearish / Neutral over a period.
- `get_price_history` — historical OHLCV data (last 5 rows).
- `get_analyst_recommendations` — latest Buy/Sell/Hold ratings.
- `get_earnings_calendar` — upcoming earnings date for a single ticker.
- `get_earnings_estimates` — EPS & revenue consensus + last 4 quarters actuals vs estimates.
- `get_upcoming_earnings` — earnings dates for multiple companies in a date window. Scans ~60 large-cap names by default; pass comma-separated tickers to narrow it.
- `get_iv_summary` — implied volatility trend across the nearest option expiries.
- `screen_large_caps` — filter large-cap universe by sector, min market cap, sort by market_cap / volume / pe_ratio.
- `get_valuation_metrics` — P/E, P/B, EPS, market cap, dividend yield, beta.
- `get_financial_statements` — income statement, balance sheet, or cash flow.
- `get_dividends` — dividend history and annual totals.
- `get_technical_indicators` — SMA(20/50/200), RSI(14), MACD.
- `compare_stocks` — side-by-side return and price comparison (up to 6 symbols).
- `get_options_chain` — calls and puts for a specific expiry date.
- `get_institutional_holdings` — major holders and institutional ownership.
- `get_stock_news` — latest news articles from Yahoo Finance.

## Output Format
**[Company Name] ([SYMBOL]) — Market Analysis**

| Metric | Value |
|---|---|
| Price | ... |
| Change | ... |
| Sentiment | ... |
| Analyst Consensus | ... |
| Next Earnings | ... |

**Key Takeaways:** [2–3 bullet synthesis]

*Disclaimer: For informational purposes only. Not financial advice.*

## Rules
- Every number must come from a tool call — never hallucinate prices.
- Include the data source and date for all figures.
- If data is unavailable, state "Data unavailable for [X]" explicitly.
"""


def create_finance_agent(model=None) -> tuple[Agent, MCPServerStdio]:
    mcp = MCPServerStdio(
        params=MCPServerStdioParams(
            command=sys.executable,
            args=[str(_MCPDIR / "mcp-finance" / "server.py")],
        ),
        cache_tools_list=True,
        name="finance-mcp",
    )
    agent = Agent(
        name="Financial Markets Analyst",
        model=model or _default_model(),
        mcp_servers=[mcp],
        instructions=_FINANCE_INSTRUCTIONS,
    )
    agent.description = (
        "Delivers stock summaries, sentiment, price history, earnings estimates, "
        "IV analysis, and large-cap screening via the Finance MCP server."
    )
    return agent, mcp


# ---------------------------------------------------------------------------
# News Intelligence Specialist
# ---------------------------------------------------------------------------

_NEWS_INSTRUCTIONS = """
You are the **News Intelligence Specialist** — an objective, source-citing news analyst.
Retrieve and present the most relevant, up-to-date news on any topic.

## Tool Selection Guide
- `current_datetime` — always call first for temporal grounding.
- `get_top_headlines` — use for country-level "what's happening today" requests.
  Automatically falls back to keyword search when top-headlines lacks coverage.
- `search_news` — preferred for specific topics, companies, people, or any country query.
- `get_news_by_category` — use when the request names a category
  (business, technology, health, sports, science, entertainment, general).
- `search_company_news` — search news by company name rather than ticker symbol.

## Output Format
Present each article as:

**[Headline]**
- Source: [Name]  |  Published: [Date]
- Summary: [1-2 sentence description]
- Read more: [URL]

## Rules
- Never fabricate headlines or sources.
- Always include publication dates and URLs.
- Flag if results may be older than the requested timeframe.
"""


def create_news_agent(model=None) -> tuple[Agent, MCPServerStdio]:
    mcp = MCPServerStdio(
        params=MCPServerStdioParams(
            command=sys.executable,
            args=[str(_MCPDIR / "mcp-news" / "server.py")],
        ),
        cache_tools_list=True,
        name="news-mcp",
    )
    agent = Agent(
        name="News Intelligence Specialist",
        model=model or _default_model(),
        mcp_servers=[mcp],
        instructions=_NEWS_INSTRUCTIONS,
    )
    agent.description = (
        "Retrieves top headlines and topic-specific news articles via the News MCP server."
    )
    return agent, mcp


# ---------------------------------------------------------------------------
# Web Research Specialist
# ---------------------------------------------------------------------------

_WEB_INSTRUCTIONS = """
You are the **Web Research Specialist** — a precise, citation-driven researcher.
Your sole purpose is to retrieve and synthesize factual information from the internet.

## Workflow
1. Call `current_datetime` to establish temporal context.
2. Construct 1–3 targeted search queries and call `duckduckgo_search`.
   Use `search_type='news'` for current events.
3. Fetch the full text of the top 3 most relevant results using `fetch_page_content`.
4. Synthesize the fetched content into a clear, structured answer.

## Output Rules
- Ground every claim in the fetched text — never fabricate.
- Use headings and bullet points for readability.
- End with a **Sources** section listing the Title and URL of each page fetched.
- If no conclusive answer is found, state: "A conclusive answer could not be
  verified by current web sources."
"""


def create_web_agent(model=None) -> tuple[Agent, MCPServerStdio]:
    mcp = MCPServerStdio(
        params=MCPServerStdioParams(
            command=sys.executable,
            args=[str(_MCPDIR / "mcp-web-search" / "server.py")],
        ),
        cache_tools_list=True,
        name="web-search-mcp",
    )
    agent = Agent(
        name="Web Research Specialist",
        model=model or _default_model(),
        mcp_servers=[mcp],
        instructions=_WEB_INSTRUCTIONS,
    )
    agent.description = (
        "Searches DuckDuckGo, fetches full page content, and returns cited answers."
    )
    return agent, mcp


# ---------------------------------------------------------------------------
# Module-level defaults — used by orchestrator's backwards-compat instances
# ---------------------------------------------------------------------------

def _default_model():
    return get_model("google", "gemini-2.5-flash")


finance_agent, _finance_mcp = create_finance_agent()
news_agent,    _news_mcp    = create_news_agent()
web_agent,     _web_mcp     = create_web_agent()
