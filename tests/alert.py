#!/usr/bin/env python3
"""
DOGE-USD Price Monitor with WhatsApp Alerts
This script monitors the DOGE-USD price every 5 minutes and sends WhatsApp alerts
when the price reaches specified thresholds.
"""

import os
import time
import yfinance as yf
from twilio.rest import Client
from datetime import datetime
import argparse
import logging
import streamlit as st
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('doge_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class DogePriceMonitor:
    def __init__(self, upper_threshold=None, lower_threshold=None, interval_minutes=5):
        """
        Initialize the DOGE price monitor.
        
        Args:
            upper_threshold: Price above which to send an alert
            lower_threshold: Price below which to send an alert
            interval_minutes: How often to check the price (in minutes)
        """
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.interval_minutes = interval_minutes
        self.last_price = None
        self.symbol = "DOGE-USD"
        
        # Twilio configuration
        self.account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
        self.auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
        self.from_whatsapp_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]
        self.to_whatsapp_number = st.secrets["TO_WHATSAPP_NUMBER"]
        
        # Validate Twilio configuration
        if not all([self.account_sid, self.auth_token, self.from_whatsapp_number, self.to_whatsapp_number]):
            logger.warning("Twilio credentials not fully configured. WhatsApp alerts will not be sent.")
    
    def get_current_price(self):
        """Get the current price of DOGE-USD."""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d")
            if data.empty:
                logger.error(f"No data returned for {self.symbol}")
                return None
            
            current_price = data['Close'].iloc[-1]
            logger.info(f"Current {self.symbol} price: ${current_price:.6f}")
            return current_price
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            return None
    
    def send_whatsapp_alert(self, message):
        """Send a WhatsApp alert using Twilio."""
        if not all([self.account_sid, self.auth_token, self.from_whatsapp_number, self.to_whatsapp_number]):
            logger.warning("Cannot send WhatsApp alert: Twilio credentials not configured")
            return False
        
        try:
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.from_whatsapp_number}",
                to=f"whatsapp:{self.to_whatsapp_number}"
            )
            logger.info(f"WhatsApp alert sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert: {e}")
            return False
    
    def check_thresholds(self, current_price):
        """Check if the current price has crossed any thresholds."""
        if self.last_price is None:
            self.last_price = current_price
            return
        
        alerts = []
        
        # Check upper threshold
        if self.upper_threshold and current_price >= self.upper_threshold:
            alerts.append(f"🚨 DOGE-USD ALERT: Price has reached ${current_price:.6f}, above your upper threshold of ${self.upper_threshold:.6f}")
        
        # Check lower threshold
        if self.lower_threshold and current_price <= self.lower_threshold:
            alerts.append(f"🚨 DOGE-USD ALERT: Price has dropped to ${current_price:.6f}, below your lower threshold of ${self.lower_threshold:.6f}")
        
        # Send alerts if any thresholds were crossed
        for alert in alerts:
            self.send_whatsapp_alert(alert)
        
        self.last_price = current_price
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        logger.info(f"Starting DOGE-USD price monitor. Checking every {self.interval_minutes} minutes.")
        logger.info(f"Upper threshold: ${self.upper_threshold if self.upper_threshold else 'Not set'}")
        logger.info(f"Lower threshold: ${self.lower_threshold if self.lower_threshold else 'Not set'}")
        
        try:
            while True:
                current_price = self.get_current_price()
                if current_price is not None:
                    self.check_thresholds(current_price)
                
                # Sleep for the specified interval
                logger.info(f"Sleeping for {self.interval_minutes} minutes until next check...")
                time.sleep(self.interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

def main():
    """Parse command line arguments and start the monitor."""
    parser = argparse.ArgumentParser(description='Monitor DOGE-USD price and send WhatsApp alerts.')
    parser.add_argument('--upper', type=float, help='Upper price threshold for alerts')
    parser.add_argument('--lower', type=float, help='Lower price threshold for alerts')
    parser.add_argument('--interval', type=int, default=5, help='Check interval in minutes (default: 5)')
    
    args = parser.parse_args()
    
    if not args.upper and not args.lower:
        logger.warning("No thresholds set. At least one threshold (--upper or --lower) should be specified.")
    
    monitor = DogePriceMonitor(
        upper_threshold=args.upper,
        lower_threshold=args.lower,
        interval_minutes=args.interval
    )
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()