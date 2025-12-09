
import yfinance as yf

def get_earnings_calendar(symbol: str) -> str:
    print(f"[DEBUG] get_earnings_calendar called for symbol='{symbol}'")
    try:
        ticker = yf.Ticker(symbol)
        calendar = ticker.calendar
        
        print(f"DEBUG: Calendar raw output: {calendar}")
        
        if calendar is None:
             print("DEBUG: Calendar is None")
             return f"No earnings calendar found for {symbol}."
        
        # Check if empty (works for dict or dataframe)
        if hasattr(calendar, 'empty') and calendar.empty:
             print("DEBUG: Calendar is empty DataFrame")
             return f"No earnings calendar found for {symbol}."
        if not calendar:
             print("DEBUG: Calendar is empty (truthy check)")
             return f"No earnings calendar found for {symbol}."
            
        return f"Earnings Calendar for {symbol}:\n{calendar}"
    except Exception as e:
         print(f"DEBUG: Exception: {e}")
         return f"Error fetching earnings calendar for '{symbol}': {e}"

print("--- Testing get_earnings_calendar('NVDA') ---")
result = get_earnings_calendar("NVDA")
print("RESULT:", result)
