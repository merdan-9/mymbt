#!/usr/bin/env python3
"""
Stock Filter Script
------------------
This script filters stocks based on:
1. Price less than $100
2. Market cap less than $300 million

It uses the yfinance library to fetch stock data and outputs results as JSON.
"""

import yfinance as yf
import pandas as pd
import json
from pathlib import Path

# Define filter criteria
MAX_PRICE = 100  # USD
MAX_MARKET_CAP = 300_000_000_000  # $300 billion

def read_symbols(file_path):
    """Read stock symbols from a file."""
    with open(file_path, 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]
    
    # Remove duplicates while preserving order
    unique_symbols = []
    for symbol in symbols:
        if symbol not in unique_symbols:
            unique_symbols.append(symbol)
    
    return unique_symbols

def filter_stocks(symbols):
    """Filter stocks based on price and market cap criteria."""
    results = []
    
    # Process symbols in batches to avoid API limits
    batch_size = 20
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}...")
        
        # Get data for this batch
        data = yf.download(batch, period="1d", group_by="ticker", progress=False)
        
        # Process each symbol in the batch
        for symbol in batch:
            try:
                # Get ticker info
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Extract the closing price
                if len(batch) == 1:
                    closing_price = data['Close'][-1]
                else:
                    closing_price = data[symbol]['Close'][-1]
                
                # Get market cap
                market_cap = info.get('marketCap', float('inf'))
                
                if closing_price < MAX_PRICE and market_cap < MAX_MARKET_CAP:
                    results.append(symbol)
                    print(f"✅ {symbol}: ${closing_price:.2f} | Market Cap: ${market_cap/1_000_000:.2f}M")
                else:
                    print(f"❌ {symbol}: ${closing_price:.2f} | Market Cap: ${market_cap/1_000_000:.2f}M")
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
    
    return results

def main():
    """Main function to run the script."""
    # Path to symbols file
    symbols_file = Path("tests/symbols.txt")
    
    if not symbols_file.exists():
        print(f"Error: {symbols_file} not found!")
        return
    
    # Read symbols
    symbols = read_symbols(symbols_file)
    print(f"Found {len(symbols)} unique symbols to evaluate")
    
    # Filter stocks
    filtered_symbols = filter_stocks(symbols)
    
    # Create and save JSON output
    if filtered_symbols:
        # Create JSON structure
        output_json = {
            "symbols": filtered_symbols
        }
        
        # Save to JSON file
        output_file = "filtered_stocks.json"
        with open(output_file, 'w') as f:
            json.dump(output_json, f, indent=2)
        
        print("\n===== FILTERED STOCKS =====")
        print(f"Found {len(filtered_symbols)} stocks with price < ${MAX_PRICE} and market cap < ${MAX_MARKET_CAP/1_000_000}M:")
        print(json.dumps(output_json, indent=2))
        print(f"\nResults saved to {output_file}")
    else:
        print("\nNo stocks matched the filter criteria.")

if __name__ == "__main__":
    main() 