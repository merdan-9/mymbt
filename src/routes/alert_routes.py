import streamlit as st
from src.components.sidebar import Sidebar
from src.components.alert_view import AlertView
from src.services.alert_service import AlertService
from src.services.stock_service import StockService

def handle_alert_view():
    """Handle the alert view route."""
    sidebar = Sidebar()
    alert_service = AlertService()
    stock_service = StockService()
    alert_view = AlertView(alert_service, stock_service)
    
    # Get sidebar controls
    sidebar.render_stock_controls()
    
    # Render the alert view
    alert_view.render() 