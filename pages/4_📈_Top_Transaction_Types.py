import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_transaction_data

st.set_page_config(page_title="Top Transaction Types", layout="wide")
st.title("📈 Top Transaction Types Analysis")

# Load data
transactions_df = get_transaction_data()

if not transactions_df.empty:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_volume = transactions_df['amount'].sum()
        st.metric("Total Volume", f"${total_volume:,.2f}")
    
    with col2:
        avg_transaction = transactions_df['amount'].mean()
        st.metric("Average Transaction", f"${avg_transaction:,.2f}")
    
    with col3:
        total_transactions = len(transactions_df)
        st.metric("Total Transactions", f"{total_transactions:,}")
    
    with col4:
        unique_types = transactions_df['transaction_type'].nunique()
        st.metric("Unique Types", unique_types)
    
    # Top transaction types by volume
    st.subheader("Top Transaction Types by Volume")
    
    type_volume = transactions_df.groupby('transaction_type')['amount'].agg(['sum', 'count', 'mean']).reset_index()
    type_volume = type_volume.sort_values('sum', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(type_volume.head(10), x='transaction_type', y='sum', 
                     title="Top 10 Transaction Types by Volume")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.pie(type_volume.head(10), values='sum', names='transaction_type',
                     title="Volume Distribution - Top 10 Types")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed table
    st.subheader("Detailed Transaction Type Analysis")
    st.dataframe(type_volume, use_container_width=True)
else:
    st.info("No transaction data available")