import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

def create_monitoring_charts(transactions_df, alerts_df):
    """
    Create monitoring charts for transaction monitoring dashboard
    """
    charts = {}
    
    try:
        # 1. Transaction Volume Over Time
        if not transactions_df.empty and 'transaction_date' in transactions_df.columns:
            transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
            daily_volume = transactions_df.groupby(transactions_df['transaction_date'].dt.date).size().reset_index()
            daily_volume.columns = ['date', 'count']
            
            fig_volume = px.line(daily_volume, x='date', y='count', 
                               title='Daily Transaction Volume',
                               labels={'date': 'Date', 'count': 'Number of Transactions'})
            fig_volume.update_traces(line=dict(color='#1f77b4', width=3))
            charts['volume_chart'] = fig_volume
        
        # 2. Transaction Amount Distribution
        if not transactions_df.empty and 'amount' in transactions_df.columns:
            fig_amount = px.histogram(transactions_df, x='amount', 
                                    title='Transaction Amount Distribution',
                                    nbins=20,
                                    labels={'amount': 'Amount'})
            fig_amount.update_traces(marker_color='#ff7f0e')
            charts['amount_chart'] = fig_amount
        
        # 3. Alerts by Severity
        if not alerts_df.empty and 'severity' in alerts_df.columns:
            alert_counts = alerts_df['severity'].value_counts().reset_index()
            alert_counts.columns = ['severity', 'count']
            
            fig_alerts = px.pie(alert_counts, values='count', names='severity',
                              title='Alerts by Severity Level')
            charts['alerts_chart'] = fig_alerts
        
        # 4. Transaction Status Distribution
        if not transactions_df.empty and 'status' in transactions_df.columns:
            status_counts = transactions_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            fig_status = px.bar(status_counts, x='status', y='count',
                              title='Transaction Status Distribution',
                              color='status')
            charts['status_chart'] = fig_status
        
        # 5. Real-time Monitoring Metrics
        if not transactions_df.empty:
            metrics_data = {
                'Total Transactions': len(transactions_df),
                'Total Amount': f"${transactions_df['amount'].sum():,.2f}" if 'amount' in transactions_df.columns else "N/A",
                'Average Amount': f"${transactions_df['amount'].mean():,.2f}" if 'amount' in transactions_df.columns else "N/A",
                'Pending Alerts': len(alerts_df[alerts_df['status'] == 'pending']) if 'status' in alerts_df.columns else len(alerts_df)
            }
            charts['metrics'] = metrics_data
            
    except Exception as e:
        st.error(f"Error creating charts: {e}")
    
    return charts

