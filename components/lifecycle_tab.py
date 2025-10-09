import streamlit as st
import pandas as pd
import numpy as np
from utils.ai_categorization import analyze_revenue_lifecycle
from utils.visualization import create_lifecycle_charts

def show_lifecycle_tab(merged_df):
    st.subheader("🔄 Revenue Lifecycle Analysis")
    
    # Perform lifecycle analysis
    lifecycle_data = analyze_revenue_lifecycle(merged_df)
    
    if not lifecycle_data:
        st.info("No transaction data available for revenue lifecycle analysis.")
        return
    
    # Display key metrics
    show_lifecycle_metrics(lifecycle_data)
    
    # Revenue distribution
    if not lifecycle_data['category_revenue'].empty:
        create_lifecycle_charts(lifecycle_data)
    
    # Revenue trends
    show_revenue_trends_analysis(lifecycle_data)
    
    # Customer analysis
    show_customer_analysis(lifecycle_data)
    
    # Recommendations
    show_lifecycle_recommendations(lifecycle_data)

def show_lifecycle_metrics(lifecycle_data):
    st.write("### 📈 Lifecycle Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${lifecycle_data['total_revenue']:,.2f}",
            "All Time"
        )
    
    with col2:
        st.metric(
            "Total Transactions",
            lifecycle_data['total_transactions'],
            "Volume"
        )
    
    with col3:
        st.metric(
            "Unique Customers",
            lifecycle_data['total_customers'],
            "Acquisition"
        )
    
    with col4:
        st.metric(
            "High Value Customers",
            lifecycle_data['high_value_customers'],
            "Retention"
        )

