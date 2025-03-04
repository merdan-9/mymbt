#!/usr/bin/env python3
"""
Cryptocurrency Price Monitor with Terminal Alerts
This script monitors cryptocurrency prices and displays alerts in the terminal when thresholds are reached.
"""

import time
import yfinance as yf
import argparse
from symbols import SYMBOLS_TO_MONITOR

class CryptoPriceMonitor:
    def __init__(self, symbols_list=None, interval_minutes=5):
        """Initialize the cryptocurrency price monitor."""
        self.symbols_list = symbols_list or SYMBOLS_TO_MONITOR
        self.interval_minutes = interval_minutes
    
    def get_current_price(self, symbol):
        """Get the current price of a symbol."""
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        
        if data.empty:
            return None
        
        current_price = data['Close'].iloc[-1]
        print(f"Current {symbol} price: ${current_price:.6f}")
        return current_price
    
    def send_terminal_alert(self, message):
        """Display an alert in the terminal."""
        print("\n" + "="*80)
        print(f"ALERT: {message}")
        print("="*80 + "\n")
        return True
    
    def check_thresholds(self, symbol, current_price, upper_threshold, lower_threshold):
        alerts = []
        
        # Check upper threshold
        if upper_threshold and current_price >= upper_threshold:
            alerts.append(f"🚨 {symbol} ALERT: Price has reached ${current_price:.6f}, above your upper threshold of ${upper_threshold:.6f}")
        
        # Check lower threshold
        if lower_threshold and current_price <= lower_threshold:
            alerts.append(f"🚨 {symbol} ALERT: Price has dropped to ${current_price:.6f}, below your lower threshold of ${lower_threshold:.6f}")
        
        # Send alerts if any thresholds were crossed
        for alert in alerts:
            self.send_terminal_alert(alert)
    
    def start_monitoring(self):
        """Start the monitoring loop for all symbols."""
        print(f"Starting cryptocurrency price monitor for {len(self.symbols_list)} symbols. Checking every {self.interval_minutes} minutes.")
        
        while True:
            for symbol_data in self.symbols_list:
                symbol = symbol_data["symbol"]
                upper_threshold = symbol_data.get("upper_threshold")
                lower_threshold = symbol_data.get("lower_threshold")
                
                current_price = self.get_current_price(symbol)
                if current_price is not None:
                    self.check_thresholds(symbol, current_price, upper_threshold, lower_threshold)
            
            # Sleep for the specified interval
            print(f"Sleeping for {self.interval_minutes} minutes until next check...")
            time.sleep(self.interval_minutes * 60)

def main():
    """Parse command line arguments and start the monitor."""
    parser = argparse.ArgumentParser(description='Monitor cryptocurrency prices and display terminal alerts.')
    parser.add_argument('--interval', type=int, default=10, help='Check interval in minutes (default: 10)')
    parser.add_argument('--symbols-file', type=str, default=None, help='Path to a custom symbols configuration file')
    
    args = parser.parse_args()
    
    # Use default symbols from symbols.py
    symbols_list = SYMBOLS_TO_MONITOR
    
    # If a custom symbols file is specified, load it
    if args.symbols_file:
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_symbols", args.symbols_file)
        custom_symbols = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_symbols)
        symbols_list = custom_symbols.SYMBOLS_TO_MONITOR
    
    monitor = CryptoPriceMonitor(
        symbols_list=symbols_list,
        interval_minutes=args.interval
    )
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()