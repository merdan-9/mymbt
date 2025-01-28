import json
import yfinance as yf
import pandas as pd
from .transaction_service import log_transaction

def load_holdings():
    """Load holdings from JSON file."""
    try:
        with open('data/holdings/holdings.json', 'r') as f:
            holdings = json.load(f)
            # Remove the empty template if it exists
            if len(holdings) == 1 and holdings[0]["symbol"] == "":
                return []
            return holdings
    except FileNotFoundError:
        return []

def save_holdings(holdings):
    """Save holdings to JSON file."""
    with open('data/holdings/holdings.json', 'w') as f:
        json.dump(holdings, f, indent=4)

def add_holding(symbol, price, unit):
    """Add a new stock holding."""
    holdings = load_holdings()
    new_holding = {
        "symbol": symbol.upper(),
        "price": float(price),
        "unit": float(unit)
    }
    holdings.append(new_holding)
    save_holdings(holdings)
    
    # Log the buy transaction
    log_transaction("BUY", symbol, price, unit)

def delete_holding(index):
    """Delete a holding by index."""
    holdings = load_holdings()
    if 0 <= index < len(holdings):
        holding = holdings[index]
        
        # Get current market price for the sell transaction
        symbol = holding['symbol']
        stock = yf.Ticker(symbol)
        current_price = stock.history(period='1d')['Close'].iloc[-1]
        
        # Log the sell transaction
        log_transaction(
            "SELL",
            holding['symbol'],
            holding['price'],
            holding['unit'],
            current_price
        )
        
        holdings.pop(index)
        save_holdings(holdings)

def get_holdings_data():
    """Get current market data for holdings."""
    holdings = load_holdings()
    if not holdings:
        return pd.DataFrame()
    
    data = []
    for holding in holdings:
        symbol = holding['symbol']
        stock = yf.Ticker(symbol)
        current_price = stock.history(period='1d')['Close'].iloc[-1]
        cost_basis = holding['price'] * holding['unit']
        market_value = current_price * holding['unit']
        profit_loss = market_value - cost_basis
        profit_loss_percent = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        data.append({
            'Symbol': symbol,
            'Units': holding['unit'],
            'Purchase Price': holding['price'],
            'Current Price': current_price,
            'Cost Basis': cost_basis,
            'Market Value': market_value,
            'Profit/Loss': profit_loss,
            'P/L %': f"{profit_loss_percent:.2f}%"
        })
    
    return pd.DataFrame(data) 