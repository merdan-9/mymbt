import json
from datetime import datetime
import pandas as pd

def load_transactions():
    """Load transactions from JSON file."""
    try:
        with open('data/holdings/transactions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_transactions(transactions):
    """Save transactions to JSON file."""
    with open('data/holdings/transactions.json', 'w') as f:
        json.dump(transactions, f, indent=4)

def log_transaction(transaction_type, symbol, price, units, current_price=None):
    """Log a new transaction."""
    transactions = load_transactions()
    
    total_value = price * units
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": transaction_type,
        "symbol": symbol.upper(),
        "price": float(price),
        "units": float(units),
        "total_value": float(total_value)
    }
    
    # Add current market price for SELL transactions
    if transaction_type == "SELL" and current_price is not None:
        transaction["market_price"] = float(current_price)
        transaction["market_value"] = float(current_price * units)
        transaction["profit_loss"] = float((current_price - price) * units)
    
    transactions.append(transaction)
    save_transactions(transactions)

def get_transaction_history(symbol=None, transaction_type=None, start_date=None, end_date=None):
    """Get filtered transaction history."""
    transactions = load_transactions()
    df = pd.DataFrame(transactions)
    
    if df.empty:
        return pd.DataFrame()
    
    # Apply filters
    if symbol:
        df = df[df['symbol'] == symbol.upper()]
    if transaction_type:
        df = df[df['type'] == transaction_type]
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    return df.sort_values('date', ascending=False)

def get_transaction_summary():
    """Get summary statistics of transactions."""
    df = get_transaction_history()
    if df.empty:
        return {
            "total_buys": 0,
            "total_sells": 0,
            "total_invested": 0,
            "total_returned": 0
        }
    
    buys = df[df['type'] == 'BUY']
    sells = df[df['type'] == 'SELL']
    
    return {
        "total_buys": len(buys),
        "total_sells": len(sells),
        "total_invested": float(buys['total_value'].sum()),
        "total_returned": float(sells['total_value'].sum())
    } 