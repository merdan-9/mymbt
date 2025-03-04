import json
import os
import uuid
from datetime import datetime

class AlertService:
    """Service to manage stock price alerts."""
    
    def __init__(self, alerts_file="alerts.json"):
        """Initialize the alert service with a file to store alerts."""
        self.alerts_file = alerts_file
        self.alerts = self._load_alerts()
    
    def _load_alerts(self):
        """Load alerts from the JSON file."""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"active": [], "history": []}
        return {"active": [], "history": []}
    
    def _save_alerts(self):
        """Save alerts to the JSON file."""
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=4)
    
    def add_alert(self, symbol, price_threshold, alert_type):
        """
        Add a new alert.
        
        Args:
            symbol: Stock symbol
            price_threshold: Price threshold to trigger the alert
            alert_type: 'above' or 'below'
        
        Returns:
            The created alert object
        """
        alert = {
            "id": str(uuid.uuid4()),
            "symbol": symbol.upper(),
            "price_threshold": float(price_threshold),
            "alert_type": alert_type,
            "created_at": datetime.now().isoformat(),
            "triggered": False,
            "triggered_at": None
        }
        
        self.alerts["active"].append(alert)
        self._save_alerts()
        return alert
    
    def get_active_alerts(self):
        """Get all active alerts."""
        return self.alerts["active"]
    
    def get_alert_history(self):
        """Get alert history."""
        return self.alerts["history"]
    
    def delete_alert(self, alert_id):
        """Delete an alert by ID."""
        self.alerts["active"] = [a for a in self.alerts["active"] if a["id"] != alert_id]
        self._save_alerts()
        return True
    
    def mark_alert_triggered(self, alert_id, current_price):
        """Mark an alert as triggered and move it to history."""
        for i, alert in enumerate(self.alerts["active"]):
            if alert["id"] == alert_id:
                alert["triggered"] = True
                alert["triggered_at"] = datetime.now().isoformat()
                alert["triggered_price"] = current_price
                
                # Move to history
                self.alerts["history"].append(alert)
                self.alerts["active"].pop(i)
                self._save_alerts()
                return alert
        
        return None 