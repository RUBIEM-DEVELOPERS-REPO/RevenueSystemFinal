import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_analytics_tab(merged_df):
    st.header("📊 Revenue Analytics")
    
    if merged_df.empty:
        st.warning("No data available for analytics")
        return
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = merged_df['amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col2:
        avg_transaction = merged_df['amount'].mean()
        st.metric("Avg Transaction", f"${avg_transaction:,.2f}")
    
    with col3:
        total_transactions = len(merged_df)
        st.metric("Total Transactions", f"{total_transactions:,}")
    
    with col4:
        unique_categories = merged_df['category_name'].nunique()
        st.metric("Categories", unique_categories)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by category
        if 'category_name' in merged_df.columns:
            category_revenue = merged_df.groupby('category_name')['amount'].sum().reset_index()
            if not category_revenue.empty:
                fig = px.pie(category_revenue, values='amount', names='category_name', 
                           title="Revenue by Category")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly trend
        if 'transaction_date' in merged_df.columns:
            merged_df['transaction_date'] = pd.to_datetime(merged_df['transaction_date'])
            monthly_revenue = merged_df.groupby(merged_df['transaction_date'].dt.to_period('M'))['amount'].sum().reset_index()
            monthly_revenue['transaction_date'] = monthly_revenue['transaction_date'].astype(str)
            
            if not monthly_revenue.empty:
                fig = px.bar(monthly_revenue, x='transaction_date', y='amount',
                           title="Monthly Revenue Trend")
                st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Transaction Data")
    st.dataframe(merged_df[['transaction_id', 'transaction_date', 'amount', 'description', 'category_name']].head(100))