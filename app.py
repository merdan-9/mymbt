import streamlit as st
from src.app_factory import init_app
from src.routes.home_routes import handle_home_view
from src.routes.stock_routes import handle_stock_view

def main():
    """Main application entry point."""
    # Initialize the application
    init_app()
    
    # Route to appropriate view handler
    if st.session_state.view == 'stocks':
        handle_stock_view()
    elif st.session_state.view == 'crypto':
        # Add a button to return to home
        if st.sidebar.button("Return to Home"):
            st.session_state.view = None
            st.rerun()
        st.info("Crypto analysis coming soon!")
    else:
        handle_home_view()

if __name__ == "__main__":
    main()
