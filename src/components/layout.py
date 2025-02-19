import streamlit as st

def setup_custom_style():
    st.markdown("""
    <style>
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
    """Create the main layout of the application."""
    st.title("MBT Trading")

def display_metric(label, value):
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True) 