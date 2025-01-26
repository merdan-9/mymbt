import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from .indicators import calculate_rsi, calculate_ema

def create_stock_plot(data, show_rsi=True, show_ema=True, rsi_period=14, ema_period=20):
    """Create an interactive stock plot using plotly"""
    # Calculate RSI and EMA if needed
    if show_rsi:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
    
    if show_ema:
        ema = data['Close'].ewm(span=ema_period, adjust=False).mean()

    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=3 if show_rsi else 2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2] if not show_rsi else [0.5, 0.2, 0.2],
        subplot_titles=('Price', 'Volume', 'RSI') if show_rsi else ('Price', 'Volume')
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add EMA if requested
    if show_ema:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ema,
                name=f'EMA {ema_period}',
                line=dict(color='orange')
            ),
            row=1, col=1
        )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color='rgba(100,100,100,0.5)'
        ),
        row=2, col=1
    )

    # Add RSI if requested
    if show_rsi:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=rsi,
                name='RSI',
                line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # Update layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        title_text="Interactive Stock Chart",
        template="plotly_white",
    )

    # Update y-axes labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    if show_rsi:
        fig.update_yaxes(title_text="RSI", row=3, col=1)

    return fig 