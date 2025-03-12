#!/usr/bin/env python3
"""
Stock Filter Script
------------------
This script filters US stocks based on:
1. Current price within 3% of 90-day high
2. Market cap greater than $2 billion
3. Symbol length <= 4 characters

It uses the yfinance library to fetch stock data and outputs results as JSON.
"""

import yfinance as yf
import pandas as pd
import json
import requests
from io import StringIO
import time
from typing import List, Dict
import random
import logging

# Configure logging
logging.basicConfig(
    filename='stock_filter.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define filter criteria
PRICE_THRESHOLD = 0.03  # 3% threshold from 90-day high
MAX_RETRIES = 3  # Maximum number of retries for failed downloads
BATCH_SIZE = 10  # Reduced batch size to avoid rate limiting
MIN_DELAY = 2  # Minimum delay between batches in seconds
MAX_DELAY = 4  # Maximum delay between batches in seconds
MIN_PRICE = 5.0  # Minimum stock price
MAX_PRICE = 100.0  # Maximum stock price
MIN_MARKET_CAP = 2_000_000_000  # Minimum market cap of $2 billion
MAX_SYMBOL_LENGTH = 4  # Maximum length of stock symbol

def get_us_symbols():
    """Get all available US stock symbols."""
    print("Fetching US stock symbols...")
    
    # Download NASDAQ symbols
    nasdaq_url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt"
    # nyse_url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nyse/nyse_tickers.txt"
    
    try:
        # Fetch NASDAQ symbols
        nasdaq_response = requests.get(nasdaq_url)
        nasdaq_symbols = [line.strip() for line in StringIO(nasdaq_response.text) if line.strip()]
        
        # Fetch NYSE symbols
        # nyse_response = requests.get(nyse_url)
        # nyse_symbols = [line.strip() for line in StringIO(nyse_response.text) if line.strip()]
        nyse_symbols = []
        
        # Combine and remove duplicates while preserving order
        all_symbols = []
        seen = set()
        for symbol in nasdaq_symbols + nyse_symbols:
            if symbol not in seen:
                all_symbols.append(symbol)
                seen.add(symbol)
        
        print(f"Found {len(all_symbols)} unique US stock symbols")
        return all_symbols
        
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return []

def download_batch_with_retry(batch: List[str], retries: int = MAX_RETRIES) -> pd.DataFrame:
    """Download data for a batch of symbols with retry logic."""
    for attempt in range(retries):
        try:
            data = yf.download(batch, period="90d", group_by="ticker", progress=False)
            if not data.empty:
                return data
            
            if attempt < retries - 1:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                print(f"Attempt {attempt + 1} failed. Retrying after {delay:.1f} seconds...")
                time.sleep(delay)
            
        except Exception as e:
            if attempt < retries - 1:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                print(f"Error on attempt {attempt + 1}: {e}. Retrying after {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to download after {retries} attempts: {e}")
    
    return pd.DataFrame()

def process_symbol_data(symbol: str, data: pd.DataFrame, batch_size: int) -> Dict:
    """Process data for a single symbol and return results if it matches criteria."""
    try:
        # Skip if symbol is longer than MAX_SYMBOL_LENGTH
        if len(symbol) > MAX_SYMBOL_LENGTH:
            return None

        # Get the price data for the symbol
        if batch_size == 1:
            price_data = data['Close']
            high_data = data['High']
        else:
            price_data = data[symbol]['Close']
            high_data = data[symbol]['High']
        
        # Skip if we don't have enough data
        if len(price_data) == 0 or len(high_data) == 0:
            logging.warning(f"{symbol}: Insufficient data")
            return None
        
        # Get market cap data
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            # Skip if market cap is below minimum
            if market_cap < MIN_MARKET_CAP:
                return None
        except Exception as e:
            logging.warning(f"{symbol}: Could not fetch market cap data: {e}")
            return None
        
        current_price = price_data.iloc[-1]  # Using iloc instead of direct indexing
        high_90d = high_data.max()
        
        # Skip if price is not within desired range
        if current_price < MIN_PRICE or current_price > MAX_PRICE:
            return None
        
        # Calculate percentage difference from 90-day high
        price_diff_pct = (high_90d - current_price) / high_90d
        
        if price_diff_pct <= PRICE_THRESHOLD:
            result = {
                "symbol": symbol,
                "current_price": current_price,
                "90d_high": high_90d,
                "diff_percentage": price_diff_pct * 100,
                "market_cap": market_cap
            }
            logging.info(f"{symbol}: Current ${current_price:.2f} | 90d High ${high_90d:.2f} | Diff: {price_diff_pct*100:.2f}% | Market Cap: ${market_cap:,.0f}")
            return result
            
    except Exception as e:
        logging.error(f"Error processing {symbol}: {e}")
        return None

def filter_stocks(symbols):
    """Filter stocks based on proximity to 90-day high."""
    results = []
    total_batches = (len(symbols) - 1) // BATCH_SIZE + 1
    
    # Process symbols in smaller batches with delays
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        logging.info(f"Processing batch {i//BATCH_SIZE + 1}/{total_batches}")
        
        # Download data with retry logic
        data = download_batch_with_retry(batch)
        
        if data.empty:
            print(f"Skipping batch due to download failure")
            continue
        
        # Process each symbol in the batch
        for symbol in batch:
            result = process_symbol_data(symbol, data, len(batch))
            if result:
                results.append(result)
        
        # Add delay between batches to avoid rate limiting
        if i + BATCH_SIZE < len(symbols):
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"\nWaiting {delay:.1f} seconds before next batch...")
            time.sleep(delay)
    
    return results

def main():
    """Main function to run the script."""
    # Clean the log file at the start of each run
    try:
        open('stock_filter.log', 'w').close()
        logging.info("Starting new stock filtering run...")
    except Exception as e:
        print(f"Warning: Could not clean log file: {e}")
    
    # Get all US stock symbols
    symbols = get_us_symbols()
    
    if not symbols:
        print("Error: No symbols found!")
        return
    
    # Filter stocks
    filtered_stocks = filter_stocks(symbols)
    
    # Create and save JSON output
    if filtered_stocks:
        # Create JSON structure with more detailed information
        output_json = {
            "stocks": filtered_stocks,
            "filter_criteria": {
                "threshold_percentage": PRICE_THRESHOLD * 100
            }
        }
        
        # Save to JSON file
        output_file = "filtered_stocks.json"
        with open(output_file, 'w') as f:
            json.dump(output_json, f, indent=2)
        
        print("\n===== FILTERED STOCKS =====")
        print(f"Found {len(filtered_stocks)} stocks within {PRICE_THRESHOLD*100}% of their 90-day high:")
        print(json.dumps(output_json, indent=2))
        print(f"\nResults saved to {output_file}")
    else:
        print("\nNo stocks matched the filter criteria.")

if __name__ == "__main__":
    main()
