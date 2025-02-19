import streamlit as st
from src.components.sidebar import Sidebar
from src.components.stock_view import StockView
from src.services.stock_service import StockService

def handle_stock_view():
    """Handle the stock view route."""
    sidebar = Sidebar()
    stock_view = StockView()
    stock_service = StockService()
    
    # Get sidebar controls
    controls = sidebar.render_stock_controls()
    
    # Process stock data
    filtered_results = []
    if controls['user_symbol'].strip():
        symbol = controls['user_symbol'].strip().upper()
        stock_info = stock_service.get_stock_info(
            symbol,
            controls['chosen_period']
        )
        if stock_info:
            filtered_results = [stock_info]
        else:
            st.warning(f"No data found for symbol: {symbol}")
    elif controls['symbols']:
        filtered_results = stock_service.get_filtered_stocks(
            controls['symbols'],
            controls['chosen_period'],
            controls['threshold']
        )
        if not filtered_results:
            st.info(f"No stocks found within {controls['threshold']}% of their period high in the selected timeframe.")
        
    # Display results
    stock_view.display_stocks(filtered_results, controls) 