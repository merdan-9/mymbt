import matplotlib.pyplot as plt
import pandas as pd
from .indicators import calculate_rsi, calculate_ema

def create_stock_plot(data, show_ema=True, period='1mo'):
    """Create the stock chart with indicators"""
    # Create figure and axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), height_ratios=[3, 1], gridspec_kw={'hspace': 0.3})
    
    # Calculate all indicators on full dataset first
    ema3 = calculate_ema(data, span=3)
    ema5 = calculate_ema(data, span=5)
    ema20 = calculate_ema(data, span=20)
    ema50 = calculate_ema(data, span=50)
    rsi = calculate_rsi(data, periods=14)
    
    # Calculate rolling highs and lows
    high20 = data['High'].rolling(window=20).max()
    high50 = data['High'].rolling(window=50).max()
    low10 = data['Low'].rolling(window=10).min()
    
    # Get the display period based on selected timeframe
    if period == '1mo':
        display_length = 30
    elif period == '3mo':
        display_length = 90
    elif period == '6mo':
        display_length = 180
    else:  # Default to all available data
        display_length = len(data)
        
    # Ensure we don't try to display more data than we have
    display_length = min(display_length, len(data))
    display_data = data.iloc[-display_length:]
    
    # Plot closing price for display period
    current_price = display_data['Close'].iloc[-1]
    ax1.plot(display_data.index, display_data['Close'], color='#1976D2', linewidth=1.5, 
            label=f'Close Price: ${current_price:.2f}')
    
    # Plot EMAs for display period
    ax1.plot(display_data.index, ema3.loc[display_data.index], color='#2196F3', linewidth=1.2, 
            label=f'EMA3: ${ema3.iloc[-1]:.2f}')
    ax1.plot(display_data.index, ema5.loc[display_data.index], color='#4CAF50', linewidth=1.2, 
            label=f'EMA5: ${ema5.iloc[-1]:.2f}')
    
    # Plot moving averages for display period
    ax1.plot(display_data.index, ema20.loc[display_data.index], color='#FFA726', linewidth=1.2, 
            label=f'EMA20: ${ema20.iloc[-1]:.2f}')
    ax1.plot(display_data.index, ema50.loc[display_data.index], color='#E64A19', linewidth=1.2, 
            label=f'EMA50: ${ema50.iloc[-1]:.2f}')
            
    # Plot rolling highs and lows
    ax1.plot(display_data.index, high20.loc[display_data.index], color='#FFA726', linewidth=1, linestyle='--',
            label=f'20D High: ${high20.iloc[-1]:.2f}')
    ax1.plot(display_data.index, high50.loc[display_data.index], color='#E64A19', linewidth=1, linestyle='--',
            label=f'50D High: ${high50.iloc[-1]:.2f}')
    ax1.plot(display_data.index, low10.loc[display_data.index], color='#7CB342', linewidth=1, linestyle='--',
            label=f'10D Low: ${low10.iloc[-1]:.2f}')
    
    # Plot RSI
    ax2.plot(display_data.index, rsi.loc[display_data.index], color='#5C6BC0', linewidth=1.2, 
            label=f'RSI(14): {rsi.iloc[-1]:.1f}')
    
    # Add overbought/oversold levels
    ax2.axhline(y=80, color='#FF5252', linestyle='--', alpha=0.5)
    ax2.axhline(y=50, color='#66BB6A', linestyle='--', alpha=0.5)
    ax2.fill_between(display_data.index, 80, 100, color='#FF5252', alpha=0.1)
    ax2.fill_between(display_data.index, 0, 50, color='#66BB6A', alpha=0.1)
    
    # Customize price chart
    ax1.set_title('Stock Price', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left', ncol=2)  # Use 2 columns for legend to save space
    ax1.set_ylabel('Price ($)')
    
    # Customize RSI chart
    ax2.set_title('RSI (14)', pad=10)
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')
    
    # Format dates on x-axis
    plt.gcf().autofmt_xdate()
    
    # Set background colors
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax2.set_facecolor('white')
    
    return fig 