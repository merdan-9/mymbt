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
        
        prompt = f"""Give me a detailed analysis of {symbol}"""
        return prompt

    def display_stock_metrics(self, stock_info, controls):
        # Display plot at the bottom
        fig = create_stock_plot(
            stock_info['data'],
            show_ema=controls.get('show_ema', False)
        )
        st.pyplot(fig, use_container_width=True)

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