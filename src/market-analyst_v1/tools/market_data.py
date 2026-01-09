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
        
        # Widen to +/- 15% to capture OTM strikes for credit spreads
        lower_bound = current_price * 0.85
        upper_bound = current_price * 1.15
        
        ntm_calls = calls[(calls['strike'] >= lower_bound) & (calls['strike'] <= upper_bound)]
        ntm_puts = puts[(puts['strike'] >= lower_bound) & (puts['strike'] <= upper_bound)]
        
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
        
        # Only calc SMA_200 if we actually have 200 points
        if len(hist) >= 200:
             hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        else:
             hist['SMA_200'] = pd.Series([None] * len(hist), index=hist.index)
        
        # RSI Calculation (14 periods) - needs at least 15 points
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
        rsi_signal = "Insufficient Data"
        if rsi_val is not None and not pd.isna(rsi_val):
            rsi_val = round(rsi_val, 2)
            if rsi_val > 70: rsi_signal = "Overbought"
            elif rsi_val < 30: rsi_signal = "Oversold"
            else: rsi_signal = "Neutral"
        else:
            rsi_val = "N/A"
        
        price = current_data['Close']
        trend = "Neutral"
        sma200 = current_data.get('SMA_200')
        
        if sma200 is not None and not pd.isna(sma200):
            if price > sma200:
                trend = "Bullish (Above SMA200)"
            else:
                trend = "Bearish (Below SMA200)"
        else:
             trend = "Unknown (No SMA200 Data)"
            
        return {
            "ticker": symbol,
            "current_price": round(price, 2),
            "sma_20": round(current_data['SMA_20'], 2) if not pd.isna(current_data.get('SMA_20')) else None,
            "sma_50": round(current_data['SMA_50'], 2) if not pd.isna(current_data.get('SMA_50')) else None,
            "sma_200": round(sma200, 2) if sma200 is not None and not pd.isna(sma200) else None,
            "rsi_14": rsi_val,
            "rsi_signal": rsi_signal,
            "trend_signal": trend
        }
        
    except Exception as e:
        return {"error": str(e)}
