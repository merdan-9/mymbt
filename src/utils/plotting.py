import matplotlib.pyplot as plt
import pandas as pd
from .indicators import calculate_rsi, calculate_ema

def create_stock_plot(data, show_ema=True):
    """Create the stock chart with indicators"""
    # Create figure and axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), height_ratios=[3, 1], gridspec_kw={'hspace': 0.3})
    
    # Calculate all indicators on full dataset first
    ema3 = calculate_ema(data, span=3)
    ema5 = calculate_ema(data, span=5)
    ma20 = data['Close'].rolling(window=20).mean()
    ma50 = data['Close'].rolling(window=50).mean()
    
    # Calculate rolling highs and lows
    high20 = data['High'].rolling(window=20).max()
    high55 = data['High'].rolling(window=55).max()
    low10 = data['Low'].rolling(window=10).min()
    
    # Get the display period (last N rows without the extra data for MA calculation)
    display_data = data.iloc[-30:]  # Default to 1 month
    if len(data) > 180:  # If we have 6mo+ data
        display_data = data.iloc[-180:]
    elif len(data) > 90:  # If we have 3mo+ data
        display_data = data.iloc[-90:]
    
    # Plot closing price for display period
    ax1.plot(display_data.index, display_data['Close'], color='#1976D2', linewidth=1.5, label='Close Price')
    
    # Plot EMAs for display period
    if show_ema:
        ax1.plot(display_data.index, ema3.loc[display_data.index], color='#2196F3', linewidth=1.2, 
                label=f'EMA3: ${ema3.iloc[-1]:.2f}')
        ax1.plot(display_data.index, ema5.loc[display_data.index], color='#4CAF50', linewidth=1.2, 
                label=f'EMA5: ${ema5.iloc[-1]:.2f}')
    
    # Plot moving averages for display period
    ax1.plot(display_data.index, ma20.loc[display_data.index], color='#FFA726', linewidth=1.2, 
            label=f'MA20: ${ma20.iloc[-1]:.2f}')
    ax1.plot(display_data.index, ma50.loc[display_data.index], color='#E64A19', linewidth=1.2, 
            label=f'MA50: ${ma50.iloc[-1]:.2f}')
            
    # Plot rolling highs and lows
    ax1.plot(display_data.index, high20.loc[display_data.index], color='#FF5252', linewidth=1, linestyle='--',
            label=f'20D High: ${high20.iloc[-1]:.2f}')
    ax1.plot(display_data.index, high55.loc[display_data.index], color='#D32F2F', linewidth=1, linestyle='--',
            label=f'55D High: ${high55.iloc[-1]:.2f}')
    ax1.plot(display_data.index, low10.loc[display_data.index], color='#7CB342', linewidth=1, linestyle='--',
            label=f'10D Low: ${low10.iloc[-1]:.2f}')
    
    # Plot volume for display period
    ax2.bar(display_data.index, display_data['Volume'], color='#90CAF9', alpha=0.5, label='Volume')
    
    # Customize price chart
    ax1.set_title('Stock Price', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left', ncol=2)  # Use 2 columns for legend to save space
    ax1.set_ylabel('Price ($)')
    
    # Customize volume chart
    ax2.set_title('Volume', pad=10)
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.set_ylabel('Volume')
    
    # Format dates on x-axis
    plt.gcf().autofmt_xdate()
    
    # Set background colors
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax2.set_facecolor('white')
    
    return fig 