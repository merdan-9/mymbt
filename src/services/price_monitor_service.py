import threading
import time
import logging
from datetime import datetime
import yfinance as yf
from src.services.alert_service import AlertService
from src.services.twilio_service import TwilioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='price_monitor.log'
)
logger = logging.getLogger('price_monitor')

class PriceMonitorService:
    """Service to monitor stock prices and trigger alerts."""
    
    def __init__(self, alert_service=None, twilio_service=None, check_interval=300):
        """
        Initialize the price monitor service.
        
        Args:
            alert_service: AlertService instance
            twilio_service: TwilioService instance
            check_interval: Interval in seconds between price checks (default: 5 minutes)
        """
        self.alert_service = alert_service or AlertService()
        self.twilio_service = twilio_service or TwilioService()
        self.check_interval = check_interval
        self.is_running = False
        self.monitor_thread = None
        self.price_cache = {}  # Cache to store recent price data
        
    def get_current_price(self, symbol):
        """Get the current price for a symbol."""
        try:
            # Check if we have a recent price in cache (less than 60 seconds old)
            cache_entry = self.price_cache.get(symbol)
            if cache_entry and (datetime.now() - cache_entry['timestamp']).total_seconds() < 60:
                return cache_entry['price']
            
            # Fetch new price
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            current_price = data['Close'].iloc[-1]
            
            # Log the current price
            logger.info(f"Current price for {symbol}: ${current_price:.6f}")
            
            # Update cache
            self.price_cache[symbol] = {
                'price': current_price,
                'timestamp': datetime.now()
            }
            
            return current_price
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None
    
    def check_alerts(self):
        """Check all active alerts against current prices."""
        active_alerts = self.alert_service.get_active_alerts()
        
        if not active_alerts:
            logger.info("No active alerts to check")
            return
        
        logger.info(f"Checking {len(active_alerts)} active alerts")
        
        for alert in active_alerts:
            symbol = alert['symbol']
            threshold = alert['price_threshold']
            alert_type = alert['alert_type']
            
            current_price = self.get_current_price(symbol)
            if current_price is None:
                continue
            
            # Log the check with price and threshold
            logger.info(f"Checking {symbol} alert: current price ${current_price:.6f}, {alert_type} threshold ${threshold:.6f}")
            
            # Check if alert condition is met
            is_triggered = False
            if alert_type == 'above' and current_price >= threshold:
                is_triggered = True
                message = f"{symbol} price is now ${current_price:.2f}, above your threshold of ${threshold:.2f}"
            elif alert_type == 'below' and current_price <= threshold:
                is_triggered = True
                message = f"{symbol} price is now ${current_price:.2f}, below your threshold of ${threshold:.2f}"
            
            if is_triggered:
                logger.info(f"Alert triggered: {message}")
                
                # Mark alert as triggered
                triggered_alert = self.alert_service.mark_alert_triggered(alert['id'], current_price)
                
                # Send notification via Twilio
                logger.info(f"Attempting to send Twilio notification for {symbol} alert")
                
                # Try to send the message using the template
                success = self.twilio_service.send_whatsapp_message(
                    symbol=symbol,
                    price=f"{current_price:.2f}"
                )
                
                # Log the result
                if success:
                    logger.info(f"Twilio notification sent successfully for {symbol} alert")
                else:
                    logger.error(f"Failed to send Twilio notification for {symbol} alert")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        logger.info("Starting price monitor loop")
        
        while self.is_running:
            try:
                logger.info(f"Running price check (interval: {self.check_interval} seconds)")
                self.check_alerts()
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
            
            # Sleep until next check
            logger.info(f"Next check in {self.check_interval} seconds")
            time.sleep(self.check_interval)
    
    def start(self):
        """Start the price monitoring service."""
        if self.is_running:
            logger.warning("Price monitor is already running")
            return False
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Price monitor started with check interval of {self.check_interval} seconds")
        return True
    
    def stop(self):
        """Stop the price monitoring service."""
        if not self.is_running:
            logger.warning("Price monitor is not running")
            return False
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        logger.info("Price monitor stopped")
        return True 