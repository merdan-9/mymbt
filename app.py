import os
import streamlit as st
from src.config import setup_page_config, apply_style
from src.data_loader import get_stock_data, load_json_file, clean_stock_data
from src.indicators import is_near_high
from src.plotting import create_stock_plot
from openai import OpenAI

# Setup page configuration and styling
setup_page_config()
apply_style()

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_gpt_analysis(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a professional stock market analyst. 
                 Provide concise, factual analysis based on the given data.
                 Format your response using markdown with clear sections:
                 - Use ### for main headings
                 - Use bullet points for lists
                 - Use bold text for important numbers and metrics
                 - Separate sections with newlines for clarity
                 - Use emojis where appropriate to enhance readability"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting GPT analysis: {str(e)}"

def calculate_technical_indicators(data, rsi_period=14, ema_period=20):
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate EMA
    ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
    
    return rsi.iloc[-1], ema.iloc[-1]

def get_period_data(symbol, periods=['1mo', '3mo', '6mo', '1y']):
    period_data = {}
    for period in periods:
        try:
            data = get_stock_data(symbol, period=period)
            if not data.empty:
                data = clean_stock_data(data)
                period_data[period] = {
                    'high': data['High'].max(),
                    'low': data['Low'].min()
                }
        except Exception:
            period_data[period] = None
    return period_data

# Sidebar controls
st.sidebar.title("Stock Control Panel")

# Load JSON files from current directory
json_files = [f for f in os.listdir() if f.endswith('.json')]

st.sidebar.subheader("Load Symbols from JSON:")
default_json_index = json_files.index("ark.json") if "ark.json" in json_files else 0
selected_json = st.sidebar.selectbox("Select JSON file", ["None"] + json_files, 
                                   index=default_json_index + 1 if "ark.json" in json_files else 0)

# User inputs
user_symbol = st.sidebar.text_input("Quick Symbol Search", "")
period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
chosen_period = st.sidebar.selectbox("Select Data Period", list(period_options.keys()))

if selected_json != "None":
    threshold = st.sidebar.slider("Price-to-High Threshold (%)", 0.0, 5.0, 1.0, 0.1)

# Technical indicators controls
st.sidebar.subheader("Technical Indicators")
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
rsi_period = st.sidebar.number_input("RSI Period", min_value=1, value=14)
show_ema = st.sidebar.checkbox("Show EMA", value=True)
ema_period = st.sidebar.number_input("EMA Period", min_value=1, value=20)

# Process symbols and display results
filtered_results = []

if user_symbol.strip():
    # If there's a Quick Symbol Search, prioritize it over JSON file search
    symbol = user_symbol.strip().upper()
    try:
        data = get_stock_data(symbol, period=period_options[chosen_period])
        if not data.empty:
            data = clean_stock_data(data)
            if not data.empty:
                filtered_results = [{  # Reset filtered_results to only contain this symbol
                    'symbol': symbol,
                    'data': data,
                    'current_price': data['Close'].iloc[-1],
                    'period_high': data['High'].max(),
                    'period_low': data['Low'].min(),
                    'average_volume': data['Volume'].mean(),
                    'diff_percent': ((data['High'].max() - data['Close'].iloc[-1]) / data['High'].max()) * 100
                }]
    except Exception as e:
        st.error(f"Error processing {symbol}: {str(e)}")

elif selected_json != "None":
    symbols = load_json_file(selected_json)
    for symbol in symbols:
        try:
            data = get_stock_data(symbol, period=period_options[chosen_period])
            if not data.empty:
                data = clean_stock_data(data)
                if not data.empty:
                    is_near, diff_percent, period_high = is_near_high(data, threshold)
                    if is_near:
                        filtered_results.append({
                            'symbol': symbol,
                            'data': data,
                            'current_price': data['Close'].iloc[-1],
                            'period_high': period_high,
                            'period_low': data['Low'].min(),
                            'average_volume': data['Volume'].mean(),
                            'diff_percent': diff_percent
                        })
        except Exception as e:
            st.error(f"Error processing {symbol}: {str(e)}")

# Display results
if filtered_results:
    tab_titles = [res['symbol'] for res in filtered_results]
    tabs = st.tabs(tab_titles)
    
    for i, stock_info in enumerate(filtered_results):
        with tabs[i]:
            symbol = stock_info['symbol']
            data = stock_info['data']
            
            # Remove the header columns and keep just the symbol header
            st.subheader(f"{symbol}")
            
            # Create two columns for metrics and chart
            col1, col2 = st.columns([1,3])
            with col1:
                # Update the metrics styling and add button styling
                st.markdown("""
                <style>
                .metric-container {
                    background-color: #f0f2f6;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 3px 0;
                }
                .metric-label {
                    color: #555;
                    font-size: 0.8em;
                }
                .metric-value {
                    color: #0e1117;
                    font-size: 1em;
                    font-weight: bold;
                }
                /* Style for Streamlit button */
                .stButton > button {
                    background-color: #FF4B4B;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    border: none;
                    font-size: 1.1em;
                    font-weight: 600;
                    width: 100%;
                    margin-top: 15px;
                }
                .stButton > button:hover {
                    background-color: #FF3333;
                    border: none;
                }
                </style>
                """, unsafe_allow_html=True)
                
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
                
                current_volume = data['Volume'].iloc[-1]
                avg_volume = stock_info['average_volume']
                volume_diff_percent = ((current_volume - avg_volume) / avg_volume) * 100
                volume_sign = "+" if volume_diff_percent > 0 else ""
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">Average Volume</div>
                    <div class="metric-value">{avg_volume:,.0f}</div>
                    <div class="metric-label">({volume_sign}{volume_diff_percent:.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">% from High</div>
                    <div class="metric-value">{stock_info['diff_percent']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Single GPT button with custom styling
                if st.button("🤖 Ask GPT Analysis", key=f"ask_gpt_{symbol}"):
                    with st.spinner(f"Analyzing {symbol}..."):
                        # Get last month's daily data
                        last_month_data = data.tail(30)
                        
                        # Calculate technical indicators
                        current_rsi, current_ema = calculate_technical_indicators(data, rsi_period, ema_period)
                        
                        # Get historical highs and lows for different periods
                        period_data = get_period_data(symbol)
                        
                        # Calculate daily changes for last month
                        daily_changes = []
                        for i in range(len(last_month_data)):
                            row = last_month_data.iloc[i]
                            daily_changes.append(f"Date: {row.name.strftime('%Y-%m-%d')}")
                            daily_changes.append(f"Open: ${row['Open']:.2f}")
                            daily_changes.append(f"High: ${row['High']:.2f}")
                            daily_changes.append(f"Low: ${row['Low']:.2f}")
                            daily_changes.append(f"Close: ${row['Close']:.2f}")
                            daily_changes.append(f"Volume: {row['Volume']:,}")
                            daily_changes.append("---")
                        
                        prompt = f"""
                        Analyze {symbol} stock and format your response using markdown:

                        Current Technical Analysis:
                        - Current Price: ${stock_info['current_price']:.2f}
                        - RSI ({rsi_period} periods): {current_rsi:.2f}
                        - EMA ({ema_period} periods): ${current_ema:.2f}
                        - Current Volume: {data['Volume'].iloc[-1]:,.0f}
                        - Average Volume: {stock_info['average_volume']:,.0f}
                        - Volume Change: {volume_diff_percent:.1f}%

                        Historical Price Ranges:
                        1 Month: High ${period_data['1mo']['high']:.2f} - Low ${period_data['1mo']['low']:.2f}
                        3 Months: High ${period_data['3mo']['high']:.2f} - Low ${period_data['3mo']['low']:.2f}
                        6 Months: High ${period_data['6mo']['high']:.2f} - Low ${period_data['6mo']['low']:.2f}
                        1 Year: High ${period_data['1y']['high']:.2f} - Low ${period_data['1y']['low']:.2f}

                        Last 30 Days Daily Data:
                        {chr(10).join(daily_changes)}

                        Provide the following sections using markdown formatting:
                        ### 📊 Company Overview
                        Brief company description and current market position

                        ### 📈 Technical Analysis
                        - Current position relative to indicators
                        - Price trend analysis
                        - Volume analysis and implications

                        ### 🎯 Key Levels
                        - Support levels
                        - Resistance levels
                        - Important price points

                        ### 💡 Trading Recommendation
                        - Entry price range
                        - Stop loss level
                        - Target profit levels
                        - Risk/reward ratio

                        ### ⚠️ Key Risks
                        List main risks to watch

                        Keep the analysis concise and focused on actionable insights.
                        """
                        analysis = get_gpt_analysis(prompt)
                        st.markdown(analysis)
            
            with col2:
                st.write("**Price Chart**")
                fig = create_stock_plot(data, show_rsi, show_ema, rsi_period, ema_period)
                st.pyplot(fig)
else:
    if selected_json != "None":
        st.info(f"No symbols found within {threshold}% of their highest price over the last {chosen_period}.")
    elif user_symbol.strip():
        st.info(f"No data found for {user_symbol.strip().upper()}")
    else:
        st.info("Please enter a symbol to search or select a JSON file.")
