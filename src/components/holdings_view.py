import streamlit as st
import plotly.express as px
from src.services.holdings_service import (
    load_holdings,
    add_holding,
    delete_holding,
    get_holdings_data
)
from src.components.transaction_view import render_transaction_view

def render_holdings_management():
    """Render the holdings management section."""
    # Add new holding form
    st.subheader("Add New Holding")
    with st.form("add_holding_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            symbol = st.text_input("Stock Symbol").upper()
        with col2:
            price = st.number_input("Purchase Price", min_value=0.0, step=0.01)
        with col3:
            unit = st.number_input("Units", min_value=0.0, step=1.0)
        
        if st.form_submit_button("Add Holding"):
            if symbol and price > 0 and unit > 0:
                add_holding(symbol, price, unit)
                st.success(f"Added {unit} units of {symbol}")
                st.rerun()
            else:
                st.error("Please fill in all fields with valid values")
    
    # Display current holdings
    st.subheader("Current Holdings")
    holdings_data = get_holdings_data()
    
    if not holdings_data.empty:
        # Display total portfolio value
        total_value = holdings_data['Market Value'].sum()
        total_cost = holdings_data['Cost Basis'].sum()
        total_pl = holdings_data['Profit/Loss'].sum()
        total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
        with col2:
            st.metric("Total Profit/Loss", f"${total_pl:,.2f}")
        with col3:
            st.metric("Total P/L %", f"{total_pl_percent:.2f}%")
        
        # Display holdings table
        st.dataframe(holdings_data, use_container_width=True)
        
        # Plot holdings distribution
        fig = px.pie(holdings_data, values='Market Value', names='Symbol',
                    title='Portfolio Distribution by Market Value')
        st.plotly_chart(fig, use_container_width=True)
        
        # Delete holdings
        st.subheader("Delete Holdings")
        holdings = load_holdings()
        for idx, holding in enumerate(holdings):
            if st.button(f"Delete {holding['symbol']} ({holding['unit']} units)", key=f"delete_{idx}"):
                delete_holding(idx)
                st.success(f"Deleted {holding['symbol']}")
                st.rerun()
    else:
        st.info("No holdings found. Add some holdings to see them here.")

def render_holdings_view():
    """Render the holdings view with tabs."""
    # Add home navigation button
    if st.button("← Back to Home"):
        st.session_state.view = 'home'
        st.rerun()
        
    st.title("My Stock Holdings")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Current Holdings", "Transaction History"])
    
    with tab1:
        render_holdings_management()
    
    with tab2:
        render_transaction_view() 