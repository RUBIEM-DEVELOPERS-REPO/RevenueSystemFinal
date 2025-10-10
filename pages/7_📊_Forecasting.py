import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_transaction_data

st.set_page_config(page_title="Revenue Forecasting", layout="wide")
st.title("Revenue Forecasting & Analysis")

# Load data
try:
    transactions_df = get_transaction_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    transactions_df = pd.DataFrame()

def safe_convert_to_float(value):
    """Safely convert any value to float"""
    try:
        if value is None or pd.isna(value) or value == '':
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace('$', '').replace(',', '').strip()
            return float(cleaned) if cleaned else 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

if not transactions_df.empty:
    # Convert and prepare data safely
    try:
        transactions_df['date'] = pd.to_datetime(transactions_df['created_at'], errors='coerce').dt.date
        transactions_df['amount_numeric'] = transactions_df['amount'].apply(safe_convert_to_float)
        
        # Filter out invalid dates and amounts
        valid_data = transactions_df[
            transactions_df['date'].notna() & 
            transactions_df['amount_numeric'].notna() & 
            (transactions_df['amount_numeric'] > 0)
        ]
        
        if valid_data.empty:
            st.warning("No valid transaction data with dates and amounts available")
            st.stop()
        
        # Group by date
        daily_revenue = valid_data.groupby('date')['amount_numeric'].sum().sort_index()
        
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.stop()
    
    # Current Performance Analysis
    st.header("Current Performance Analysis")
    
    # Key metrics for the day
    today_revenue = daily_revenue.iloc[-1] if len(daily_revenue) > 0 else 0
    today_date = daily_revenue.index[-1] if len(daily_revenue) > 0 else "N/A"
    total_transactions = len(valid_data[valid_data['date'] == daily_revenue.index[-1]]) if len(daily_revenue) > 0 else 0
    avg_transaction = today_revenue / total_transactions if total_transactions > 0 else 0
    
    # Currency Performance Analysis
    st.subheader("Currency Performance Analysis")
    
    if 'currency' in transactions_df.columns:
        # Currency distribution analysis
        currency_performance = valid_data.groupby('currency').agg({
            'amount_numeric': ['sum', 'count', 'mean'],
            'date': 'nunique'
        }).round(2)
        
        # Flatten column names
        currency_performance.columns = ['Total Revenue', 'Transaction Count', 'Average Amount', 'Days Active']
        
        # Calculate percentage of total revenue
        total_all_currencies = currency_performance['Total Revenue'].sum()
        currency_performance['Revenue Share'] = (currency_performance['Total Revenue'] / total_all_currencies * 100).round(1)
        
        # Display currency performance table
        st.write("**Currency Performance Summary**")
        
        # Create formatted display table
        display_currency = currency_performance.copy()
        display_currency['Total Revenue'] = display_currency['Total Revenue'].apply(lambda x: f"{x:,.2f}")
        display_currency['Average Amount'] = display_currency['Average Amount'].apply(lambda x: f"{x:,.2f}")
        display_currency['Revenue Share'] = display_currency['Revenue Share'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            display_currency,
            use_container_width=True,
            column_config={
                "Total Revenue": st.column_config.TextColumn("Total Revenue"),
                "Transaction Count": st.column_config.NumberColumn("Transactions"),
                "Average Amount": st.column_config.TextColumn("Avg Amount"),
                "Days Active": st.column_config.NumberColumn("Active Days"),
                "Revenue Share": st.column_config.TextColumn("Revenue Share")
            }
        )
        
        # Currency visualization
        st.write("**Currency Distribution**")
        
        # Create visualization
        fig_currency = go.Figure()
        
        # Bar chart for revenue by currency
        fig_currency.add_trace(go.Bar(
            x=currency_performance.index,
            y=currency_performance['Total Revenue'],
            name='Total Revenue',
            marker_color='#1f77b4',
            text=currency_performance['Total Revenue'].apply(lambda x: f"{x:,.0f}"),
            textposition='auto'
        ))
        
        fig_currency.update_layout(
            title="Revenue Distribution by Currency",
            xaxis_title="Currency",
            yaxis_title="Revenue Amount",
            plot_bgcolor='white',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_currency, use_container_width=True)
    
    else:
        st.info("Currency data not available in transaction records")
    
    # Revenue Performance Analysis
    st.subheader("Revenue Performance Analysis")
    
    # Create comprehensive revenue performance table
    revenue_metrics = []
    
    # Basic revenue metrics
    revenue_metrics.append({
        'Metric': 'Total Revenue',
        'Value': f"{today_revenue:,.2f}",
        'Description': 'Sum of all valid transactions',
        'Status': 'High' if today_revenue > 1000 else 'Medium' if today_revenue > 500 else 'Low'
    })
    
    revenue_metrics.append({
        'Metric': 'Transaction Volume',
        'Value': f"{total_transactions:,}",
        'Description': 'Number of completed transactions',
        'Status': 'High' if total_transactions > 50 else 'Medium' if total_transactions > 20 else 'Low'
    })
    
    revenue_metrics.append({
        'Metric': 'Average Transaction Value',
        'Value': f"{avg_transaction:,.2f}",
        'Description': 'Mean value per transaction',
        'Status': 'High' if avg_transaction > 100 else 'Medium' if avg_transaction > 50 else 'Low'
    })
    
    # Additional performance metrics
    if len(daily_revenue) > 1:
        # Calculate growth metrics
        previous_revenue = daily_revenue.iloc[-2] if len(daily_revenue) > 1 else 0
        daily_growth = ((today_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        
        revenue_metrics.append({
            'Metric': 'Daily Growth Rate',
            'Value': f"{daily_growth:+.1f}%",
            'Description': 'Change from previous day',
            'Status': 'High' if daily_growth > 10 else 'Medium' if daily_growth > 0 else 'Low'
        })
    
    # Transaction efficiency metrics
    if 'transaction_type_name' in valid_data.columns:
        unique_types = valid_data['transaction_type_name'].nunique()
        revenue_metrics.append({
            'Metric': 'Product Diversity',
            'Value': f"{unique_types} types",
            'Description': 'Number of transaction categories',
            'Status': 'High' if unique_types > 5 else 'Medium' if unique_types > 2 else 'Low'
        })
    
    # Convert to DataFrame
    revenue_df = pd.DataFrame(revenue_metrics)
    
    # Display revenue performance table
    st.write("**Revenue Performance Metrics**")
    
    # Color coding for status
    def color_status(status):
        if status == 'High':
            return 'background-color: #d4edda; color: #155724;'
        elif status == 'Medium':
            return 'background-color: #fff3cd; color: #856404;'
        else:
            return 'background-color: #f8d7da; color: #721c24;'
    
    styled_df = revenue_df.style.apply(
        lambda x: [color_status(x['Status']) for _ in x], 
        axis=1,
        subset=['Metric', 'Value', 'Description', 'Status']
    )
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("Performance Metric"),
            "Value": st.column_config.TextColumn("Current Value"),
            "Description": st.column_config.TextColumn("Metric Description"),
            "Status": st.column_config.TextColumn("Performance Level")
        }
    )
    
    # Revenue performance visualization
    st.write("**Revenue Performance Visualization**")
    
    # Create performance gauge chart
    performance_score = min(100, (today_revenue / 2000) * 100) if today_revenue > 0 else 0  # Scale based on 2000 target
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = performance_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Revenue Performance Score"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Revenue Overview
    st.subheader("Revenue Overview")
    
    if len(daily_revenue) == 1:
        # Single day visualization
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode = "number",
            value = today_revenue,
            number = {'valueformat': ",.0f"},
            title = {"text": "Total Revenue"},
            domain = {'row': 0, 'column': 0}
        ))
        
        fig.update_layout(
            grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
            height = 200,
            paper_bgcolor = 'lightgray'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Transaction breakdown
        st.subheader("Transaction Breakdown")
        
        # By transaction type
        if 'transaction_type_name' in valid_data.columns:
            today_data = valid_data[valid_data['date'] == daily_revenue.index[-1]]
            type_breakdown = today_data.groupby('transaction_type_name')['amount_numeric'].agg(['sum', 'count']).reset_index()
            type_breakdown.columns = ['Transaction Type', 'Total Amount', 'Count']
            
            # Amount by type
            fig_amount = px.bar(
                type_breakdown,
                x='Transaction Type',
                y='Total Amount',
                title="Revenue Distribution by Transaction Type",
                color='Total Amount',
                color_continuous_scale='blues'
            )
            fig_amount.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_amount, use_container_width=True)
            
            # Count by type
            fig_count = px.pie(
                type_breakdown,
                values='Count',
                names='Transaction Type',
                title="Transaction Volume Distribution",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig_count, use_container_width=True)
    
    else:
        # Multiple days available
        st.subheader("Revenue Trend Analysis")
        
        # Show last 7 days if available, otherwise all available days
        recent_days = daily_revenue.tail(min(7, len(daily_revenue)))
        
        fig_trend = px.line(
            x=recent_days.index,
            y=recent_days.values,
            title="Revenue Trend - Last 7 Days",
            labels={'x': 'Date', 'y': 'Revenue Amount'},
            markers=True,
            color_discrete_sequence=['#1f77b4']
        )
        fig_trend.update_layout(
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Revenue Projections
    st.header("Revenue Projections")
    
    st.write("Based on current performance, here are potential revenue projections:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Weekly projection
        weekly_proj = today_revenue * 7
        st.metric("Weekly Projection", f"{weekly_proj:,.2f}")
        st.caption("Based on current daily performance")
    
    with col2:
        # Monthly projection
        monthly_proj = today_revenue * 30
        st.metric("Monthly Projection", f"{monthly_proj:,.2f}")
        st.caption("30-day extrapolation")
    
    with col3:
        # Annual projection
        annual_proj = today_revenue * 365
        st.metric("Annual Projection", f"{annual_proj:,.2f}")
        st.caption("Full year estimate")

else:
    st.info("No transaction data available. Please check your database connection.")

# Performance Insights
with st.expander("Performance Insights"):
    if not transactions_df.empty and len(daily_revenue) > 0:
        today_data = valid_data[valid_data['date'] == daily_revenue.index[-1]]
        
        insights = []
        
        # Revenue insight
        if today_revenue > 1000:
            insights.append("Strong Revenue Performance: Current revenue exceeds 1000 threshold")
        elif today_revenue < 100:
            insights.append("Revenue Optimization Opportunity: Consider promotional activities to boost performance")
        
        # Transaction volume insight
        if total_transactions > 50:
            insights.append("High Transaction Volume: Strong customer engagement levels")
        elif total_transactions < 10:
            insights.append("Growth Opportunity: Focus on customer acquisition strategies")
        
        # Average transaction insight
        if avg_transaction > 100:
            insights.append("Premium Transaction Value: High average transaction indicates quality customer base")
        elif avg_transaction < 20:
            insights.append("Upsell Potential: Low average transaction value suggests bundle or cross-sell opportunities")
        
        if insights:
            st.subheader("Key Observations")
            for insight in insights:
                st.success(insight)
        else:
            st.info("Current performance metrics are within expected ranges")