import streamlit as st
from src.services.stock_service import StockService
from src.services.gpt_service import GPTService
from src.utils.plotting import create_stock_plot

class StockView:
    def __init__(self):
        self.stock_service = StockService()
        self.gpt_service = GPTService()

    def display_stock_metrics(self, stock_info, controls):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            metrics = [
                ("Current Price", f"${stock_info['current_price']:.2f}"),
                ("Period High", f"${stock_info['period_high']:.2f}"),
                ("Period Low", f"${stock_info['period_low']:.2f}"),
            ]
            
            for label, value in metrics:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

            current_volume = stock_info['data']['Volume'].iloc[-1]
            avg_volume = stock_info['average_volume']
            volume_diff_percent = ((current_volume - avg_volume) / avg_volume) * 100
            volume_sign = "+" if volume_diff_percent > 0 else ""
            
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Volume vs Avg</div>
                <div class="metric-value">{volume_sign}{volume_diff_percent:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

            # Add AI Analysis button and display here
            get_analysis = st.button("🤖 Ask GPT Analysis", key=f"ai_{stock_info['symbol']}", type="primary", use_container_width=True)
            if get_analysis:
                prompt = f"""Analyze the following stock data for {stock_info['symbol']}:
                Current Price: ${stock_info['current_price']:.2f}
                Period High: ${stock_info['period_high']:.2f}
                Period Low: ${stock_info['period_low']:.2f}
                Distance from High: {stock_info['diff_percent']:.2f}%
                Volume Change: {volume_diff_percent:.1f}%
                """
                
                analysis = self.gpt_service.get_stock_analysis(prompt)
                st.markdown(analysis)

        with col2:
            fig = create_stock_plot(
                stock_info['data'],
                show_ema=controls.get('show_ema', False)
            )
            st.pyplot(fig, use_container_width=True)
            
        return volume_diff_percent

    def display_stocks(self, filtered_results, controls):
        if not filtered_results:
            return

        tab_titles = [res['symbol'] for res in filtered_results]
        tabs = st.tabs(tab_titles)
        
        for i, stock_info in enumerate(filtered_results):
            with tabs[i]:
                symbol = stock_info['symbol']
                st.subheader(f"{symbol}")
                
                volume_diff_percent = self.display_stock_metrics(stock_info, controls) 