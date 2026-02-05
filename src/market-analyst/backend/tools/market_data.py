import yfinance as yf
import pandas as pd
import math
from datetime import datetime, timedelta

def normalize_period(period: str) -> str:
    """Standardizes period strings for yfinance."""
    p = period.lower().strip()
    if p in ["1yr", "1year"]: return "1y"
    if p in ["3mo", "3month"]: return "3mo"
    if p in ["1mo", "1month"]: return "1mo"
    if p in ["1wk", "1week"]: return "1wk"
    return p

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
        period = normalize_period(period)
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
            "vix_reference": round(vix_price, 2) if vix_price else "N/A",
            "volatility_regime": "HIGH_RISK_VOL" if (vix_price and vix_price > 30) else "ELEVATED_VOL" if (vix_price and vix_price > 20) else "LOW_VOL" if (vix_price and vix_price < 15) else "NORMAL_VOL"
        }
    except Exception as e:
        return {"error": str(e)}

def get_available_expirations(symbol: str) -> list:
    """Returns a list of available option expiration dates."""
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        return list(ticker.options)
    except Exception as e:
        return []

def get_option_chain_snapshot(symbol: str, target_date: str = None) -> str:
    """
    Fetches a snapshot of the option chain for a specific expiry.
    If target_date is None, picks the nearest liquid monthly expiry.
    """
    print(f"[DEBUG] get_option_chain_snapshot called for: {symbol} (Target: {target_date})")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
        
        if not expirations:
            return f"No options data found for {symbol}."
            
        if not target_date or target_date not in expirations:
            today = datetime.now()
            for exp in expirations:
                exp_date = datetime.strptime(exp, "%Y-%m-%d")
                days_to_exp = (exp_date - today).days
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
        
        # Filter around ATM for most relevant strikes
        ntm_calls = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:6]].sort_values('strike')
        ntm_puts = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:6]].sort_values('strike')
        
        summary = f"Option Chain Snapshot for {symbol} (Expiry: {target_date})\n"
        summary += f"Current Spot Price: {round(current_price, 2)}\n\n"
        
        summary += "--- CALLS (Strike | Last | Ask | IV | Vol) ---\n"
        for _, row in ntm_calls.iterrows():
            last = row.get('lastPrice', 0.0)
            ask = row.get('ask', 0.0)
            vol = row.get('volume', 0)
            iv = round(row['impliedVolatility']*100, 1) if not pd.isna(row.get('impliedVolatility')) else 0
            price_display = f"{ask}" if ask > 0 else f"{last} (Last)"
            summary += f"Strike: {row['strike']} | Price: {price_display} | IV: {iv}% | Vol: {vol}\n"
            
        summary += "\n--- PUTS (Strike | Last | Ask | IV | Vol) ---\n"
        for _, row in ntm_puts.iterrows():
            last = row.get('lastPrice', 0.0)
            ask = row.get('ask', 0.0)
            vol = row.get('volume', 0)
            iv = round(row['impliedVolatility']*100, 1) if not pd.isna(row.get('impliedVolatility')) else 0
            price_display = f"{ask}" if ask > 0 else f"{last} (Last)"
            summary += f"Strike: {row['strike']} | Price: {price_display} | IV: {iv}% | Vol: {vol}\n"
            
        return summary
        
    except Exception as e:
        return f"Error fetching option chain: {str(e)}"

def get_volatility_term_structure(symbol: str) -> str:
    """
    Analyzes IV across multiple expiries to identify Term Structure skew.
    """
    print(f"[DEBUG] get_volatility_term_structure called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        expirations = ticker.options[:4] # Check first 4 expiries
        
        if not expirations:
            return "No options data for volatility analysis."
            
        results = []
        for exp in expirations:
            opt = ticker.option_chain(exp)
            # Use mean IV of ATM calls
            calls = opt.calls
            price_info = get_current_price(symbol)
            if isinstance(price_info, str): continue
            current_price = float(price_info)
            atm_iv = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:2]]['impliedVolatility'].mean()
            results.append(f"- {exp}: {round(atm_iv * 100, 1)}% IV")
            
        summary = f"VOLATILITY TERM STRUCTURE for {symbol}:\n" + "\n".join(results)
        
        # Analyze skew
        if len(expirations) >= 2:
            try:
                iv1 = float(results[0].split(": ")[1].replace("% IV", ""))
                iv2 = float(results[1].split(": ")[1].replace("% IV", ""))
                if iv1 > iv2 + 5:
                    summary += f"\n\nSKEW ALERT: Front-month IV is significantly HIGHER ({iv1}% vs {iv2}%). Potential for Calendar Spreads (Sell Front, Buy Back)."
                elif iv1 < iv2 - 5:
                    summary += f"\n\nSKEW ALERT: Front-month IV is significantly LOWER ({iv1}% vs {iv2}%). Diagonal opportunities."
                else:
                    summary += f"\n\nTerm Structure is relatively flat."
            except: pass
            
        return summary
    except Exception as e:
        return f"Error analyzing term structure: {str(e)}"

