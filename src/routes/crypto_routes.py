import streamlit as st
import plotly.graph_objects as go
from src.services.crypto_service import get_top_performing_crypto

def handle_crypto_view():
    st.title("Cryptocurrency Analysis")
    
    # Add a button to return to home
    if st.sidebar.button("Return to Home"):
        st.session_state.view = None
        st.rerun()
    
    # Period selection
    period_options = {
        "7 Days": 7,
        "15 Days": 15,
        "30 Days": 30
    }
    selected_period = st.selectbox(
        "Select Analysis Period",
        options=list(period_options.keys())
    )
    
    days = period_options[selected_period]
    
    with st.spinner("Fetching cryptocurrency data..."):
        performance_data = get_top_performing_crypto(days)
    
    if performance_data:
        st.subheader(f"Top Performing Cryptocurrencies - Last {days} Days")
        
        # Display top performers
        for idx, crypto in enumerate(performance_data[:5]):  # Show top 5
            symbol = crypto['symbol']
            price_change = crypto['price_change']
            df = crypto['data']
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{idx + 1}. {symbol}**")
                
                # Create candlestick chart
                fig = go.Figure(data=[go.Candlestick(x=df.index,
                                                    open=df['open'],
                                                    high=df['high'],
                                                    low=df['low'],
                                                    close=df['close'])])
                fig.update_layout(
                    title=f"{symbol} Price Movement",
                    yaxis_title="Price (USD)",
                    xaxis_title="Date",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric(
                    label="Price Change",
                    value=f"{price_change:.2f}%",
                    delta=f"{price_change:.2f}%"
                )
    else:
        st.error("Unable to fetch cryptocurrency data. Please try again later.") 