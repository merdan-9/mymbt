import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from .indicators import calculate_rsi, calculate_ema

def create_stock_plot(data, show_ema=True):
    """Create the stock chart with indicators"""
    addplots = []
    
    if show_ema:
        ema3 = calculate_ema(data, span=3)
        ema5 = calculate_ema(data, span=5)
        current_ema3 = ema3.iloc[-1]
        current_ema5 = ema5.iloc[-1]
        ema3_plot = mpf.make_addplot(ema3, color='#2196F3', label=f'EMA(3): ${current_ema3:.2f}')
        ema5_plot = mpf.make_addplot(ema5, color='#4CAF50', label=f'EMA(5): ${current_ema5:.2f}')
        addplots.extend([ema3_plot, ema5_plot])
    
    # Create custom style
    mc = mpf.make_marketcolors(
        up='#42A5F5',
        down='#FFB74D',
        edge={'up': '#1E88E5', 'down': '#FFA726'},
        wick={'up': '#1E88E5', 'down': '#FFA726'},
        volume={'up': '#FFE0B2', 'down': '#BBDEFB'},
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle='',
        gridcolor='#0A192F',
        facecolor='white',
        edgecolor='white',
        figcolor='white',
        rc={
            'axes.labelcolor': '#333333',
            'xtick.color': '#333333',
            'ytick.color': '#333333',
            'axes.facecolor': 'white'
        }
    )
    
    fig, ax = mpf.plot(
        data,
        type='candle',
        style=s,
        volume=True,
        addplot=addplots if addplots else None,
        returnfig=True,
        figscale=1.8,
        datetime_format='%Y-%m-%d',
        panel_ratios=(6,2),
        tight_layout=True,
        figratio=(16,9),
        volume_panel=1,
        show_nontrading=False,
        fill_between=dict(y1=data['Low'].values, y2=data['High'].values, alpha=0.1)
    )
    
    plt.gcf().patch.set_facecolor('white')
    for ax in plt.gcf().axes:
        ax.set_facecolor('white')
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    plt.subplots_adjust(hspace=0.3)
    
    return fig 