
import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_sma(data: pd.DataFrame, window: int = 20) -> float:
    return data['close'].rolling(window=window).mean().iloc[-1]

def calculate_ema(data: pd.DataFrame, window: int = 20) -> float:
    return data['close'].ewm(span=window, adjust=False).mean().iloc[-1]

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> float:
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(data: pd.DataFrame) -> Dict[str, float]:
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    
    return {
        "macd": macd.iloc[-1],
        "signal": signal.iloc[-1],
        "histogram": macd.iloc[-1] - signal.iloc[-1]
    }

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
    sma = data['close'].rolling(window=window).mean()
    std = data['close'].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    
    return {
        "upper": upper_band.iloc[-1],
        "middle": sma.iloc[-1],
        "lower": lower_band.iloc[-1]
    }
