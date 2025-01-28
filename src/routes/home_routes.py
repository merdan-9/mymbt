import streamlit as st
from src.components.layout import create_main_layout

def handle_home_view():
    """Handle the home view route."""
    stocks_selected, crypto_selected, holdings_selected = create_main_layout()
    
    if stocks_selected:
        st.session_state.view = 'stocks'
        st.rerun()
    elif crypto_selected:
        st.session_state.view = 'crypto'
        st.rerun()
    elif holdings_selected:
        st.session_state.view = 'holdings'
        st.rerun() 