def show_revenue_trends_analysis(lifecycle_data):
    st.write("### 📊 Revenue Trends (Retention Analysis)")
    
    if not lifecycle_data['revenue_trend'].empty:
        # Create trend visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        
        lifecycle_data['revenue_trend'].plot(
            ax=ax,
            marker='o',
            linestyle='-',
            color='green',
            title="Daily Revenue Trend"
        )
        ax.set_ylabel('Revenue ($)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Trend analysis
        revenue_growth = lifecycle_data['revenue_trend'].pct_change().mean() * 100
        if not np.isnan(revenue_growth):
            if revenue_growth > 0:
                st.success(f"📈 Positive revenue trend: {revenue_growth:.1f}% average daily growth")
            else:
                st.warning(f"📉 Revenue trend: {revenue_growth:.1f}% average daily change")

def show_customer_analysis(lifecycle_data):
    st.write("### 👥 Customer Value Segmentation")
    
    if lifecycle_data['total_customers'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer segmentation pie chart
            segments = {
                'High Value': lifecycle_data['high_value_customers'],
                'Regular': lifecycle_data['total_customers'] - lifecycle_data['high_value_customers']
            }
            
            fig, ax = plt.subplots()
            ax.pie(
                segments.values(),
                labels=segments.keys(),
                autopct='%1.1f%%',
                colors=['#ff9999', '#66b3ff']
            )
            ax.set_title('Customer Value Segments')
            st.pyplot(fig)
        
        with col2:
            st.write("**Customer Insights**")
            if 'customer_metrics' in lifecycle_data:
                avg_transactions = lifecycle_data['customer_metrics'][('amount', 'count')].mean()
                avg_spend = lifecycle_data['customer_metrics'][('amount', 'mean')].mean()
                
                st.metric("Avg Transactions per Customer", f"{avg_transactions:.1f}")
                st.metric("Avg Spend per Transaction", f"${avg_spend:.2f}")
                st.metric("High Value Customer %", 
                        f"{(lifecycle_data['high_value_customers'] / lifecycle_data['total_customers']) * 100:.1f}%")
        
        # Customer journey analysis
        show_customer_journey_analysis()

def show_customer_journey_analysis():
    # This would integrate with your customer journey analysis code
    st.write("### 🧭 Customer Journey Analysis")
    st.info("Customer journey analysis features will be implemented here")

def show_lifecycle_recommendations(lifecycle_data):
    st.write("### 🎯 Lifecycle Optimization Recommendations")
    
    recommendations = generate_recommendations(lifecycle_data)
    
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("✅ Good balance across revenue lifecycle stages!")

def generate_recommendations(lifecycle_data):
    recommendations = []
    
    # Acquisition recommendations
    if lifecycle_data['total_customers'] < 50:
        recommendations.append("🚀 **Acquisition**: Focus on customer acquisition - current customer base is small")
    
    # Retention recommendations
    if lifecycle_data.get('avg_daily_transactions', 0) < 10:
        recommendations.append("📊 **Retention**: Low transaction frequency - consider loyalty programs")
    
    # Revenue optimization
    if lifecycle_data['total_customers'] > 0 and lifecycle_data['high_value_customers'] / lifecycle_data['total_customers'] < 0.2:
        recommendations.append("💰 **Revenue**: Low percentage of high-value customers - focus on upselling")
    
    # Category optimization
    if not lifecycle_data['category_revenue'].empty:
        top_category = lifecycle_data['category_revenue'].index[0]
        top_revenue_share = lifecycle_data['category_revenue'].iloc[0] / lifecycle_data['total_revenue']
        if top_revenue_share > 0.5:
            recommendations.append(f"📈 **Diversification**: {top_category} dominates revenue ({top_revenue_share:.1%}) - diversify income streams")
    
    return recommendations

    import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from utils.ai_categorization import analyze_revenue_lifecycle

def show_lifecycle_tab(merged_df):
    """Display revenue lifecycle analysis tab"""
    
    st.subheader("🔄 Revenue Lifecycle Analysis")
    
    # Perform lifecycle analysis
    lifecycle_data = analyze_revenue_lifecycle(merged_df)
    
    if not lifecycle_data:
        st.info("No transaction data available for revenue lifecycle analysis.")
        return
    
    # Display key metrics
    show_lifecycle_metrics(lifecycle_data)
    
    # Revenue distribution
    if not lifecycle_data['category_revenue'].empty:
        create_lifecycle_charts(lifecycle_data)
    
    # Revenue trends
    show_revenue_trends_analysis(lifecycle_data)
    
    # Customer analysis
    show_customer_analysis(lifecycle_data)
    
    # Recommendations
    show_lifecycle_recommendations(lifecycle_data)
    
    # Customer journey analysis
    show_customer_journey_analysis(merged_df)

def show_lifecycle_metrics(lifecycle_data):
    """Display lifecycle key metrics"""
    
    st.write("### 📈 Lifecycle Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${lifecycle_data['total_revenue']:,.2f}",
            "All Time"
        )
    
    with col2:
        st.metric(
            "Total Transactions",
            lifecycle_data['total_transactions'],
            "Volume"
        )
    
    with col3:
        st.metric(
            "Unique Customers",
            lifecycle_data['total_customers'],
            "Acquisition"
        )
    
    with col4:
        st.metric(
            "High Value Customers",
            lifecycle_data['high_value_customers'],
            "Retention"
        )

def create_lifecycle_charts(lifecycle_data):
    """Create lifecycle analysis charts"""
    
    st.write("### 💰 Revenue by Category (Lifecycle Stage Proxy)")
    
    if not lifecycle_data['category_revenue'].empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart using Plotly
            fig_pie = px.pie(
                values=lifecycle_data['category_revenue'].values,
                names=lifecycle_data['category_revenue'].index,
                title="Revenue Distribution by Category"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart using Plotly
            fig_bar = px.bar(
                x=lifecycle_data['category_revenue'].index,
                y=lifecycle_data['category_revenue'].values,
                title="Revenue by Category",
                labels={'x': 'Category', 'y': 'Revenue ($)'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

def show_revenue_trends_analysis(lifecycle_data):
    """Display revenue trends analysis"""
    
    st.write("### 📊 Revenue Trends (Retention Analysis)")
    
    if not lifecycle_data['revenue_trend'].empty:
        # Create interactive trend chart
        trend_df = lifecycle_data['revenue_trend'].reset_index()
        trend_df.columns = ['date', 'revenue']
        
        fig = px.line(
            trend_df,
            x='date',
            y='revenue',
            title="Daily Revenue Trend",
            labels={'revenue': 'Revenue ($)', 'date': 'Date'}
        )
        fig.update_traces(mode='lines+markers', line=dict(color='green'))
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis
        revenue_growth = lifecycle_data['revenue_trend'].pct_change().mean() * 100
        if not np.isnan(revenue_growth):
            if revenue_growth > 0:
                st.success(f"📈 Positive revenue trend: {revenue_growth:.1f}% average daily growth")
            else:
                st.warning(f"📉 Revenue trend: {revenue_growth:.1f}% average daily change")

def show_customer_analysis(lifecycle_data):
    """Display customer value analysis"""
    
    st.write("### 👥 Customer Value Segmentation")
    
    if lifecycle_data['total_customers'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer segmentation pie chart
            segments = {
                'High Value': lifecycle_data['high_value_customers'],
                'Regular': lifecycle_data['total_customers'] - lifecycle_data['high_value_customers']
            }
            
            fig = px.pie(
                values=list(segments.values()),
                names=list(segments.keys()),
                title="Customer Value Segments",
                color_discrete_sequence=['#ff9999', '#66b3ff']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Customer Insights**")
            if 'customer_metrics' in lifecycle_data:
                avg_transactions = lifecycle_data['customer_metrics'][('amount', 'count')].mean()
                avg_spend = lifecycle_data['customer_metrics'][('amount', 'mean')].mean()
                
                st.metric("Avg Transactions per Customer", f"{avg_transactions:.1f}")
                st.metric("Avg Spend per Transaction", f"${avg_spend:.2f}")
                st.metric("High Value Customer %", 
                        f"{(lifecycle_data['high_value_customers'] / lifecycle_data['total_customers']) * 100:.1f}%")

def show_lifecycle_recommendations(lifecycle_data):
    """Generate and display lifecycle recommendations"""
    
    st.write("### 🎯 Lifecycle Optimization Recommendations")
    
    recommendations = generate_recommendations(lifecycle_data)
    
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("✅ Good balance across revenue lifecycle stages!")

def generate_recommendations(lifecycle_data):
    """Generate lifecycle optimization recommendations"""
    
    recommendations = []
    
    # Acquisition recommendations
    if lifecycle_data['total_customers'] < 50:
        recommendations.append("🚀 **Acquisition**: Focus on customer acquisition - current customer base is small")
    
    # Retention recommendations
    if lifecycle_data.get('avg_daily_transactions', 0) < 10:
        recommendations.append("📊 **Retention**: Low transaction frequency - consider loyalty programs")
    
    # Revenue optimization
    if lifecycle_data['total_customers'] > 0 and lifecycle_data['high_value_customers'] / lifecycle_data['total_customers'] < 0.2:
        recommendations.append("💰 **Revenue**: Low percentage of high-value customers - focus on upselling")
    
    # Category optimization
    if not lifecycle_data['category_revenue'].empty:
        top_category = lifecycle_data['category_revenue'].index[0]
        top_revenue_share = lifecycle_data['category_revenue'].iloc[0] / lifecycle_data['total_revenue']
        if top_revenue_share > 0.5:
            recommendations.append(f"📈 **Diversification**: {top_category} dominates revenue ({top_revenue_share:.1%}) - diversify income streams")
    
    return recommendations

def show_customer_journey_analysis(merged_df):
    """Display customer journey analysis"""
    
    if 'customer_id' in merged_df.columns and 'created_at' in merged_df.columns:
        st.subheader("🧭 Customer Journey Analysis")
        
        # Select a customer to analyze
        customer_options = merged_df['customer_id'].unique()
        if len(customer_options) > 0:
            selected_customer = st.selectbox("Select Customer to Analyze Journey", customer_options[:10])
            
            customer_data = merged_df[merged_df['customer_id'] == selected_customer].sort_values('created_at')
            
            if not customer_data.empty:
                st.write(f"**Customer {selected_customer} Journey**")
                
                # Journey timeline
                journey_events = []
                for idx, row in customer_data.iterrows():
                    event = {
                        'date': row['created_at'],
                        'category': row.get('category_name', 'Unknown'),
                        'amount': row.get('amount', 0),
                        'type': row.get('transaction_type_name', 'Unknown')
                    }
                    journey_events.append(event)
                
                # Display journey summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("First Transaction", customer_data['created_at'].min().strftime('%Y-%m-%d'))
                with col2:
                    st.metric("Total Transactions", len(customer_data))
                with col3:
                    st.metric("Total Spent", f"${customer_data['amount'].sum():.2f}")
                
                # Journey visualization
                st.write("**Transaction Timeline**")
                journey_df = pd.DataFrame(journey_events)
                st.dataframe(journey_df, use_container_width=True)