import yfinance as yf
import pandas as pd
import math
from datetime import datetime, timedelta

def check_and_fix_ticker(symbol: str) -> str:
    """
    Checks if the ticker has data. If not, tries appending '.NS' (for NSE India).
    Returns the working ticker or the original if neither works.
    """
    print(f"[DEBUG] check_and_fix_ticker called using: {symbol}")
    symbol = symbol.upper().strip()
    
    # Try original
    ticker = yf.Ticker(symbol)
    try:
        # fast_info is quick way to check validity
        if ticker.fast_info.last_price is not None:
             return symbol
    except:
        pass
        
    # Try .NS
    ns_symbol = symbol + ".NS"
    ns_ticker = yf.Ticker(ns_symbol)
    try:
        if ns_ticker.fast_info.last_price is not None:
            return ns_symbol
    except:
        pass
        
    return symbol

def get_current_price(symbol: str) -> float:
    """Fetches the current market price of the stock."""
    print(f"[DEBUG] get_current_price called for: {symbol}")
    try:
        # Auto-fix ticker if needed
        symbol = check_and_fix_ticker(symbol)
        
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        if price is None:
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        
        if price is None:
             return f"Error: No price data for {symbol}"
             
        return price
    except Exception as e:
        return f"Error fetching price for {symbol}: {str(e)}"

def get_historical_volatility(symbol: str, period: str = "1mo") -> dict:
    """
    Calculates historical volatility and returns VIX context if available.
    """
    print(f"[DEBUG] get_historical_volatility called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return {"error": "No historical data found"}
        
        hist['Returns'] = hist['Close'].pct_change()
        volatility = hist['Returns'].std() * math.sqrt(252)
        
        vix_price = None
        try:
            vix = yf.Ticker("^VIX")
            vix_price = vix.fast_info.last_price
        except:
            pass

        return {
            "ticker_used": symbol,
            "annualized_volatility": round(volatility * 100, 2),
            "period": period,
            "vix_reference": round(vix_price, 2) if vix_price else "N/A"
        }
    except Exception as e:
        return {"error": str(e)}

def get_option_chain_snapshot(symbol: str) -> str:
    """
    Fetches a snapshot of the option chain.
    """
    print(f"[DEBUG] get_option_chain_snapshot called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        
        if not expirations:
            return f"No options data found for {symbol}."
            
        target_date = None
        today = datetime.now()
        
        for exp in expirations:
            exp_date = datetime.strptime(exp, "%Y-%m-%d")
            days_to_exp = (exp_date - today).days
            # Adjusted window: 7 to 45 days to capture monthly expiries for better liquidity
            if 7 <= days_to_exp <= 45:
                target_date = exp
                break
        
        if not target_date:
            target_date = expirations[0]
            
        opt = ticker.option_chain(target_date)
        calls = opt.calls
        puts = opt.puts
        
        price_info = get_current_price(symbol)
        if isinstance(price_info, str): return price_info
        current_price = float(price_info)
        
        # Filter around ATM for most relevant strikes (closest 6 calls/puts)
        ntm_calls = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:6]].sort_values('strike')
        ntm_puts = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:6]].sort_values('strike')
        
        summary = f"Option Chain Snapshot for {symbol} (Expiry: {target_date})\n"
        summary += f"Current Spot Price: {round(current_price, 2)}\n\n"
        
        summary += "--- CALLS (Ask | Strike | IV) ---\n"
        for _, row in ntm_calls.iterrows():
            summary += f"Strike: {row['strike']} | Ask: {row['ask']} | IV: {round(row['impliedVolatility']*100, 1)}%\n"
            
        summary += "\n--- PUTS (Ask | Strike | IV) ---\n"
        for _, row in ntm_puts.iterrows():
            summary += f"Strike: {row['strike']} | Ask: {row['ask']} | IV: {round(row['impliedVolatility']*100, 1)}%\n"
            
        return summary
        
    except Exception as e:
        return f"Error fetching option chain: {str(e)}"

def get_technical_indicators(symbol: str) -> dict:
    """
    Calculates key technical indicators: SMA (20, 50, 200) and RSI (14).
    Returns a dictionary of values and signals.
    """
    print(f"[DEBUG] get_technical_indicators called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        
        # Fetch enough history for SMA 200
        hist = ticker.history(period="1y") 
        if hist.empty:
             return {"error": "No historical data found"}
        
        # Safe calculations
        # SMA
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['EMA_20'] = hist['Close'].ewm(span=20, adjust=False).mean()
        
        # MACD (12, 26, 9)
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = exp1 - exp2
        hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        
        # Only calc SMA_200 if we actually have 200 points
        if len(hist) >= 200:
             hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        else:
             hist['SMA_200'] = pd.Series([None] * len(hist), index=hist.index)
        
        # RSI Calculation
        if len(hist) >= 15:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI_14'] = 100 - (100 / (1 + rs))
        else:
            hist['RSI_14'] = pd.Series([None] * len(hist), index=hist.index)
        
        current_data = hist.iloc[-1]
        
        # Interpretation RSI
        rsi_val = current_data.get('RSI_14')
        rsi_signal = "Neutral"
        if rsi_val is not None and not pd.isna(rsi_val):
            rsi_val = round(rsi_val, 2)
            if rsi_val > 70: rsi_signal = "Overbought"
            elif rsi_val < 30: rsi_signal = "Oversold"
        
        # Interpretation MACD
        macd_val = current_data.get('MACD')
        signal_val = current_data.get('Signal_Line')
        macd_signal = "Neutral"
        if macd_val is not None and signal_val is not None:
            if macd_val > signal_val: macd_signal = "Bullish Crossover"
            else: macd_signal = "Bearish Crossover"

        price = current_data['Close']
        trend = "Neutral"
        sma200 = current_data.get('SMA_200')
        
        if sma200 is not None and not pd.isna(sma200):
            if price > sma200: trend = "Bullish Long-term"
            else: trend = "Bearish Long-term"
            
        return {
            "ticker": symbol,
            "current_price": round(price, 2),
            "sma_20": round(current_data['SMA_20'], 2) if not pd.isna(current_data.get('SMA_20')) else "N/A",
            "ema_20": round(current_data['EMA_20'], 2) if not pd.isna(current_data.get('EMA_20')) else "N/A",
            "sma_50": round(current_data['SMA_50'], 2) if not pd.isna(current_data.get('SMA_50')) else "N/A",
            "sma_200": round(sma200, 2) if sma200 is not None and not pd.isna(sma200) else "N/A",
            "rsi_14": rsi_val or "N/A",
            "macd": round(macd_val, 2) if macd_val is not None else "N/A",
            "macd_signal": macd_signal,
            "rsi_signal": rsi_signal,
            "trend_signal": trend
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_fundamental_data(symbol: str) -> dict:
    """
    Fetches fundamental financial metrics: P/E, PEG, Debt/Equity, Debt/Asset, and Net Profit Margin.
    """
    print(f"[DEBUG] get_fundamental_data called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Use info.get to handle missing keys gracefully
        pe_ratio = info.get('forwardPE') or info.get('trailingPE')
        peg_ratio = info.get('pegRatio')
        debt_to_equity = info.get('debtToEquity')
        profit_margin = info.get('profitMargins')
        
        return {
            "ticker": symbol,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "peg_ratio": round(peg_ratio, 2) if peg_ratio else "N/A",
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else "N/A",
            "net_profit_margin": f"{round(profit_margin * 100, 2)}%" if profit_margin else "N/A",
            "market_cap": info.get('marketCap', "N/A"),
            "sector": info.get('sector', "N/A")
        }
    except Exception as e:
        return {"error": str(e)}
