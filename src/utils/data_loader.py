import json
import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period='1mo'):
    """
    Fetch stock data from Yahoo Finance.
    
    Args:
        symbol (str): Stock symbol
        period (str): Time period (e.g., '1mo', '3mo', '6mo', '1y')
    
    Returns:
        pd.DataFrame: Stock data
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception:
        return pd.DataFrame()

def clean_stock_data(data):
    """
    Clean and validate stock data.
    
    Args:
        data (pd.DataFrame): Raw stock data
    
    Returns:
        pd.DataFrame: Cleaned stock data
    """
    if data.empty:
        return data
        
    # Remove rows with missing values
    data = data.dropna()
    
    # Ensure required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_columns):
        return pd.DataFrame()
    
    return data

def load_json_file(filename):
    """
    Load symbols from a JSON file.
    
    Args:
        filename (str): Name of the JSON file
    
    Returns:
        list: List of stock symbols
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'symbols' in data:
                return data['symbols']
            return []
    except Exception:
        return [] 