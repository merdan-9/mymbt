import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from .indicators import calculate_rsi, calculate_ema

def create_stock_plot(data, show_rsi=True, show_ema=True, rsi_period=14, ema_period=20):
    """Create the stock chart with indicators"""
    addplots = []
    
    if show_rsi:
        rsi = calculate_rsi(data, rsi_period)
        rsi_plot = mpf.make_addplot(rsi, panel=2, ylabel='RSI',
                                   ylim=(0, 100),
                                   secondary_y=False,
                                   color='#6236FF')
        
        overbought = pd.Series(70, index=data.index)
        oversold = pd.Series(30, index=data.index)
        ob_plot = mpf.make_addplot(overbought, panel=2, color='#FF6B6B', linestyle='--', secondary_y=False)
        os_plot = mpf.make_addplot(oversold, panel=2, color='#4CAF50', linestyle='--', secondary_y=False)
        addplots.extend([rsi_plot, ob_plot, os_plot])
    
    if show_ema:
        ema = calculate_ema(data, ema_period)
        ema_plot = mpf.make_addplot(ema, color='#2196F3')
        addplots.append(ema_plot)
    
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
        panel_ratios=(6,2,2) if show_rsi else (6,2),
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