import os
import json
import openai
import yfinance as yf
import pandas as pd
import streamlit as st
import mplfinance as mpf

# 1. ----------------------- PAGE SETTINGS -----------------------
st.set_page_config(
    page_title="My Trading System",
    layout="centered",  # wide or centered
    initial_sidebar_state="expanded"
)

# Minimal Apple-inspired style
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


# 2. --------------------- LOAD CONFIG JSON ----------------------
with open("config.json", "r") as f:
    config = json.load(f)
stock_list = config.get("symbols", [])


# 3. --------------------- OPENAI SETUP --------------------------
# Make sure you've set your API key as an environment variable or in st.secrets
openai_api_key = os.getenv("OPENAI_API_KEY", "")
if not openai_api_key:
    st.warning("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
else:
    openai.api_key = openai_api_key


# 4. --------------------- FILTER LOGIC EXAMPLE ------------------
def filter_stocks(symbols):
    """
    Example filtering function.
    In real life, you'd have more sophisticated logic,
    e.g., RSI < 30, volume > some threshold, etc.
    """
    filtered = []
    for sym in symbols:
        try:
            data = yf.download(sym, period="1mo", progress=False)
            if data.empty:
                continue
            # Example logic: If the last close price is greater than its 5-day average
            close_prices = data["Close"]
            last_close = close_prices.iloc[-1]
            avg_5day = close_prices.tail(5).mean()

            if True:
                filtered.append(sym)
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
    return filtered


# 5. --------------------- SIDEBAR CONTROLS ----------------------
st.sidebar.title("Stock Control Panel")

single_symbol = st.sidebar.text_input("Enter Single Symbol", "")
analyze_button = st.sidebar.button("Analyze Single Symbol")

filter_button = st.sidebar.button("Filter Default Stocks")


# 6. -------------------- MAIN LAYOUT / CONTENT ------------------

st.title("My Minimal Stock App")
st.write("A simple personal project to fetch & filter stocks, then get ChatGPT's opinion.")


# A. Display single symbol analysis
if analyze_button and single_symbol.strip():
    symbol = single_symbol.strip().upper()
    st.subheader(f"Analysis for {symbol}")

    # Fetch data
    data = yf.download(symbol, period="6mo", progress=False)
    if not data.empty:
        st.write(f"Last available date: {data.index[-1].date()}")
        st.write(data.tail(5))

        # Plot a candlestick chart
        st.write("### Candlestick Chart (last 30 days)")
        short_data = data.tail(30)
        fig, ax = mpf.plot(
            short_data,
            type='candle',
            style='charles',
            volume=True,
            returnfig=True,
            figscale=1.2
        )
        st.pyplot(fig)

        # Option to consult ChatGPT about the single symbol
        if openai_api_key:
            consult = st.button("Ask ChatGPT for opinion on this symbol")
            if consult:
                # Basic prompt
                prompt_text = (
                    f"Please provide a brief analysis or opinion about the stock {symbol}. "
                    f"Here is some recent data: {short_data.tail().to_dict()}. "
                    "Consider price trends, fundamentals, or any relevant factors. "
                    "Keep it concise."
                )
                with st.spinner("Asking ChatGPT..."):
                    try:
                        response = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=prompt_text,
                            max_tokens=150,
                            temperature=0.7
                        )
                        st.write("**ChatGPT says:**")
                        st.success(response.choices[0].text.strip())
                    except Exception as e:
                        st.error(f"Error calling OpenAI API: {e}")
    else:
        st.warning(f"No data found for symbol: {symbol}")


# B. Filter default stocks from JSON
if filter_button:
    with st.spinner("Filtering stocks..."):
        filtered_symbols = filter_stocks(stock_list)

    if filtered_symbols:
        st.write("## Filtered Stocks")
        st.write(
            "Simple criterion: last close price > 5-day average (1-month data)."
        )
        st.write(filtered_symbols)

        # Option to consult ChatGPT about the entire list
        if openai_api_key:
            ask_all = st.button("Ask ChatGPT about these filtered stocks")
            if ask_all:
                prompt_text = (
                    "The following stocks have their last close price above their 5-day average: "
                    f"{filtered_symbols}. "
                    "Please provide a brief insight or reasoning on whether these might be "
                    "interesting to investigate further."
                )
                with st.spinner("Asking ChatGPT..."):
                    try:
                        response = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=prompt_text,
                            max_tokens=200,
                            temperature=0.7
                        )
                        st.write("**ChatGPT says:**")
                        st.success(response.choices[0].text.strip())
                    except Exception as e:
                        st.error(f"Error calling OpenAI API: {e}")
    else:
        st.info("No stocks passed the filter or no data was available.")


# C. Footer
st.markdown("---")
st.caption("This app is for making million, billion, trillion dollars.")
