import streamlit as st
from src.components.sidebar import Sidebar
from src.components.crypto_view import CryptoView
from src.services.crypto_service import CryptoService, load_crypto_symbols

def handle_crypto_view():
    """Handle the cryptocurrency view route."""
    sidebar = Sidebar()
    crypto_view = CryptoView()
    crypto_service = CryptoService()
    
    # Get sidebar controls
    controls = sidebar.render_crypto_controls()
    
    # Add a button to return to home
    if st.sidebar.button("Return to Home"):
        st.session_state.view = None
        st.rerun()
    
    # Process crypto data
    filtered_results = []
    if controls['user_symbol'].strip():
        symbol = controls['user_symbol'].strip().upper()
        if not symbol.endswith('-USD'):
            symbol = f"{symbol}-USD"
        
        crypto_info = crypto_service.get_crypto_info(
            symbol,
            controls['chosen_period']
        )
        if crypto_info:
            filtered_results = [crypto_info]
        else:
            st.warning(f"No data found for symbol: {symbol}")
    elif controls['symbols']:
        # Ensure all symbols have -USD suffix
        symbols = [f"{s}-USD" if not s.endswith('-USD') else s for s in controls['symbols']]
        filtered_results = crypto_service.get_filtered_crypto(
            symbols,
            controls['chosen_period'],
            controls['threshold'],
            filter_type=controls['filter_type']
        )
        if not filtered_results:
            filter_desc = "high" if controls['filter_type'] == 'high' else "low"
            st.info(f"No cryptocurrencies found within {controls['threshold']}% of their period {filter_desc} in the selected timeframe.")
    
    # Display results
    crypto_view.display_cryptos(filtered_results, controls) 