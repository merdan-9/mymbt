import pandas as pd

def calculate_rsi(data, periods=14):
    """Calculate RSI indicator"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_ema(data, span=20):
    """Calculate EMA indicator"""
    return data['Close'].ewm(span=span, adjust=False).mean()

def is_near_high(data, threshold_percent=1.0):
    """
    Check if the current price is near the period high.
    
    Args:
        data (pd.DataFrame): Stock data
        threshold_percent (float): Threshold percentage
    
    Returns:
        tuple: (is_near, diff_percent, period_high)
    """
    if data.empty:
        return False, 0, 0
        
    current_price = data['Close'].iloc[-1]
    period_high = data['High'].max()
    
    diff_percent = abs((period_high - current_price) / period_high) * 100
    is_near = diff_percent <= threshold_percent
    
    return is_near, diff_percent, period_high 