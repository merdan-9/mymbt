import os
import json
import yfinance as yf
import pandas as pd
import streamlit as st
import mplfinance as mpf
from datetime import datetime, timedelta

# 1. --------------------- STREAMLIT PAGE CONFIG & STYLE ---------------------
st.set_page_config(
    page_title="My Enhanced Trading System",
    layout="wide",
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

# 2. ---------------------- HELPER FUNCTIONS -----------------------
@st.cache_data
def get_stock_data(symbol, period="1mo"):
    """
    Cached function to fetch stock data using yfinance.
    """
    return yf.download(symbol, period=period, progress=False)

def load_json_file(filename):
    """
    Load symbols from a JSON file.
    """
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

def is_near_high(data, threshold_percent=1.0):
    """
    Check if current price is within threshold_percent of the highest price 
    over the specified period.

    Returns:
        - bool: True if current price is within threshold_percent of high
        - float: Percentage difference from high
        - float: 30-day (or chosen period) high
    """
    current_price = data['Close'].iloc[-1]
    period_high = data['High'].max()
    price_diff_percent = ((period_high - current_price) / period_high) * 100
    return price_diff_percent <= threshold_percent, price_diff_percent, period_high


# 3. ------------------------- SIDEBAR CONTROLS ------------------------
st.sidebar.title("Stock Control Panel")

# Load JSON files from current directory
json_files = [f for f in os.listdir() if f.endswith('.json')]

st.sidebar.subheader("Load Symbols from JSON:")
selected_json = st.sidebar.selectbox("Select JSON file", ["None"] + json_files)

# User can also add a single symbol
user_symbol = st.sidebar.text_input("Quick Symbol Search", "")

# Period selection
period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
chosen_period = st.sidebar.selectbox("Select Data Period", list(period_options.keys()))

# Chart type selection
chart_type = st.sidebar.selectbox("Chart Type", ["Candlestick", "Line"])

# Threshold for near-high check (only shown when using JSON files)
if selected_json != "None":
    threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

# 4. ------------------------- MAIN APP LAYOUT -------------------------
st.title("My Enhanced Trading System")
st.write("""
This system loads symbols from selected JSON files or user input, 
retrieves recent data from Yahoo Finance, and shows those near 
their highest price within a user-defined threshold.
""")

# 5. ------------------------ GET & FILTER SYMBOLS ---------------------
symbols_to_plot = set()
filtered_results = []

# If user entered a single symbol, process it directly
if user_symbol.strip():
    symbol = user_symbol.strip().upper()
    try:
        data = get_stock_data(symbol, period=period_options[chosen_period])
        if data.empty:
            st.warning(f"No data found for {symbol}.")
        else:
            # Clean data
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            data.dropna(inplace=True)
            
            if not data.empty:
                filtered_results.append({
                    'symbol': symbol,
                    'data': data,
                    'current_price': data['Close'].iloc[-1],
                    'period_high': data['High'].max(),
                    'period_low': data['Low'].min(),
                    'average_volume': data['Volume'].mean(),
                    'diff_percent': ((data['High'].max() - data['Close'].iloc[-1]) / data['High'].max()) * 100
                })
    except Exception as e:
        st.error(f"Error processing {symbol}: {str(e)}")

# Process JSON file symbols if selected and no single symbol is entered
elif selected_json != "None":
    symbols_from_json = load_json_file(selected_json)
    symbols_to_plot.update(symbols_from_json)
    st.write(f"Loaded symbols from **{selected_json}**.")

    if not symbols_to_plot:
        st.info("No symbols found in the selected JSON file.")
        st.stop()

    # Process JSON symbols with threshold filtering
    for symbol in symbols_to_plot:
        try:
            data = get_stock_data(symbol, period=period_options[chosen_period])
            if data.empty:
                st.warning(f"No data found for {symbol}.")
                continue
            
            # Clean data
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            data.dropna(inplace=True)
            
            if data.empty:
                st.warning(f"Data is empty after cleaning for {symbol}.")
                continue
            
            # Check if near high
            is_near, diff_percent, period_high = is_near_high(data, threshold)
            
            if is_near:
                filtered_results.append({
                    'symbol': symbol,
                    'data': data,
                    'current_price': data['Close'].iloc[-1],
                    'period_high': period_high,
                    'period_low': data['Low'].min(),
                    'average_volume': data['Volume'].mean(),
                    'diff_percent': diff_percent
                })
        except Exception as e:
            st.error(f"Error processing {symbol}: {str(e)}")

# 7. ---------------------- DISPLAY FILTERED SYMBOLS -------------------
if filtered_results:
    if user_symbol.strip():
        st.subheader(f"Stock Data for {user_symbol.strip().upper()}")
    else:
        st.success(
            f"Found {len(filtered_results)} symbol(s) within {threshold}% of their highest price "
            f"over the last {chosen_period}."
        )

    # Create tabs for each symbol
    tab_titles = [res['symbol'] for res in filtered_results]
    tabs = st.tabs(tab_titles)
    
    for i, stock_info in enumerate(filtered_results):
        with tabs[i]:
            symbol = stock_info['symbol']
            data = stock_info['data']
            st.subheader(f"{symbol}")
            
            col1, col2 = st.columns([1,2])
            with col1:
                st.write(f"**Current Price:** ${stock_info['current_price']:.2f}")
                st.write(f"**Period High:** ${stock_info['period_high']:.2f}")
                st.write(f"**Period Low:** ${stock_info['period_low']:.2f}")
                st.write(f"**Avg. Volume:** {stock_info['average_volume']:.0f}")
                st.write(f"**% from High:** {stock_info['diff_percent']:.2f}%")
                st.write("Recent Data:")
                st.dataframe(data.tail(5))
            
            with col2:
                st.write("**Price Chart**")
                if chart_type == "Candlestick":
                    fig, ax = mpf.plot(
                        data,
                        type='candle',
                        style='charles',
                        volume=True,
                        returnfig=True,
                        figscale=1.2,
                        datetime_format='%Y-%m-%d'
                    )
                    st.pyplot(fig)
                else:
                    st.line_chart(data["Close"])
else:
    if user_symbol.strip():
        st.info(f"No data found for {user_symbol.strip().upper()}")
    elif selected_json != "None":
        st.info(
            f"No symbols found within {threshold}% of their highest "
            f"price over the last {chosen_period}."
        )
    else:
        st.info("Please enter a symbol to search or select a JSON file.")

# Footer
st.markdown("---")
st.caption("This app is for demonstration purposes only and is not financial advice.")
