import streamlit as st
from src.app_factory import init_app
from src.routes.stock_routes import handle_stock_view

def main():
    """Main application entry point."""
    # Initialize the application
    init_app()
    
    # Only handle stock view
    handle_stock_view()

if __name__ == "__main__":
    main()
