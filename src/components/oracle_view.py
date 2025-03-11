import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from src.services.stock_service import StockService

class OracleView:
    """Component for displaying stock oracle results."""
    
    def __init__(self):
        """Initialize the oracle view."""
        self.stock_service = StockService()
    
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
            
            # Run the oracle script
            import subprocess
            try:
                result = subprocess.run(['python3', 'tests/oracle.py'], 
                                     capture_output=True, 
                                     text=True)
                if result.returncode == 0:
                    st.success("Oracle run completed successfully!")
                else:
                    st.error(f"Error running oracle: {result.stderr}")
            except Exception as e:
                st.error(f"Error running oracle: {str(e)}")
        
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