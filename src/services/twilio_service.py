import os
import logging
import streamlit as st
from twilio.rest import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='twilio_service.log'
)
logger = logging.getLogger('twilio_service')

class TwilioService:
    """Service to handle WhatsApp message sending via Twilio."""
    
    def __init__(self):
        """Initialize the Twilio service using Streamlit secrets."""
        self.client = None
        
        try:
            # Get credentials from Streamlit secrets
            self.account_sid = st.secrets.get("TWILIO_ACCOUNT_SID")
            self.auth_token = st.secrets.get("TWILIO_AUTH_TOKEN")
            self.from_number = st.secrets.get("TWILIO_WHATSAPP_NUMBER")
            self.to_number = st.secrets.get("TO_WHATSAPP_NUMBER")
            self.template_sid = "HXb5b62575e6e4ff6129ad7c8efe1f983e"  # Content SID for the template
            
            # Initialize Twilio client if credentials are available
            if self.account_sid and self.auth_token:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not found in Streamlit secrets")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
    
    def is_configured(self):
        """Check if Twilio is properly configured."""
        return (self.client is not None and 
                self.account_sid is not None and 
                self.auth_token is not None and 
                self.from_number is not None and
                self.to_number is not None)
    
    def send_whatsapp_message(self, to_number=None, message=None, symbol=None, price=None):
        """
        Send a WhatsApp message using a template.
        
        Args:
            to_number: Optional override for recipient's phone number
            message: Not used when using templates, kept for compatibility
            symbol: Stock symbol for the template
            price: Current price for the template
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.warning("Twilio is not properly configured. Cannot send message.")
            return False
        
        try:
            # Use the provided number or default to the one in secrets
            recipient = to_number or self.to_number
            
            # Format the 'to' number for WhatsApp
            if not recipient.startswith('whatsapp:'):
                recipient = f"whatsapp:{recipient}"
            
            # Format the 'from' number for WhatsApp
            from_number = self.from_number
            if not from_number.startswith('whatsapp:'):
                from_number = f"whatsapp:{from_number}"
            
            # Send the message using the template
            message = self.client.messages.create(
                from_=from_number,
                content_sid=self.template_sid,
                content_variables=f'{{"1":"{symbol}","2":"{price}"}}',
                to=recipient
            )
            
            logger.info(f"WhatsApp message sent successfully for {symbol} at ${price}. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False 