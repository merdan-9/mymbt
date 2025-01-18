import json
import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data
def get_stock_data(symbol, period="1mo"):
    """Cached function to fetch stock data using yfinance."""
    return yf.download(symbol, period=period, progress=False)

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

def clean_stock_data(data):
    """Clean and prepare stock data"""
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data.dropna(inplace=True)
    return data 