import streamlit as st
from src.services.transaction_service import get_transaction_history, get_transaction_summary

def render_transaction_view():
    """Render the transaction history view."""
    st.subheader("Transaction History")
    
    # Filters
    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            symbol_filter = st.text_input("Filter by Symbol").upper()
            transaction_type = st.selectbox(
                "Transaction Type",
                options=["All", "BUY", "SELL"]
            )
        with col2:
            start_date = st.date_input("Start Date", key="start_date")
            end_date = st.date_input("End Date", key="end_date")
    
    # Apply filters
    type_filter = transaction_type if transaction_type != "All" else None
    transactions = get_transaction_history(
        symbol=symbol_filter if symbol_filter else None,
        transaction_type=type_filter,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Display summary
    summary = get_transaction_summary()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Buys", summary["total_buys"])
    with col2:
        st.metric("Total Sells", summary["total_sells"])
    with col3:
        st.metric("Total Invested", f"${summary['total_invested']:,.2f}")
    with col4:
        st.metric("Total Returned", f"${summary['total_returned']:,.2f}")
    
    # Display transactions
    if not transactions.empty:
        st.dataframe(transactions, use_container_width=True)
    else:
        st.info("No transactions found with the current filters.") 