def get_market_indices() -> str:
    """
    Fetches current market context using SPY (S&P 500) and ^VIX.
    Returns trend (Price vs SMA50) and Volatility regime.
    """
    try:
        tickers = yf.Tickers("SPY ^VIX")
        spy = tickers.tickers['SPY']
        vix = tickers.tickers['^VIX']
        
        # SPY Data
        spy_hist = spy.history(period="3mo")
        if spy_hist.empty: return "Market data unavailable."
        
        current_spy = spy_hist['Close'].iloc[-1]
        spy_sma50 = spy_hist['Close'].rolling(window=50).mean().iloc[-1]
        spy_trend = "BULLISH" if current_spy > spy_sma50 else "BEARISH"
        
        # VIX Data
        vix_hist = vix.history(period="1d")
        current_vix = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 0
        
        vix_regime = "LOW"
        if current_vix > 20: vix_regime = "ELEVATED"
        if current_vix > 30: vix_regime = "HIGH/FEAR"
        
        return f"MARKET CONTEXT:\n- SPY Trend: {spy_trend} (Price: {round(current_spy, 2)} vs SMA50: {round(spy_sma50, 2)})\n- VIX Level: {round(current_vix, 2)} ({vix_regime})"
        
    except Exception as e:
        return f"Error fetching market indices: {str(e)}"

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
        price = current_data['Close']
        rsi_val = current_data.get('RSI_14')
        macd_val = current_data.get('MACD')
        signal_val = current_data.get('Signal_Line')
        sma200 = current_data.get('SMA_200')
        if pd.isna(sma200): sma200 = None

        # Interpretation RSI
        # Deterministic Signals
        rsi_signal = "NEUTRAL"
        if rsi_val is not None and not pd.isna(rsi_val):
             if rsi_val > 70: rsi_signal = "OVERBOUGHT"
             elif rsi_val < 30: rsi_signal = "OVERSOLD"
        
        macd_signal = "NEUTRAL"
        if macd_val is not None and signal_val is not None and not pd.isna(macd_val) and not pd.isna(signal_val):
             if macd_val > signal_val: macd_signal = "BULLISH_CROSS"
             elif macd_val < signal_val: macd_signal = "BEARISH_CROSS"
             
        trend_signal = "NEUTRAL"
        sma50 = current_data.get('SMA_50')
        sma20 = current_data.get('SMA_20')
        
        # Check all components for trend signal
        if sma200 is not None and sma50 is not None and sma20 is not None and not pd.isna(sma50) and not pd.isna(sma20):
             if price > sma20 > sma50 > sma200: trend_signal = "STRONG_BULLISH"
             elif price < sma20 < sma50 < sma200: trend_signal = "STRONG_BEARISH"
             elif price > sma200: trend_signal = "BULLISH"
             elif price < sma200: trend_signal = "BEARISH"

        return {
            "ticker": symbol,
            "current_price": round(price, 2),
            "sma_20": round(current_data['SMA_20'], 2) if not pd.isna(current_data.get('SMA_20')) else "N/A",
            "ema_20": round(current_data['EMA_20'], 2) if not pd.isna(current_data.get('EMA_20')) else "N/A",
            "sma_50": round(current_data['SMA_50'], 2) if not pd.isna(current_data.get('SMA_50')) else "N/A",
            "sma_200": round(sma200, 2) if (sma200 is not None and not pd.isna(sma200)) else "N/A",
            "rsi_14": round(rsi_val, 2) if (rsi_val is not None and not pd.isna(rsi_val)) else "N/A",
            "macd": round(macd_val, 2) if (macd_val is not None and not pd.isna(macd_val)) else "N/A",
            "macd_signal": macd_signal,
            "rsi_signal": rsi_signal,
            "trend_signal": trend_signal
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
        
        eps_trailing = info.get('trailingEps')
        eps_forward = info.get('forwardEps')
        dividend_yield = info.get('dividendYield')

        # Ticker Calendar (Earnings)
        next_earnings = "N/A"
        try:
            cal = ticker.calendar
            if cal and 'Earnings Date' in cal:
                dates = cal['Earnings Date']
                if dates:
                    next_earnings = dates[0].strftime("%Y-%m-%d")
        except Exception:
            pass

        return {
            "ticker": symbol,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "peg_ratio": round(peg_ratio, 2) if peg_ratio else "N/A",
            "eps_trailing": round(eps_trailing, 2) if eps_trailing else "N/A",
            "eps_forward": round(eps_forward, 2) if eps_forward else "N/A",
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else "N/A",
            "net_profit_margin": f"{round(profit_margin * 100, 2)}%" if profit_margin else "N/A",
            "dividend_yield": f"{round(dividend_yield * 100, 2)}%" if dividend_yield else "N/A",
            "market_cap": info.get('marketCap', "N/A"),
            "sector": info.get('sector', "N/A"),
            "next_earnings_date": next_earnings,
            "valuation_score": "UNDERVALUED" if (pe_ratio and pe_ratio < 15) else "PREMIUM" if (pe_ratio and pe_ratio > 30) else "FAIR_VALUE",
            "quality_score": "HIGH_QUALITY" if (profit_margin and profit_margin > 0.20) else "LOW_MARGIN" if (profit_margin and profit_margin < 0.10) else "AVERAGE"
        }
    except Exception as e:
        return {"error": str(e)}

def get_analyst_consensus(symbol: str) -> dict:
    """
    Fetches Wall St. analyst recommendations and price targets.
    """
    print(f"[DEBUG] get_analyst_consensus called for: {symbol}")
    try:
        symbol = check_and_fix_ticker(symbol)
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        consensus = info.get('recommendationKey', 'none')
        target = info.get('targetMeanPrice')
        num_analysts = info.get('numberOfAnalystOpinions')
        
        # Current price for comparison
        current = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        
        upside = "N/A"
        if target and current and current > 0:
            upside_pct = ((target - current) / current) * 100
            upside = f"{round(upside_pct, 1)}%"
            
        return {
            "consensus": consensus.replace('_', ' ').title(),
            "target_price": target or "N/A",
            "current_price": current,
            "upside_potential": upside,
            "analyst_count": num_analysts or "N/A"
        }
    except Exception as e:
        return {"error": f"Failed to fetch analyst data: {str(e)}"}
