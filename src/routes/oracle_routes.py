import streamlit as st
from src.components.sidebar import Sidebar
from src.components.oracle_view import OracleView

def handle_oracle_view():
    """Handle the oracle view route."""
    sidebar = Sidebar()
    oracle_view = OracleView()
    
    # Get sidebar controls
    sidebar.render_stock_controls()
    
    # Render the oracle view
    oracle_view.render() 