import os
import json
import yfinance as yf
import pandas as pd
import streamlit as st
import mplfinance as mpf

# 1. --------------- STREAMLIT PAGE CONFIG & BASIC STYLE ---------------
st.set_page_config(
    page_title="My Trading System",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Minimal Apple-inspired style overrides
st.markdown(
    """
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                     Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
        background-color: #FBFBFB;
        color: #1D1D1F;
        margin: 0; padding: 0;
    }
    .css-12oz5g7 {
        padding-top: 2rem;  /* top padding for main content */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 2. ---------------------- LOAD JSON FILES -----------------------
def load_json_file(filename):
    """Load symbols from a JSON file."""
    try:
        with open(filename, "r") as f:
            config = json.load(f)
        return config.get("symbols", [])
    except FileNotFoundError:
        st.sidebar.error(f"File {filename} not found.")
        return []
    except json.JSONDecodeError:
        st.sidebar.error(f"Invalid JSON format in {filename}")
        return []

# Get list of JSON files
json_files = [f for f in os.listdir() if f.endswith('.json')]

# Add this function after the load_json_file function
def is_near_high(data, threshold_percent=1.0):
    """
    Check if current price is within threshold_percent of 30-day high.
    
    Args:
        data (pd.DataFrame): Price data
        threshold_percent (float): Maximum percentage difference from high
        
    Returns:
        bool: True if current price is within threshold_percent of high
        float: Percentage difference from high
    """
    current_price = data['Close'].iloc[-1]
    period_high = data['High'].max()
    price_diff_percent = ((period_high - current_price) / period_high) * 100
    
    return price_diff_percent <= threshold_percent, price_diff_percent

# 4. ------------------------- SIDEBAR CONTROLS ------------------------
st.sidebar.title("Stock Control Panel")

# Add buttons for each JSON file
selected_json = None
st.sidebar.subheader("Load Symbols from JSON")
for json_file in json_files:
    if st.sidebar.button(f"Load {json_file}"):
        selected_json = json_file

user_symbol = st.sidebar.text_input("Add a single symbol (optional)", "")


# 5. ------------------------- MAIN APP LAYOUT -------------------------
st.title("My Trading System")
st.write("Select a JSON file from the sidebar to load and plot symbols.")

# Load symbols based on selection
symbols_to_plot = set()
if selected_json:
    symbols = load_json_file(selected_json)
    symbols_to_plot.update(symbols)
    st.write(f"Loaded symbols from {selected_json}")

# Add user symbol if provided
if user_symbol.strip():
    symbols_to_plot.add(user_symbol.strip().upper())

# 6. ------------------------- PLOT FOR EACH SYMBOL --------------------
st.subheader("Filtered Stock Analysis")
threshold = st.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

filtered_symbols = []
for symbol in symbols_to_plot:
    try:
        # Fetch exactly 30 days of data
        data = yf.download(symbol, period="1mo", progress=False)
        
        # Handle empty data
        if data.empty:
            st.warning(f"No data found for {symbol}.")
            continue
            
        # Clean data (keep existing data cleaning code)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        data = data.dropna()
        
        if data.empty:
            continue
            
        data.index = pd.to_datetime(data.index)
        
        # Check if price is near high
        is_near, diff_percent = is_near_high(data, threshold)
        
        if is_near:
            filtered_symbols.append({
                'symbol': symbol,
                'current_price': data['Close'].iloc[-1],
                'period_high': data['High'].max(),
                'diff_percent': diff_percent,
                'data': data
            })
    
    except Exception as e:
        st.error(f"Error processing {symbol}: {str(e)}")

# Display filtered results
if filtered_symbols:
    st.success(f"Found {len(filtered_symbols)} symbols within {threshold}% of their 30-day high")
    
    for stock in filtered_symbols:
        with st.expander(f"{stock['symbol']} - {stock['diff_percent']:.2f}% from high"):
            st.write(f"Current Price: ${stock['current_price']:.2f}")
            st.write(f"30-day High: ${stock['period_high']:.2f}")
            
            # Display the last few rows
            st.write(stock['data'].tail(5))
            
            # Plot candlestick chart
            fig, ax = mpf.plot(
                stock['data'],
                type='candle',
                style='charles',
                volume=True,
                returnfig=True,
                figscale=1.2,
                datetime_format='%Y-%m-%d'
            )
            st.pyplot(fig)
else:
    st.info(f"No symbols found within {threshold}% of their 30-day high")

st.markdown("---")
st.caption("This app is for demonstration purposes only and is not financial advice.")
