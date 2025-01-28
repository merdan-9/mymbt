import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import streamlit as st
import time
from src.utils.indicators import is_near_high

def load_crypto_symbols():
    """Load cryptocurrency symbols from crypto.json file."""
    try:
        with open('data/crypto/crypto.json', 'r') as f:
            data = json.load(f)
            return data.get('symbols', [])
    except FileNotFoundError:
        print("data/crypto/crypto.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error reading data/crypto/crypto.json file")
        return []

def get_crypto_data(symbol, period='1d'):
    """
    Fetch historical cryptocurrency data using yfinance.
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., 'BTC-USD')
        period (str): Time period ('1h', '1d', '5d', '1mo', '3mo', '6mo', '1y')
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Validate period and set appropriate interval
        valid_periods = ['5d', '1mo', '3mo', '6mo', '1y']
        if period not in valid_periods:
            period = '5d'  # Default to 5d if invalid period
        
        # Use 1-minute interval for 1h period, otherwise daily interval
        interval = '1m' if period == '1h' else '1d'
        
        # Fetch historical data
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            print(f"No data available for {symbol}")
            return pd.DataFrame()
            
        return df
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def clean_crypto_data(data):
    """Clean and prepare cryptocurrency data."""
    if data.empty:
        return data
    
    # Ensure all required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_columns):
        return pd.DataFrame()
    
    # Remove any rows with NaN values
    data = data.dropna()
    
    # Ensure the index is DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        if 'Date' in data.columns:
            data.set_index('Date', inplace=True)
        else:
            try:
                data.index = pd.to_datetime(data.index)
            except:
                return pd.DataFrame()
    
    return data

class CryptoService:
    def __init__(self):
        self.period_options = {
            "5d": "5 Days",
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year"
        }

    def get_crypto_info(self, symbol, period):
        """Get detailed information for a single cryptocurrency."""
        try:
            data = get_crypto_data(symbol, period=period)
            if data.empty:
                return None
                
            data = clean_crypto_data(data)
            if data.empty:
                return None
            
            _, diff_percent, period_high = is_near_high(data)
                
            return {
                'symbol': symbol,
                'data': data,
                'current_price': data['Close'].iloc[-1],
                'period_high': period_high,
                'period_low': data['Low'].min(),
                'average_volume': data['Volume'].mean(),
                'diff_percent': diff_percent
            }
        except Exception as e:
            print(f"Error getting crypto info for {symbol}: {str(e)}")
            return None

    def get_filtered_crypto(self, symbols, period, threshold, filter_type='high'):
        """
        Get cryptocurrencies filtered by near-high or near-low threshold.
        
        Args:
            symbols (list): List of cryptocurrency symbols
            period (str): Time period for data
            threshold (float): Threshold percentage for filtering
            filter_type (str): Type of filter ('high' or 'low')
        """
        filtered_results = []
        for symbol in symbols:
            try:
                data = get_crypto_data(symbol, period=period)
                if not data.empty:
                    data = clean_crypto_data(data)
                    if not data.empty:
                        current_price = data['Close'].iloc[-1]
                        if filter_type == 'high':
                            period_high = data['High'].max()
                            diff_percent = ((period_high - current_price) / period_high) * 100
                            is_near = diff_percent <= threshold
                        else:  # filter_type == 'low'
                            period_low = data['Low'].min()
                            diff_percent = ((current_price - period_low) / current_price) * 100
                            is_near = diff_percent <= threshold
                            
                        if is_near:
                            filtered_results.append({
                                'symbol': symbol,
                                'data': data,
                                'current_price': current_price,
                                'period_high': data['High'].max(),
                                'period_low': data['Low'].min(),
                                'average_volume': data['Volume'].mean(),
                                'diff_percent': diff_percent,
                                'filter_type': filter_type
                            })
            except Exception:
                continue
        return filtered_results

    def calculate_technical_indicators(self, data, rsi_period=14, ema_period=20):
        """Calculate technical indicators for cryptocurrency data."""
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate EMA
        ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
        
        return rsi.iloc[-1], ema.iloc[-1]

    def get_period_data(self, symbol, periods=None):
        """Get data across multiple time periods for a cryptocurrency."""
        if periods is None:
            periods = ['1mo', '3mo', '6mo', '1y']
            
        period_data = {}
        for period in periods:
            try:
                data = get_crypto_data(symbol, period=period)
                if not data.empty:
                    data = clean_crypto_data(data)
                    period_data[period] = {
                        'high': data['High'].max(),
                        'low': data['Low'].min()
                    }
            except Exception:
                period_data[period] = None
        return period_data 