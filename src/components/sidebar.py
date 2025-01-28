import os
import streamlit as st
from src.utils.data_loader import load_json_file
from src.services.crypto_service import load_crypto_symbols

class Sidebar:
    def __init__(self):
        self.stock_period_options = {
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year"
        }
        self.crypto_period_options = {
            "5d": "5 Days",
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year"
        }
    
    def render_stock_controls(self):
        """Render the sidebar with navigation and stock controls."""
        st.sidebar.title("Stock Controls")
            
        # Load JSON files from data directories
        stock_files = [f for f in os.listdir('data/stocks') if f.endswith('.json')]
        
        st.sidebar.subheader("Load Stock Symbols from JSON:")
        default_json_index = stock_files.index("ark.json") if "ark.json" in stock_files else 0
        selected_json = st.sidebar.selectbox(
            "Select JSON file",
            ["None"] + stock_files,
            index=default_json_index + 1 if "ark.json" in stock_files else 0
        )
            
        # Initialize session state for symbols if not exists
        if 'symbols' not in st.session_state:
            st.session_state.symbols = []
            
        if selected_json != "None":
            st.session_state.selected_json = selected_json
            
        # Load symbols if JSON file selected
        symbols = []
        if selected_json != "None":
            symbols = load_json_file(os.path.join('data/stocks', selected_json))
            st.session_state.symbols = symbols

        # Stock controls
        user_symbol = st.sidebar.text_input("Quick Symbol Search", "")
        chosen_period = st.sidebar.selectbox("Select Data Period", list(self.stock_period_options.keys()))
        
        threshold = None
        if selected_json != "None":
            threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

        return {
            'user_symbol': user_symbol,
            'chosen_period': chosen_period,
            'threshold': threshold,
            'show_ema': True,
            'symbols': symbols
        }
        
    def render_crypto_controls(self):
        """Render the sidebar with navigation and cryptocurrency controls."""
        st.sidebar.title("Crypto Controls")
        
        # Load crypto symbols
        symbols = load_crypto_symbols()
        
        # Initialize session state for symbols if not exists
        if 'crypto_symbols' not in st.session_state:
            st.session_state.crypto_symbols = symbols
            
        # Crypto controls
        user_symbol = st.sidebar.text_input("Quick Symbol Search (e.g., BTC, ETH)", "")
        chosen_period = st.sidebar.selectbox("Select Data Period", list(self.crypto_period_options.keys()))
        
        # Filter type selection
        filter_type = st.sidebar.radio("Filter Type", ["High", "Low"], horizontal=True)
        
        # Threshold label changes based on filter type
        threshold_label = "Price-to-High Threshold (%)" if filter_type == "High" else "Price-to-Low Threshold (%)"
        threshold = st.sidebar.slider(threshold_label, 0.0, 5.0, 1.0, 0.1)

        return {
            'user_symbol': user_symbol,
            'chosen_period': chosen_period,
            'threshold': threshold,
            'filter_type': filter_type.lower(),
            'show_ema': True,
            'symbols': symbols
        } 