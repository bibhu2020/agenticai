
"""
MCP Trader Server using FastMCP
"""
import sys
import os

# Add src to pythonpath so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
from mcp_telemetry import log_usage

# Local imports (assuming src/mcp-trader is a package or run from src)
try:
    from .data.market_data import get_market_data, get_current_price
    from .data.fundamentals import get_fundamental_data
    from .strategies.momentum import analyze_momentum
    from .strategies.mean_reversion import analyze_mean_reversion
    from .strategies.value import analyze_value
    from .strategies.golden_cross import analyze_golden_cross
    from .strategies.macd_crossover import analyze_macd_crossover
    from .strategies.bollinger_squeeze import analyze_bollinger_squeeze
    from .indicators.technical import calculate_sma, calculate_rsi, calculate_macd
except ImportError:
    # Fallback if run directly and relative imports fail
    from data.market_data import get_market_data, get_current_price
    from data.fundamentals import get_fundamental_data
    from strategies.momentum import analyze_momentum
    from strategies.mean_reversion import analyze_mean_reversion
    from strategies.value import analyze_value
    from strategies.golden_cross import analyze_golden_cross
    from strategies.macd_crossover import analyze_macd_crossover
    from strategies.bollinger_squeeze import analyze_bollinger_squeeze
    from indicators.technical import calculate_sma, calculate_rsi, calculate_macd


# Initialize FastMCP Server
mcp = FastMCP("MCP Trader", host="0.0.0.0")

@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """Get the current price for a stock symbol."""
    log_usage("mcp-trader", "get_stock_price")
    return get_current_price(symbol)

@mcp.tool()
def get_stock_fundamentals(symbol: str) -> Dict[str, Any]:
    """Get fundamental data (PE, Market Cap, Sector) for a stock."""
    log_usage("mcp-trader", "get_stock_fundamentals")
    return get_fundamental_data(symbol)

@mcp.tool()
def get_momentum_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run Momentum Strategy analysis on a stock.
    Returns Buy/Sell/Hold recommendation based on RSI, MACD, and Price Trend.
    """
    log_usage("mcp-trader", "get_momentum_strategy")
    return analyze_momentum(symbol)

@mcp.tool()
def get_mean_reversion_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run Mean Reversion Strategy analysis on a stock.
    Returns Buy/Sell/Hold recommendation based on Bollinger Bands and RSI.
    """
    return analyze_mean_reversion(symbol)

@mcp.tool()
def get_value_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run Value Strategy analysis on a stock.
    Returns Buy/Sell/Hold recommendation based on fundamentals (PE, Dividend Yield).
    """
    return analyze_value(symbol)

@mcp.tool()
def get_golden_cross_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run Golden Cross Strategy (Trend Following).
    Detects SMA 50 crossing above/below SMA 200.
    """
    return analyze_golden_cross(symbol)

@mcp.tool()
def get_macd_crossover_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run MACD Crossover Strategy (Momentum).
    Detects MACD line crossing Signal line.
    """
    return analyze_macd_crossover(symbol)

@mcp.tool()
def get_bollinger_squeeze_strategy(symbol: str) -> Dict[str, Any]:
    """
    Run Bollinger Squeeze Strategy (Volatility).
    Detects low volatility periods followed by potential breakouts.
    """
    return analyze_bollinger_squeeze(symbol)

@mcp.tool()
def get_technical_summary(symbol: str) -> Dict[str, Any]:
    """
    Get a summary of technical indicators for a stock (RSI, MACD, SMA).
    """
    raw_data = get_market_data(symbol, period="3mo")
    if not raw_data:
        return {"error": "No data found"}
    
    import pandas as pd
    df = pd.DataFrame(raw_data)
    
    return {
        "symbol": symbol,
        "price": df['close'].iloc[-1],
        "rsi_14": calculate_rsi(df),
        "sma_20": calculate_sma(df, 20),
        "sma_50": calculate_sma(df, 50),
        "macd": calculate_macd(df)
    }

if __name__ == "__main__":
    # Run the MCP server
    import os
    if os.environ.get("MCP_TRANSPORT") == "sse":
        import uvicorn
        port = int(os.environ.get("PORT", 7860))
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=port)
    else:
        mcp.run()
