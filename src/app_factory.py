import streamlit as st
from src.components.layout import setup_custom_style

def init_app():
    """Initialize and configure the application."""
    # Setup page configuration and styling
    st.set_page_config(page_title="Asset Market Analysis", layout="wide")
    setup_custom_style()
    
    # Initialize session state
    if 'view' not in st.session_state:
        st.session_state.view = None 