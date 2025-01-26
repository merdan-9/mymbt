import os
import streamlit as st
from src.utils.data_loader import load_json_file

class Sidebar:
    def __init__(self):
        self.period_options = {
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y"
        }

    def render_stock_controls(self):
        st.sidebar.title("Stock Control Panel")
        
        # Load JSON files
        json_files = [f for f in os.listdir() if f.endswith('.json')]
        
        st.sidebar.subheader("Load Stock Symbols from JSON:")
        default_json_index = json_files.index("ark.json") if "ark.json" in json_files else 0
        selected_json = st.sidebar.selectbox(
            "Select JSON file",
            ["None"] + json_files,
            index=default_json_index + 1 if "ark.json" in json_files else 0
        )
        
        # Stock controls
        user_symbol = st.sidebar.text_input("Quick Symbol Search", "")
        chosen_period = st.sidebar.selectbox("Select Data Period", list(self.period_options.keys()))
        
        threshold = None
        if selected_json != "None":
            threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

        # Load symbols if JSON file selected
        symbols = None
        if selected_json != "None":
            symbols = load_json_file(selected_json)

        return {
            'user_symbol': user_symbol,
            'chosen_period': chosen_period,
            'threshold': threshold,
            'show_ema': True,
            'symbols': symbols
        } 