import streamlit as st
import pandas as pd
import os
from datetime import datetime

class AlertView:
    """Component for displaying and managing stock price alerts."""
    
    def __init__(self, alert_service, stock_service):
        """
        Initialize the alert view.
        
        Args:
            alert_service: AlertService instance
            stock_service: StockService instance
        """
        self.alert_service = alert_service
        self.stock_service = stock_service
    
    def _format_datetime(self, iso_datetime):
        """Format ISO datetime string to readable format."""
        if not iso_datetime:
            return ""
        try:
            dt = datetime.fromisoformat(iso_datetime)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return iso_datetime
    
    def render_add_alert_form(self):
        """Render the form for adding a new alert."""
        st.subheader("Create New Price Alert")
        
        with st.form("add_alert_form"):
            # Symbol input
            symbol = st.text_input("Stock Symbol", "").upper()
            
            # Get current price if symbol is provided
            current_price = None
            if symbol:
                try:
                    stock_info = self.stock_service.get_stock_info(symbol, "1d")
                    if stock_info:
                        current_price = stock_info['current_price']
                        st.info(f"Current price of {symbol}: ${current_price:.2f}")
                except:
                    st.warning(f"Could not fetch current price for {symbol}")
            
            # Alert type selection
            alert_type = st.radio("Alert Type", ["Upper Price Alert", "Lower Price Alert"], horizontal=True)
            
            # Price threshold input based on selected alert type
            if alert_type == "Upper Price Alert":
                price_threshold = st.number_input(
                    "Upper Price Threshold", 
                    min_value=0.01, 
                    step=0.01,
                    value=current_price * 1.05 if current_price else 100.0,  # Default to 5% above current price
                    help="Alert when price goes above this value",
                    key="upper_price_input"
                )
            else:  # Lower Price Alert
                price_threshold = st.number_input(
                    "Lower Price Threshold", 
                    min_value=0.01, 
                    step=0.01,
                    value=current_price * 0.95 if current_price else 100.0,  # Default to 5% below current price
                    help="Alert when price goes below this value",
                    key="lower_price_input"
                )
            
            # Time interval selector
            check_interval = st.number_input("Check Interval (minutes)", 
                                           min_value=1, 
                                           max_value=60, 
                                           value=5,
                                           step=1,
                                           help="How often to check if price thresholds have been crossed")
            
            submitted = st.form_submit_button("Create Alert")
            
            if submitted:
                if not symbol:
                    st.error("Please enter a stock symbol")
                    return
                
                # Create the alert based on selected type
                if alert_type == "Upper Price Alert":
                    alert = self.alert_service.add_alert(
                        symbol=symbol,
                        price_threshold=price_threshold,
                        alert_type="above"
                    )
                else:  # Lower Price Alert
                    alert = self.alert_service.add_alert(
                        symbol=symbol,
                        price_threshold=price_threshold,
                        alert_type="below"
                    )
                
                # Update the check interval in the price monitor service
                if 'price_monitor' in st.session_state:
                    st.session_state.price_monitor.check_interval = check_interval * 60  # Convert to seconds
                
                alert_type_display = "upper" if alert_type == "Upper Price Alert" else "lower"
                st.success(f"{alert_type_display.capitalize()} price alert created for {symbol} at ${price_threshold:.2f}. Checking every {check_interval} minutes.")
                return [alert]
        
        return None
    
    def render_active_alerts(self):
        """Render the list of active alerts."""
        st.subheader("Active Alerts")
        
        active_alerts = self.alert_service.get_active_alerts()
        
        if not active_alerts:
            st.info("No active alerts. Create one above.")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(active_alerts)
        
        # Format the DataFrame
        display_df = df.copy()
        if not display_df.empty:
            display_df['created_at'] = display_df['created_at'].apply(self._format_datetime)
            display_df['alert_type'] = display_df['alert_type'].apply(lambda x: f"Price goes {x} threshold")
            
            # Rename columns for display
            display_df = display_df.rename(columns={
                'symbol': 'Symbol',
                'price_threshold': 'Price Threshold',
                'alert_type': 'Alert Type',
                'created_at': 'Created At'
            })
            
            # Select columns to display
            display_df = display_df[['Symbol', 'Price Threshold', 'Alert Type', 'Created At']]
        
        # Display the DataFrame
        st.dataframe(display_df)
        
        # Add delete buttons
        st.subheader("Delete Alert")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            alert_ids = [a['id'] for a in active_alerts]
            alert_labels = [f"{a['symbol']} - ${a['price_threshold']} ({a['alert_type']})" for a in active_alerts]
            selected_alert = st.selectbox("Select Alert to Delete", 
                                         options=range(len(alert_ids)),
                                         format_func=lambda i: alert_labels[i] if i < len(alert_labels) else "")
        
        with col2:
            if st.button("Delete", key="delete_alert_btn"):
                if selected_alert is not None and 0 <= selected_alert < len(alert_ids):
                    alert_id = alert_ids[selected_alert]
                    if self.alert_service.delete_alert(alert_id):
                        st.success("Alert deleted successfully")
                        st.rerun()
    
    def render_alert_history(self):
        """Render the alert history."""
        st.subheader("Alert History")
        
        alert_history = self.alert_service.get_alert_history()
        
        if not alert_history:
            st.info("No alert history yet.")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(alert_history)
        
        # Format the DataFrame
        display_df = df.copy()
        if not display_df.empty:
            display_df['created_at'] = display_df['created_at'].apply(self._format_datetime)
            display_df['triggered_at'] = display_df['triggered_at'].apply(self._format_datetime)
            display_df['alert_type'] = display_df['alert_type'].apply(lambda x: f"Price went {x} threshold")
            
            # Rename columns for display
            display_df = display_df.rename(columns={
                'symbol': 'Symbol',
                'price_threshold': 'Threshold',
                'triggered_price': 'Triggered Price',
                'alert_type': 'Alert Type',
                'created_at': 'Created At',
                'triggered_at': 'Triggered At'
            })
            
            # Select columns to display
            display_df = display_df[['Symbol', 'Threshold', 'Triggered Price', 'Alert Type', 'Created At', 'Triggered At']]
        
        # Display the DataFrame
        st.dataframe(display_df)
    
    def render_price_check_logs(self):
        """Render the price check logs."""
        st.subheader("Price Check Logs")
        
        log_file = "price_monitor.log"
        
        if not os.path.exists(log_file):
            st.info("No price check logs available yet.")
            return
        
        # Read the log file
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()
            
            # Create tabs for different types of logs
            tab1, tab2 = st.tabs(["Price Checks", "Alert Notifications"])
            
            with tab1:
                # Filter logs to only show price checks
                price_logs = [log for log in logs if "Current price for" in log or "Checking" in log]
                
                if not price_logs:
                    st.info("No price check logs available yet.")
                else:
                    # Display the logs in a text area
                    st.text_area("Recent Price Checks", 
                                value="".join(price_logs[-100:]),  # Show last 100 logs
                                height=300,
                                disabled=True)
            
            with tab2:
                # Filter logs to show alert triggers and Twilio notifications
                alert_logs = [log for log in logs if "Alert triggered" in log or 
                             "Twilio notification" in log or 
                             "Attempting to send Twilio" in log]
                
                if not alert_logs:
                    st.info("No alert notification logs available yet.")
                else:
                    # Display the logs in a text area
                    st.text_area("Alert Notifications", 
                                value="".join(alert_logs[-100:]),  # Show last 100 logs
                                height=300,
                                disabled=True)
            
            # Add a refresh button
            if st.button("Refresh Logs"):
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading log file: {str(e)}")
    
    def render(self):
        """Render the complete alert view."""
        st.title("Stock Price Alerts")
        
        # Add new alert form
        self.render_add_alert_form()
        
        # Show active alerts
        st.markdown("---")
        self.render_active_alerts()
        
        # Show alert history
        st.markdown("---")
        self.render_alert_history()
        
        # Show price check logs
        st.markdown("---")
        self.render_price_check_logs() 