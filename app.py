import os
import json
import yfinance as yf
import pandas as pd
import streamlit as st
import mplfinance as mpf
from datetime import datetime, timedelta
import numpy as np
import altair as alt
import matplotlib.pyplot as plt

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

def calculate_rsi(data, periods=14):
    """
    Calculate RSI indicator using pandas
    """
    # Calculate price changes
    delta = data['Close'].diff()
    
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # Calculate average gain and loss
    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_ema(data, span=20):
    """
    Calculate EMA indicator using pandas
    """
    return data['Close'].ewm(span=span, adjust=False).mean()

# 3. ------------------------- SIDEBAR CONTROLS ------------------------
st.sidebar.title("Stock Control Panel")

# Load JSON files from current directory
json_files = [f for f in os.listdir() if f.endswith('.json')]

st.sidebar.subheader("Load Symbols from JSON:")
# Modified to set "ark.json" as default if it exists in the list
default_json_index = json_files.index("ark.json") if "ark.json" in json_files else 0
selected_json = st.sidebar.selectbox("Select JSON file", ["None"] + json_files, 
                                   index=default_json_index + 1 if "ark.json" in json_files else 0)

# User can also add a single symbol
user_symbol = st.sidebar.text_input("Quick Symbol Search", "")

# Period selection
period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
chosen_period = st.sidebar.selectbox("Select Data Period", list(period_options.keys()))

# Threshold for near-high check (only shown when using JSON files)
if selected_json != "None":
    threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

# Add these controls in the sidebar section
st.sidebar.subheader("Technical Indicators")
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
rsi_period = st.sidebar.number_input("RSI Period", min_value=1, value=14)

show_ema = st.sidebar.checkbox("Show EMA", value=True)
ema_period = st.sidebar.number_input("EMA Period", min_value=1, value=20)

# 4. ------------------------- MAIN APP LAYOUT -------------------------

# 5. ------------------------ GET & FILTER SYMBOLS ---------------------
symbols_to_plot = set()
filtered_results = []

# Process JSON file symbols if selected (giving it priority)
if selected_json != "None":
    symbols_from_json = load_json_file(selected_json)
    symbols_to_plot.update(symbols_from_json)
    
    if user_symbol.strip():
        st.info("JSON file selected - ignoring single symbol input. Clear the JSON selection to use single symbol search.")
    
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

# If no JSON file is selected, process single symbol if provided
elif user_symbol.strip():
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

# 7. ---------------------- DISPLAY FILTERED SYMBOLS -------------------
if filtered_results:
    # Update the header display logic
    if selected_json != "None":
        # st.success(
        #     f"Found {len(filtered_results)} symbol(s) within {threshold}% of their highest price "
        #     f"over the last {chosen_period}."
        # )
        pass
    else:  # Single symbol case
        st.subheader(f"Stock Data for {user_symbol.strip().upper()}")

    # Create tabs for each symbol
    tab_titles = [res['symbol'] for res in filtered_results]
    tabs = st.tabs(tab_titles)
    
    for i, stock_info in enumerate(filtered_results):
        with tabs[i]:
            symbol = stock_info['symbol']
            data = stock_info['data']
            st.subheader(f"{symbol}")
            
            col1, col2 = st.columns([1,3])
            with col1:
                st.write(f"**Current Price:** ${stock_info['current_price']:.2f}")
                st.write(f"**Period High:** ${stock_info['period_high']:.2f}")
                st.write(f"**Period Low:** ${stock_info['period_low']:.2f}")
                
                # Calculate volume comparison
                current_volume = data['Volume'].iloc[-1]
                avg_volume = stock_info['average_volume']
                volume_diff_percent = ((current_volume - avg_volume) / avg_volume) * 100
                volume_sign = "+" if volume_diff_percent > 0 else ""
                
                st.write(f"**Avg. Volume:** {avg_volume:,.0f} ({volume_sign}{volume_diff_percent:.1f}%)")
                st.write(f"**% from High:** {stock_info['diff_percent']:.1f}%")
            
            with col2:
                st.write("**Price Chart**")
                # Calculate indicators
                if show_rsi:
                    rsi = calculate_rsi(data, rsi_period)
                    rsi_plot = mpf.make_addplot(rsi, panel=2, ylabel='RSI',
                                               ylim=(0, 100),
                                               secondary_y=False,
                                               color='#6236FF')  # Modern purple for RSI
                    
                    overbought = pd.Series(70, index=data.index)
                    oversold = pd.Series(30, index=data.index)
                    ob_plot = mpf.make_addplot(overbought, panel=2, color='#FF6B6B', linestyle='--', secondary_y=False)
                    os_plot = mpf.make_addplot(oversold, panel=2, color='#4CAF50', linestyle='--', secondary_y=False)
                
                if show_ema:
                    ema = calculate_ema(data, ema_period)
                    ema_plot = mpf.make_addplot(ema, color='#2196F3')
                
                # Prepare addplots
                addplots = []
                if show_ema:
                    addplots.append(ema_plot)
                if show_rsi:
                    addplots.extend([rsi_plot, ob_plot, os_plot])
                
                # Create custom style with modern colors
                mc = mpf.make_marketcolors(
                    # up='#FFB74D',      # Orange/yellow for up candles
                    # down='#42A5F5',    # Blue for down candles
                    # edge={'up': '#FFA726', 'down': '#1E88E5'},
                    # wick={'up': '#FFA726', 'down': '#1E88E5'},
                    up='#42A5F5',      # Orange/yellow for up candles
                    down='#FFB74D',    # Blue for down candles
                    edge={'up': '#1E88E5', 'down': '#FFA726'},
                    wick={'up': '#1E88E5', 'down': '#FFA726'},
                    volume={'up': '#FFE0B2', 'down': '#BBDEFB'},  # Lighter shades for volume
                )
                
                s = mpf.make_mpf_style(
                    marketcolors=mc,
                    gridstyle='',      # Remove grid
                    gridcolor='#0A192F',  # Set grid color same as background to hide it
                    facecolor='white',  # White background
                    edgecolor='white',
                    figcolor='white',
                    rc={
                        'axes.labelcolor': '#333333',
                        'xtick.color': '#333333',
                        'ytick.color': '#333333',
                        'axes.facecolor': 'white'
                    }
                )
                
                # Update plot configuration
                fig, ax = mpf.plot(
                    data,
                    type='candle',
                    style=s,
                    volume=True,
                    addplot=addplots if addplots else None,
                    returnfig=True,
                    figscale=1.8,
                    datetime_format='%Y-%m-%d',
                    panel_ratios=(6,2,2) if show_rsi else (6,2),
                    tight_layout=True,
                    figratio=(16,9),
                    volume_panel=1,
                    show_nontrading=False,
                    fill_between=dict(y1=data['Low'].values, y2=data['High'].values, alpha=0.1)  # Add subtle fill
                )
                
                # Add this right after the plot to adjust the figure background
                plt.gcf().patch.set_facecolor('white')
                for ax in plt.gcf().axes:
                    ax.set_facecolor('white')
                    # Remove spines
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                
                # Adjust layout
                plt.subplots_adjust(hspace=0.3)
                
                st.pyplot(fig)
else:
    if selected_json != "None":
        st.info(
            f"No symbols found within {threshold}% of their highest "
            f"price over the last {chosen_period}."
        )
    elif user_symbol.strip():
        st.info(f"No data found for {user_symbol.strip().upper()}")
    else:
        st.info("Please enter a symbol to search or select a JSON file.")

# Footer
# st.markdown("---")
# st.caption("This app is for demonstration purposes only and is not financial advice.")
