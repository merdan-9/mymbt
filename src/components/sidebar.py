import os
import streamlit as st
from src.utils.data_loader import load_json_file

class Sidebar:
    def __init__(self):
        self.stock_period_options = {
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year"
        }
        
        # Initialize navigation state if not exists
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'stocks'
    
    def render_navigation(self):
        """Render the navigation menu in the sidebar."""
        st.sidebar.title("Navigation")
        
        # Navigation buttons
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📊 Stocks", use_container_width=True, 
                        type="primary" if st.session_state.current_view == 'stocks' else "secondary"):
                st.session_state.current_view = 'stocks'
                st.rerun()
        
        with col2:
            if st.button("🔔 Alerts", use_container_width=True,
                        type="primary" if st.session_state.current_view == 'alerts' else "secondary"):
                st.session_state.current_view = 'alerts'
                st.rerun()
        
        st.sidebar.markdown("---")
    
    def render_stock_controls(self):
        """Render the sidebar with navigation and stock controls."""
        # Render navigation first
        self.render_navigation()
        
        st.sidebar.title("Stock Controls")
            
        # Load JSON files from root directory
        stock_files = [f for f in os.listdir('.') if f.endswith('.json')]
        
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
            symbols = load_json_file(selected_json)
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