import ccxt
import pandas as pd
from datetime import datetime, timedelta
import json
import os

def load_crypto_symbols():
    """Load cryptocurrency symbols from crypto.json file."""
    try:
        with open('crypto.json', 'r') as f:
            data = json.load(f)
            return data.get('symbols', [])
    except FileNotFoundError:
        print("crypto.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error reading crypto.json file")
        return []

def fetch_crypto_data(symbol, days):
    """Fetch historical cryptocurrency data from Coinbase."""
    exchange = ccxt.coinbase()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Fetch OHLCV data (Open, High, Low, Close, Volume)
    timeframe = '1d'
    since = int(start_time.timestamp() * 1000)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
    
    # Convert to DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    return df

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
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    
    # Sort by price change
    performance.sort(key=lambda x: x['price_change'], reverse=True)
    return performance 