def create_revenue_charts(transactions_df):
    """
    Create comprehensive revenue analysis charts
    """
    charts = {}
    
    try:
        # Ensure transaction_date is datetime
        if 'transaction_date' in transactions_df.columns:
            transactions_df = transactions_df.copy()
            transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
            
            # 1. Daily Revenue Trend
            daily_revenue = transactions_df.groupby(transactions_df['transaction_date'].dt.date)['amount'].sum().reset_index()
            daily_revenue.columns = ['date', 'revenue']
            
            fig_trend = px.line(daily_revenue, x='date', y='revenue', 
                              title='Daily Revenue Trend',
                              labels={'date': 'Date', 'revenue': 'Revenue ($)'})
            fig_trend.update_traces(line=dict(color='#00CC96', width=3))
            charts['revenue_trend'] = fig_trend
            
            # 2. Revenue by Category
            if 'category_name' in transactions_df.columns:
                category_revenue = transactions_df.groupby('category_name')['amount'].sum().reset_index()
                category_revenue = category_revenue.sort_values('amount', ascending=False)
                
                fig_category = px.bar(category_revenue, x='category_name', y='amount',
                                    title='Revenue by Category',
                                    labels={'category_name': 'Category', 'amount': 'Revenue ($)'})
                fig_category.update_traces(marker_color='#636EFA')
                charts['revenue_by_category'] = fig_category
                
                # 3. Category Distribution Pie Chart
                fig_pie = px.pie(category_revenue, values='amount', names='category_name',
                               title='Revenue Distribution by Category')
                charts['category_pie'] = fig_pie
            
            # 4. Monthly Revenue Summary
            transactions_df['month'] = transactions_df['transaction_date'].dt.to_period('M')
            monthly_revenue = transactions_df.groupby('month')['amount'].sum().reset_index()
            monthly_revenue['month'] = monthly_revenue['month'].astype(str)
            
            fig_monthly = px.bar(monthly_revenue, x='month', y='amount',
                               title='Monthly Revenue Summary',
                               labels={'month': 'Month', 'amount': 'Revenue ($)'})
            charts['monthly_revenue'] = fig_monthly
            
            # 5. Revenue by Transaction Type
            if 'type_name' in transactions_df.columns:
                type_revenue = transactions_df.groupby('type_name')['amount'].sum().reset_index()
                type_revenue = type_revenue.sort_values('amount', ascending=False)
                
                fig_type = px.bar(type_revenue.head(10), x='type_name', y='amount',
                                title='Top 10 Revenue Sources by Type',
                                labels={'type_name': 'Transaction Type', 'amount': 'Revenue ($)'})
                charts['revenue_by_type'] = fig_type
            
            # 6. Cumulative Revenue
            daily_revenue = daily_revenue.sort_values('date')
            daily_revenue['cumulative_revenue'] = daily_revenue['revenue'].cumsum()
            
            fig_cumulative = px.line(daily_revenue, x='date', y='cumulative_revenue',
                                   title='Cumulative Revenue Over Time',
                                   labels={'date': 'Date', 'cumulative_revenue': 'Cumulative Revenue ($)'})
            fig_cumulative.update_traces(line=dict(color='#FFA15A', width=3))
            charts['cumulative_revenue'] = fig_cumulative
            
        # 7. Revenue Statistics
        stats = {
            'total_revenue': transactions_df['amount'].sum(),
            'average_transaction': transactions_df['amount'].mean(),
            'total_transactions': len(transactions_df),
            'max_transaction': transactions_df['amount'].max(),
            'min_transaction': transactions_df['amount'].min()
        }
        charts['stats'] = stats
        
    except Exception as e:
        print(f"Error creating revenue charts: {e}")
        # Return empty charts dict but with basic stats
        charts['stats'] = {
            'total_revenue': transactions_df['amount'].sum() if 'amount' in transactions_df.columns else 0,
            'average_transaction': transactions_df['amount'].mean() if 'amount' in transactions_df.columns else 0,
            'total_transactions': len(transactions_df)
        }
    
    return charts

def create_lifecycle_charts(transactions_df):
    """
    Create basic revenue lifecycle charts
    """
    charts = {}
    
    try:
        # Basic lifecycle distribution
        if 'status' in transactions_df.columns:
            status_counts = transactions_df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                       title='Revenue Lifecycle Distribution')
            charts['lifecycle_distribution'] = fig
        
        # Revenue by status
        if 'status' in transactions_df.columns and 'amount' in transactions_df.columns:
            status_revenue = transactions_df.groupby('status')['amount'].sum()
            fig2 = px.bar(x=status_revenue.index, y=status_revenue.values,
                        title='Revenue by Lifecycle Stage',
                        labels={'x': 'Status', 'y': 'Revenue'})
            charts['revenue_by_stage'] = fig2
        
        # Basic metrics
        charts['metrics'] = {
            'total_revenue': transactions_df['amount'].sum(),
            'completion_rate': (len(transactions_df[transactions_df['status'] == 'completed']) / len(transactions_df) * 100) if 'status' in transactions_df.columns else 'N/A',
            'unique_customers': transactions_df['customer_id'].nunique() if 'customer_id' in transactions_df.columns else 'N/A'
        }
        
    except Exception as e:
        print(f"Error in create_lifecycle_charts: {e}")
    
    return charts