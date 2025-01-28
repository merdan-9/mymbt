import ccxt
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import streamlit as st
import time

@st.cache_data(ttl=3600)  # Cache for 1 hour
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_crypto_data(symbol, days):
    """Fetch historical cryptocurrency data from Coinbase."""
    try:
        exchange = ccxt.coinbase({
            'enableRateLimit': True,  # Enable built-in rate limiter
            'timeout': 30000  # Increase timeout to 30 seconds
        })
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Fetch OHLCV data (Open, High, Low, Close, Volume)
        timeframe = '1d'
        since = int(start_time.timestamp() * 1000)
        
        # Add retry mechanism
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
                
                # Convert to DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                return df
            except ccxt.NetworkError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay * (attempt + 1))
            except ccxt.ExchangeError as e:
                print(f"Exchange error for {symbol}: {str(e)}")
                return pd.DataFrame()
                
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def get_top_performing_crypto(days=30):
    """Get the top performing cryptocurrencies in the given period."""
    symbols = load_crypto_symbols()
    performance = []
    
    for symbol in symbols[:10]:  # Limit to top 10 for performance
        try:
            df = fetch_crypto_data(symbol, days)
            if not df.empty:
                price_change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                performance.append({
                    'symbol': symbol,
                    'price_change': price_change,
                    'data': df
                })
            # Add small delay between requests
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue
    
    # Sort by price change
    performance.sort(key=lambda x: x['price_change'], reverse=True)
    return performance 