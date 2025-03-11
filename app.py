import streamlit as st
from src.app_factory import init_app
from src.routes.stock_routes import handle_stock_view
from src.routes.alert_routes import handle_alert_view
from src.routes.oracle_routes import handle_oracle_view
from src.services.alert_service import AlertService
from src.services.price_monitor_service import PriceMonitorService
from src.services.twilio_service import TwilioService

def main():
    """Main application entry point."""
    # Initialize the application
    init_app()
    
    # Initialize services
    alert_service = AlertService()
    twilio_service = TwilioService()
    
    # Initialize or retrieve price monitor from session state
    if 'price_monitor' not in st.session_state:
        price_monitor = PriceMonitorService(alert_service, twilio_service)
        st.session_state.price_monitor = price_monitor
    else:
        price_monitor = st.session_state.price_monitor
    
    # Start the price monitor in a background thread if not already started
    if 'price_monitor_started' not in st.session_state:
        price_monitor.start()
        st.session_state.price_monitor_started = True
    
    # Route to the appropriate view based on navigation state
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'stocks'
        
    if st.session_state.current_view == 'stocks':
        handle_stock_view()
    elif st.session_state.current_view == 'alerts':
        handle_alert_view()
    elif st.session_state.current_view == 'oracle':
        handle_oracle_view()

if __name__ == "__main__":
    main()
