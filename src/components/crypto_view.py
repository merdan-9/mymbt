import streamlit as st
from src.services.crypto_service import CryptoService
from src.services.gpt_service import GPTService
from src.utils.plotting import create_stock_plot

class CryptoView:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.gpt_service = GPTService()

    def prepare_detailed_analysis_data(self, crypto_info):
        symbol = crypto_info['symbol']
        data = crypto_info['data']
        
        # Get historical data for different periods
        period_data = self.crypto_service.get_period_data(symbol)
        
        # Calculate EMAs
        ema_3 = data['Close'].ewm(span=3, adjust=False).mean()
        ema_5 = data['Close'].ewm(span=5, adjust=False).mean()
        ema_20 = data['Close'].ewm(span=20, adjust=False).mean()
        ema_50 = data['Close'].ewm(span=50, adjust=False).mean()
        
        # Get last month of daily closing prices with dates
        one_month_data = data.tail(30)
        closing_prices_str = "\n".join([f"            {date.strftime('%Y-%m-%d')}: ${price:.2f}" 
                                      for date, price in zip(one_month_data.index, one_month_data['Close'])])
        
        prompt = f"""Analyze the following detailed cryptocurrency data for {symbol}:

          1. Current Price Data:
            - Current Price: ${crypto_info['current_price']:.2f}
            - Recent Daily Closes:
      {closing_prices_str}

          2. Historical Price Ranges:
            1 Month: High ${period_data['1mo']['high']:.2f}, Low ${period_data['1mo']['low']:.2f}
            3 Months: High ${period_data['3mo']['high']:.2f}, Low ${period_data['3mo']['low']:.2f}
            6 Months: High ${period_data['6mo']['high']:.2f}, Low ${period_data['6mo']['low']:.2f}
            12 Months: High ${period_data['1y']['high']:.2f}, Low ${period_data['1y']['low']:.2f}

          3. Technical Indicators:
            EMA:
            - EMA3: ${ema_3.iloc[-1]:.2f}
            - EMA5: ${ema_5.iloc[-1]:.2f}
            - EMA20: ${ema_20.iloc[-1]:.2f}
            - EMA50: ${ema_50.iloc[-1]:.2f}

          4. Volume Analysis:
            Current Volume vs Average: {((crypto_info['data']['Volume'].iloc[-1] - crypto_info['average_volume']) / crypto_info['average_volume'] * 100):.1f}%
          """
        return prompt

    def display_crypto_metrics(self, crypto_info, controls):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            metrics = [
                ("Current Price", f"${crypto_info['current_price']:.2f}"),
                ("Period High", f"${crypto_info['period_high']:.2f}"),
                ("Period Low", f"${crypto_info['period_low']:.2f}"),
            ]
            
            for label, value in metrics:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

            current_volume = crypto_info['data']['Volume'].iloc[-1]
            avg_volume = crypto_info['average_volume']
            volume_diff_percent = ((current_volume - avg_volume) / avg_volume) * 100
            volume_sign = "+" if volume_diff_percent > 0 else ""
            
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Volume vs Avg</div>
                <div class="metric-value">{volume_sign}{volume_diff_percent:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

            # Add AI Analysis button
            get_analysis = st.button("🤖 Ask GPT Analysis", key=f"ai_{crypto_info['symbol']}", type="primary", use_container_width=True)
            if get_analysis:
                prompt = self.prepare_detailed_analysis_data(crypto_info)
                analysis = self.gpt_service.get_stock_analysis(prompt)
                
                # Split and display the analysis sections
                sections = analysis.split('\n')
                for section in sections:
                    if section.startswith('###'):
                        st.markdown(f"<h3 style='color: #1f77b4;'>{section.replace('###', '').strip()}</h3>", unsafe_allow_html=True)
                    elif section.startswith('-'):
                        item = section.replace('-', '').strip()
                        if ':' in item:
                            label, content = item.split(':', 1)
                            st.markdown(f"""
                            <div style='margin-bottom: 10px;'>
                                <span style='font-weight: bold; color: #2c3e50;'>{label}:</span>
                                <span style='color: #34495e;'>{content}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='color: #34495e; margin-left: 20px;'>{item}</div>", unsafe_allow_html=True)
                    elif section.strip():
                        st.markdown(f"<div style='color: #34495e;'>{section}</div>", unsafe_allow_html=True)

        with col2:
            fig = create_stock_plot(
                crypto_info['data'],
                show_ema=controls.get('show_ema', False)
            )
            st.pyplot(fig, use_container_width=True)
            
        return volume_diff_percent

    def display_cryptos(self, filtered_results, controls):
        if not filtered_results:
            return

        tab_titles = [res['symbol'] for res in filtered_results]
        tabs = st.tabs(tab_titles)
        
        for i, crypto_info in enumerate(filtered_results):
            with tabs[i]:
                symbol = crypto_info['symbol']
                st.subheader(f"{symbol}")
                
                volume_diff_percent = self.display_crypto_metrics(crypto_info, controls) 