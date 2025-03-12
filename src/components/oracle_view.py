import streamlit as st
import pandas as pd
import logging
from datetime import datetime
import yfinance as yf
import json
import requests
from io import StringIO
import time
from typing import List, Dict
import random
from src.services.stock_service import StockService

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

class OracleView:
    """Component for displaying stock oracle results."""
    
    def __init__(self):
        """Initialize the oracle view."""
        self.stock_service = StockService()
        
        # Configure logging
        logging.basicConfig(
            filename='stock_filter.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_us_symbols(self):
        """Get all available US stock symbols."""
        st.write("Fetching US stock symbols...")
        
        # Download NASDAQ symbols
        nasdaq_url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt"
        
        try:
            # Fetch NASDAQ symbols
            nasdaq_response = requests.get(nasdaq_url)
            nasdaq_symbols = [line.strip() for line in StringIO(nasdaq_response.text) if line.strip()]
            
            # Combine and remove duplicates while preserving order
            all_symbols = []
            seen = set()
            for symbol in nasdaq_symbols:
                if symbol not in seen:
                    all_symbols.append(symbol)
                    seen.add(symbol)
            
            st.write(f"Found {len(all_symbols)} unique US stock symbols")
            return all_symbols
            
        except Exception as e:
            st.error(f"Error fetching symbols: {e}")
            return []

    def download_batch_with_retry(self, batch: List[str], retries: int = MAX_RETRIES) -> pd.DataFrame:
        """Download data for a batch of symbols with retry logic."""
        for attempt in range(retries):
            try:
                data = yf.download(batch, period="90d", group_by="ticker", progress=False)
                if not data.empty:
                    return data
                
                if attempt < retries - 1:
                    delay = random.uniform(MIN_DELAY, MAX_DELAY)
                    time.sleep(delay)
                
            except Exception as e:
                if attempt < retries - 1:
                    delay = random.uniform(MIN_DELAY, MAX_DELAY)
                    time.sleep(delay)
                else:
                    st.error(f"Failed to download after {retries} attempts: {e}")
        
        return pd.DataFrame()

    def process_symbol_data(self, symbol: str, data: pd.DataFrame, batch_size: int) -> Dict:
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
            
            current_price = price_data.iloc[-1]
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

    def filter_stocks(self, symbols):
        """Filter stocks based on proximity to 90-day high."""
        results = []
        total_batches = (len(symbols) - 1) // BATCH_SIZE + 1
        progress_bar = st.progress(0)
        
        # Process symbols in smaller batches with delays
        for i in range(0, len(symbols), BATCH_SIZE):
            batch = symbols[i:i + BATCH_SIZE]
            progress = (i // BATCH_SIZE + 1) / total_batches
            progress_bar.progress(progress)
            st.write(f"Processing batch {i//BATCH_SIZE + 1}/{total_batches}")
            
            # Download data with retry logic
            data = self.download_batch_with_retry(batch)
            
            if data.empty:
                st.warning(f"Skipping batch due to download failure")
                continue
            
            # Process each symbol in the batch
            for symbol in batch:
                result = self.process_symbol_data(symbol, data, len(batch))
                if result:
                    results.append(result)
            
            # Add delay between batches to avoid rate limiting
            if i + BATCH_SIZE < len(symbols):
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                time.sleep(delay)
        
        progress_bar.progress(1.0)
        return results

    def run_oracle(self):
        """Run the oracle filtering process."""
        # Clean the log file at the start of each run
        try:
            open('stock_filter.log', 'w').close()
            logging.info("Starting new stock filtering run...")
        except Exception as e:
            st.warning(f"Could not clean log file: {e}")
        
        # Get all US stock symbols
        symbols = self.get_us_symbols()
        
        if not symbols:
            st.error("Error: No symbols found!")
            return
        
        # Filter stocks
        filtered_stocks = self.filter_stocks(symbols)
        
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
            
            st.success(f"Found {len(filtered_stocks)} stocks within {PRICE_THRESHOLD*100}% of their 90-day high!")
            return True
        else:
            st.info("No stocks matched the filter criteria.")
            return False

    def _read_log_file(self):
        """Read and parse the stock filter log file."""
        try:
            with open('stock_filter.log', 'r') as f:
                lines = f.readlines()
            
            # Parse log entries
            stocks = []
            for line in lines:
                if 'Current' in line and '90d High' in line:
                    # Parse the log entry
                    parts = line.split(' - ')[1].split(' | ')
                    symbol = parts[0].split(':')[0].strip()
                    current_price = float(parts[0].split('$')[1].strip())
                    high_90d = float(parts[1].split('$')[1].strip())
                    diff_pct = float(parts[2].split(':')[1].replace('%', '').strip())
                    market_cap = float(parts[3].split('$')[1].replace(',', '').strip())
                    
                    stocks.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        '90d_high': high_90d,
                        'diff_percentage': diff_pct,
                        'market_cap': market_cap
                    })
            
            return stocks
        except Exception as e:
            st.error(f"Error reading log file: {str(e)}")
            return []
    
    def render(self):
        """Render the oracle view."""
        st.title("Stock Oracle")
        
        # Add description
        st.markdown("""
        The Stock Oracle filters US stocks based on the following criteria:
        - Current price within 3% of 90-day high
        - Market cap greater than $2 billion
        - Symbol length <= 4 characters
        - Price between $5 and $100
        """)
        
        # Add run button
        if st.button("🔮 Run Oracle", type="primary"):
            st.info("Running stock oracle... This may take a few minutes.")
            success = self.run_oracle()
            if success:
                st.success("Oracle run completed successfully!")
        
        # Display results from log file
        stocks = self._read_log_file()
        
        if stocks:
            # Convert to DataFrame for display
            df = pd.DataFrame(stocks)
            
            # Format columns
            df['current_price'] = df['current_price'].apply(lambda x: f"${x:.2f}")
            df['90d_high'] = df['90d_high'].apply(lambda x: f"${x:.2f}")
            df['diff_percentage'] = df['diff_percentage'].apply(lambda x: f"{x:.2f}%")
            df['market_cap'] = df['market_cap'].apply(lambda x: f"${x:,.0f}")
            
            # Rename columns for display
            df = df.rename(columns={
                'symbol': 'Symbol',
                'current_price': 'Current Price',
                '90d_high': '90-Day High',
                'diff_percentage': 'Difference',
                'market_cap': 'Market Cap'
            })
            
            # Display the DataFrame
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No oracle results available. Click 'Run Oracle' to start filtering stocks.") 