import streamlit as st

def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="My MBT System",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_style():
    """Apply custom CSS styling"""
    st.markdown(
        """
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                         Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
            background-color: #FBFBFB;
            color: #1D1D1F;
            margin: 0; padding: 0;
        }
        .css-12oz5g7 {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    ) 