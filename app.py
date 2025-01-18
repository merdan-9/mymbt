import os
import streamlit as st
from src.config import setup_page_config, apply_style
from src.data_loader import get_stock_data, load_json_file, clean_stock_data
from src.indicators import is_near_high
from src.plotting import create_stock_plot

# Setup page configuration and styling
setup_page_config()
apply_style()

# Sidebar controls
st.sidebar.title("Stock Control Panel")

# Load JSON files from current directory
json_files = [f for f in os.listdir() if f.endswith('.json')]

st.sidebar.subheader("Load Symbols from JSON:")
default_json_index = json_files.index("ark.json") if "ark.json" in json_files else 0
selected_json = st.sidebar.selectbox("Select JSON file", ["None"] + json_files, 
                                   index=default_json_index + 1 if "ark.json" in json_files else 0)

# User inputs
user_symbol = st.sidebar.text_input("Quick Symbol Search", "")
period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
chosen_period = st.sidebar.selectbox("Select Data Period", list(period_options.keys()))

if selected_json != "None":
    threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

# Technical indicators controls
st.sidebar.subheader("Technical Indicators")
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
rsi_period = st.sidebar.number_input("RSI Period", min_value=1, value=14)
show_ema = st.sidebar.checkbox("Show EMA", value=True)
ema_period = st.sidebar.number_input("EMA Period", min_value=1, value=20)

# Process symbols and display results
filtered_results = []

if selected_json != "None":
    symbols = load_json_file(selected_json)
    for symbol in symbols:
        try:
            data = get_stock_data(symbol, period=period_options[chosen_period])
            if not data.empty:
                data = clean_stock_data(data)
                if not data.empty:
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

elif user_symbol.strip():
    symbol = user_symbol.strip().upper()
    try:
        data = get_stock_data(symbol, period=period_options[chosen_period])
        if not data.empty:
            data = clean_stock_data(data)
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

# Display results
if filtered_results:
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
                
                current_volume = data['Volume'].iloc[-1]
                avg_volume = stock_info['average_volume']
                volume_diff_percent = ((current_volume - avg_volume) / avg_volume) * 100
                volume_sign = "+" if volume_diff_percent > 0 else ""
                
                st.write(f"**Avg. Volume:** {avg_volume:,.0f} ({volume_sign}{volume_diff_percent:.1f}%)")
                st.write(f"**% from High:** {stock_info['diff_percent']:.1f}%")
            
            with col2:
                st.write("**Price Chart**")
                fig = create_stock_plot(data, show_rsi, show_ema, rsi_period, ema_period)
                st.pyplot(fig)
else:
    if selected_json != "None":
        st.info(f"No symbols found within {threshold}% of their highest price over the last {chosen_period}.")
    elif user_symbol.strip():
        st.info(f"No data found for {user_symbol.strip().upper()}")
    else:
        st.info("Please enter a symbol to search or select a JSON file.")
