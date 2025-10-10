import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_transaction_data

st.set_page_config(page_title="Top Transaction Types", layout="wide")
st.title(" Top Transaction Types Analysis")

# Load data
try:
    transactions_df = get_transaction_data()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    transactions_df = pd.DataFrame()

if not transactions_df.empty:
    # Ensure we have the required columns and proper data types
    if 'amount' not in transactions_df.columns:
        st.error("❌ 'amount' column not found in transaction data")
        st.stop()
    
    if 'transaction_type' not in transactions_df.columns:
        st.error("❌ 'transaction_type' column not found in transaction data")
        st.stop()
    
    # Safely convert amount to numeric
    transactions_df['amount_numeric'] = pd.to_numeric(transactions_df['amount'], errors='coerce')
    
    # Filter out invalid amounts
    valid_transactions = transactions_df[transactions_df['amount_numeric'].notna()]
    
    if valid_transactions.empty:
        st.warning(" No valid transaction amounts found")
        st.stop()
    
    # Summary metrics with safe calculations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_volume = valid_transactions['amount_numeric'].sum()
        st.metric("Total Volume", f"${total_volume:,.2f}")
    
    with col2:
        avg_transaction = valid_transactions['amount_numeric'].mean()
        st.metric("Average Transaction", f"${avg_transaction:,.2f}")
    
    with col3:
        total_transactions = len(valid_transactions)
        st.metric("Total Transactions", f"{total_transactions:,}")
    
    with col4:
        unique_types = valid_transactions['transaction_type'].nunique()
        st.metric("Unique Types", unique_types)
    
    # Top transaction types by volume
    st.subheader("Top Transaction Types by Volume")
    
    # Group by transaction type with safe aggregation
    type_volume = valid_transactions.groupby('transaction_type').agg({
        'amount_numeric': ['sum', 'count', 'mean']
    }).reset_index()
    
    # Flatten column names
    type_volume.columns = ['transaction_type', 'total_volume', 'transaction_count', 'average_amount']
    
    # Sort by total volume
    type_volume = type_volume.sort_values('total_volume', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not type_volume.empty:
            fig1 = px.bar(
                type_volume.head(10), 
                x='transaction_type', 
                y='total_volume',
                title="Top 10 Transaction Types by Volume",
                labels={'total_volume': 'Total Volume ($)', 'transaction_type': 'Transaction Type'}
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for bar chart")
    
    with col2:
        if not type_volume.empty and len(type_volume) >= 1:
            fig2 = px.pie(
                type_volume.head(10), 
                values='total_volume', 
                names='transaction_type',
                title="Volume Distribution - Top 10 Types"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data available for pie chart")
    
    # Transaction frequency analysis
    st.subheader("Transaction Frequency Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not type_volume.empty:
            fig3 = px.bar(
                type_volume.head(10).sort_values('transaction_count', ascending=False),
                x='transaction_type',
                y='transaction_count',
                title="Top 10 Transaction Types by Frequency",
                color='transaction_count',
                color_continuous_scale='viridis'
            )
            fig3.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Number of Transactions"
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        if not type_volume.empty:
            fig4 = px.scatter(
                type_volume.head(15),
                x='transaction_count',
                y='average_amount',
                size='total_volume',
                color='transaction_type',
                title="Transaction Type Analysis: Frequency vs Average Amount",
                labels={
                    'transaction_count': 'Number of Transactions',
                    'average_amount': 'Average Amount ($)',
                    'total_volume': 'Total Volume'
                },
                hover_data=['transaction_type', 'total_volume']
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    # Detailed table with formatting
    st.subheader("Detailed Transaction Type Analysis")
    
    # Format the numeric columns for display
    display_df = type_volume.copy()
    display_df['total_volume'] = display_df['total_volume'].apply(lambda x: f"${x:,.2f}")
    display_df['average_amount'] = display_df['average_amount'].apply(lambda x: f"${x:,.2f}")
    display_df['transaction_count'] = display_df['transaction_count'].apply(lambda x: f"{x:,}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Download option
    csv = type_volume.to_csv(index=False)
    st.download_button(
        label="📥 Download Transaction Type Analysis as CSV",
        data=csv,
        file_name="transaction_type_analysis.csv",
        mime="text/csv"
    )
    
else:
    st.info("No transaction data available. Please check your database connection.")