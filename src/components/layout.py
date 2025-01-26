import streamlit as st

def setup_custom_style():
    st.markdown("""
    <style>
    div.stButton > button {
        width: 200px;
        height: 120px;
        background-color: #2196F3;
        color: white;
        border-radius: 10px;
        font-size: 32px;
        font-weight: bold;
        margin: 20px auto;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #1976D2;
    }

    div.stButton {
        display: flex;
        justify-content: center;
    }

    /* Override primary button style for AI Analysis */
    div.stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        margin: 10px 0 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #ff3333 !important;
    }

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
    </style>
    """, unsafe_allow_html=True)

def create_main_layout():
    st.title("Asset Market Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        stocks_selected = st.button("STOCKS")
    with col2:
        crypto_selected = st.button("CRYPTO")
    
    return stocks_selected, crypto_selected

def display_metric(label, value):
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True) 