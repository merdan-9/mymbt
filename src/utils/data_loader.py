import json
import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period='1mo'):
    """
    Fetch stock data from Yahoo Finance.
    
    Args:
        symbol (str): Stock symbol
        period (str): Display period (e.g., '1mo', '3mo', '6mo', '1y')
    
    Returns:
        pd.DataFrame: Stock data with enough history for indicators
    """
    try:
        ticker = yf.Ticker(symbol)
        # Always fetch 2 years of data to ensure enough history for indicators
        data = ticker.history(period='2y')
        
        # Return appropriate amount of data based on period
        if period == '1mo':
            return data.tail(80)  # 30 days display + 50 days for MA calculation
        elif period == '3mo':
            return data.tail(140)  # 90 days display + 50 days for MA calculation
        elif period == '6mo':
            return data.tail(230)  # 180 days display + 50 days for MA calculation
        else:  # 1y
            return data.tail(365)  # Full year
            
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
        filename (str): Path to the JSON file, relative to the data directory
        
    Returns:
        list: List of symbols from the file
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data.get('symbols', [])
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error reading {filename}")
        return [] 