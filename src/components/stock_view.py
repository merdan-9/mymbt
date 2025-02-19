import streamlit as st
from src.services.stock_service import StockService
from src.services.gpt_service import GPTService
from src.utils.plotting import create_stock_plot

class StockView:
    def __init__(self):
        self.stock_service = StockService()
        self.gpt_service = GPTService()

    def prepare_detailed_analysis_data(self, stock_info):
        symbol = stock_info['symbol']
        data = stock_info['data']
        
        # Get historical data for different periods
        period_data = self.stock_service.get_period_data(symbol, ['1mo', '3mo', '6mo', '1y'])
        
        # Calculate EMAs for last month
        ema_3 = data['Close'].ewm(span=3, adjust=False).mean()
        ema_5 = data['Close'].ewm(span=5, adjust=False).mean()
        ema_20 = data['Close'].ewm(span=20, adjust=False).mean()
        ema_50 = data['Close'].ewm(span=50, adjust=False).mean()
        ema_100 = data['Close'].ewm(span=100, adjust=False).mean()
        ema_200 = data['Close'].ewm(span=200, adjust=False).mean()
        
        # Calculate Moving Averages
        ma_30 = data['Close'].rolling(window=30).mean()
        ma_60 = data['Close'].rolling(window=60).mean()
        ma_120 = data['Close'].rolling(window=120).mean()
        ma_240 = data['Close'].rolling(window=240).mean()
        
        # Get last 3 months of daily closing prices with dates
        one_month_data = data.tail(30)
        closing_prices_str = "\n".join([f"            {date.strftime('%Y-%m-%d')}: ${price:.2f}" 
                                      for date, price in zip(one_month_data.index, one_month_data['Close'])])
        
        prompt = f"""Analyze the following detailed stock data for {symbol}:

          1. Current Price Data:
            - Current Price: ${stock_info['current_price']:.2f}
            - Three Month Daily Closes:
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
            - EMA100: ${ema_100.iloc[-1]:.2f}
            - EMA200: ${ema_200.iloc[-1]:.2f}
            Moving Averages:
            - MA30: ${ma_30.iloc[-1]:.2f}
            - MA60: ${ma_60.iloc[-1]:.2f}
            - MA120: ${ma_120.iloc[-1]:.2f}
            - MA240: ${ma_240.iloc[-1]:.2f}

          4. Volume Analysis:
            Current Volume vs Average: {((stock_info['data']['Volume'].iloc[-1] - stock_info['average_volume']) / stock_info['average_volume'] * 100):.1f}%
          """
        return prompt

    def display_stock_metrics(self, stock_info, controls):
        # GPT Analysis button
        get_analysis = st.button("🤖 Ask GPT Analysis", key=f"ai_{stock_info['symbol']}", type="primary", use_container_width=True)
        if get_analysis:
            prompt = self.prepare_detailed_analysis_data(stock_info)
            analysis = self.gpt_service.get_stock_analysis(prompt)
            
            # Split the analysis into sections
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

        # Display plot at the bottom
        fig = create_stock_plot(
            stock_info['data'],
            show_ema=controls.get('show_ema', False)
        )
        st.pyplot(fig, use_container_width=True)

    def display_stocks(self, filtered_results, controls):
        if not filtered_results:
            return

        tab_titles = [res['symbol'] for res in filtered_results]
        tabs = st.tabs(tab_titles)
        
        for i, stock_info in enumerate(filtered_results):
            with tabs[i]:
                symbol = stock_info['symbol']
                st.subheader(f"{symbol}")
                self.display_stock_metrics(stock_info, controls) 