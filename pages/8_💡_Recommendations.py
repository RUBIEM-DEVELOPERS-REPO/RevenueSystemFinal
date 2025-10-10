import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_transaction_data

st.set_page_config(page_title="Recommendations", layout="wide")
st.title("Data-Driven Recommendations")

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

def generate_data_driven_insights(df):
    """Generate insights based on available transaction data"""
    insights = {
        'revenue_streams': [],
        'key_insights': [],
        'optimization_recommendations': [],
        'data_quality_notes': []
    }
    
    # Safely convert amounts
    df['amount_numeric'] = df['amount'].apply(safe_convert_to_float)
    valid_data = df[df['amount_numeric'] > 0]
    
    if valid_data.empty:
        insights['key_insights'].append("No valid transaction amounts found for analysis")
        return insights
    
    # Basic revenue analysis
    total_revenue = valid_data['amount_numeric'].sum()
    total_transactions = len(valid_data)
    avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Revenue stream analysis by transaction type
    if 'transaction_type_name' in df.columns:
        revenue_by_type = valid_data.groupby('transaction_type_name')['amount_numeric'].agg(['sum', 'count']).reset_index()
        revenue_by_type['percentage'] = (revenue_by_type['sum'] / total_revenue * 100).round(1)
        
        for _, row in revenue_by_type.iterrows():
            insights['revenue_streams'].append({
                'stream_name': row['transaction_type_name'],
                'revenue_amount': row['sum'],
                'transaction_count': row['count'],
                'contribution_percentage': row['percentage'],
                'avg_transaction_size': row['sum'] / row['count'] if row['count'] > 0 else 0
            })
    
    # Key insights
    insights['key_insights'].append(f"Total revenue analyzed: ${total_revenue:,.2f}")
    insights['key_insights'].append(f"Average transaction value: ${avg_transaction:,.2f}")
    insights['key_insights'].append(f"Total transactions processed: {total_transactions:,}")
    
    if avg_transaction < 50:
        insights['key_insights'].append("Low average transaction value - consider upselling strategies")
    elif avg_transaction > 200:
        insights['key_insights'].append("High average transaction value - focus on customer retention")
    
    # Optimization recommendations
    if total_transactions < 100:
        insights['optimization_recommendations'].append({
            'recommendation': "Increase transaction volume through marketing campaigns",
            'confidence': 85,
            'expected_impact': "Medium",
            'implementation_complexity': "Low"
        })
    
    if len(insights['revenue_streams']) > 0:
        top_stream = max(insights['revenue_streams'], key=lambda x: x['contribution_percentage'])
        if top_stream['contribution_percentage'] > 60:
            insights['optimization_recommendations'].append({
                'recommendation': f"Diversify revenue streams - {top_stream['stream_name']} dominates at {top_stream['contribution_percentage']}%",
                'confidence': 75,
                'expected_impact': "High",
                'implementation_complexity': "Medium"
            })
    
    # Time-based recommendations
    if 'created_at' in df.columns:
        try:
            df['hour'] = pd.to_datetime(df['created_at']).dt.hour
            hourly_volume = df['hour'].value_counts()
            if len(hourly_volume) > 0:
                peak_hour = hourly_volume.idxmax()
                insights['optimization_recommendations'].append({
                    'recommendation': f"Peak activity at {peak_hour}:00 - optimize resources during this hour",
                    'confidence': 90,
                    'expected_impact': "Medium",
                    'implementation_complexity': "Low"
                })
        except:
            pass
    
    # Data quality notes
    if len(df) != len(valid_data):
        insights['data_quality_notes'].append(f"{(len(df) - len(valid_data))} transactions had invalid amounts")
    
    return insights

if not transactions_df.empty:
    st.subheader("Automated Business Insights")
    
    if st.button("Generate Data-Driven Recommendations", type="primary"):
        with st.spinner("Analyzing your transaction data for insights..."):
            insights = generate_data_driven_insights(transactions_df)
            
            st.success("Analysis Complete!")
            
            # Revenue Streams
            if insights['revenue_streams']:
                st.subheader("Revenue Stream Analysis")
                
                # Create visualization
                revenue_df = pd.DataFrame(insights['revenue_streams'])
                if not revenue_df.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.pie(
                            revenue_df,
                            values='contribution_percentage',
                            names='stream_name',
                            title="Revenue Distribution by Transaction Type"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig2 = px.bar(
                            revenue_df,
                            x='stream_name',
                            y='avg_transaction_size',
                            title="Average Transaction Size by Type",
                            color='avg_transaction_size'
                        )
                        fig2.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Detailed breakdown
                for stream in insights['revenue_streams']:
                    with st.expander(f"{stream['stream_name']} - {stream['contribution_percentage']}% of revenue"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Revenue", f"${stream['revenue_amount']:,.2f}")
                        with col2:
                            st.metric("Transaction Count", f"{stream['transaction_count']:,}")
                        with col3:
                            st.metric("Avg Size", f"${stream['avg_transaction_size']:,.2f}")
            
            # Key Insights
            if insights['key_insights']:
                st.subheader("Key Insights")
                for i, insight in enumerate(insights['key_insights'], 1):
                    st.info(f"{i}. {insight}")
            
            # Optimization Recommendations
            if insights['optimization_recommendations']:
                st.subheader("Optimization Recommendations")
                for i, rec in enumerate(insights['optimization_recommendations'], 1):
                    confidence_color = "High" if rec.get('confidence', 0) > 80 else "Medium" if rec.get('confidence', 0) > 60 else "Low"
                    
                    with st.expander(f"Recommendation {i}: {rec.get('recommendation', '')}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Confidence", f"{rec.get('confidence', 0)}%")
                        with col2:
                            st.metric("Expected Impact", rec.get('expected_impact', 'Unknown'))
                        with col3:
                            st.metric("Implementation", rec.get('implementation_complexity', 'Unknown'))
            
            # Data Quality Notes
            if insights['data_quality_notes']:
                st.subheader("Data Quality Notes")
                for note in insights['data_quality_notes']:
                    st.warning(note)
    
    # Quick Data Overview Section
    st.subheader("Quick Data Overview")
    
    # Create a comprehensive data summary table
    transactions_df['amount_numeric'] = transactions_df['amount'].apply(safe_convert_to_float)
    valid_data = transactions_df[transactions_df['amount_numeric'] > 0]
    
    if not valid_data.empty:
        # Create summary statistics table
        summary_data = []
        
        # Basic metrics
        total_revenue = valid_data['amount_numeric'].sum()
        total_transactions = len(valid_data)
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        max_transaction = valid_data['amount_numeric'].max()
        min_transaction = valid_data['amount_numeric'].min()
        
        summary_data.append({
            'Metric': 'Total Revenue',
            'Value': f"${total_revenue:,.2f}",
            'Explanation': 'Sum of all valid transaction amounts'
        })
        
        summary_data.append({
            'Metric': 'Total Transactions',
            'Value': f"{total_transactions:,}",
            'Explanation': 'Number of transactions with valid amounts'
        })
        
        summary_data.append({
            'Metric': 'Average Transaction',
            'Value': f"${avg_transaction:,.2f}",
            'Explanation': 'Mean value per transaction'
        })
        
        summary_data.append({
            'Metric': 'Largest Transaction',
            'Value': f"${max_transaction:,.2f}",
            'Explanation': 'Highest single transaction amount'
        })
        
        summary_data.append({
            'Metric': 'Smallest Transaction',
            'Value': f"${min_transaction:,.2f}",
            'Explanation': 'Lowest single transaction amount'
        })
        
        # Transaction type metrics
        if 'transaction_type_name' in valid_data.columns:
            unique_types = valid_data['transaction_type_name'].nunique()
            summary_data.append({
                'Metric': 'Transaction Types',
                'Value': unique_types,
                'Explanation': 'Number of distinct transaction categories'
            })
            
            # Most common type
            common_type = valid_data['transaction_type_name'].mode()
            if not common_type.empty:
                summary_data.append({
                    'Metric': 'Most Common Type',
                    'Value': common_type.iloc[0],
                    'Explanation': 'Most frequent transaction category'
                })
        
        # Date range metrics
        if 'created_at' in valid_data.columns:
            try:
                valid_data['date'] = pd.to_datetime(valid_data['created_at']).dt.date
                date_range = f"{valid_data['date'].min()} to {valid_data['date'].max()}"
                days_covered = (valid_data['date'].max() - valid_data['date'].min()).days + 1
                
                summary_data.append({
                    'Metric': 'Date Range',
                    'Value': date_range,
                    'Explanation': 'Period covered by transaction data'
                })
                
                summary_data.append({
                    'Metric': 'Days Covered',
                    'Value': days_covered,
                    'Explanation': 'Number of days in the analysis period'
                })
            except:
                pass
        
        # Data quality metrics
        invalid_count = len(transactions_df) - len(valid_data)
        data_quality_pct = (len(valid_data) / len(transactions_df) * 100) if len(transactions_df) > 0 else 0
        
        summary_data.append({
            'Metric': 'Data Quality',
            'Value': f"{data_quality_pct:.1f}%",
            'Explanation': f"Percentage of valid transactions ({invalid_count} invalid records)"
        })
        
        # Convert to DataFrame and display
        summary_df = pd.DataFrame(summary_data)
        
        # Display the table with custom styling
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Metric": st.column_config.TextColumn("Metric", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="small"),
                "Explanation": st.column_config.TextColumn("Explanation", width="large")
            }
        )
        
        # Data Interpretation Section
        st.subheader("Data Interpretation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Performance Indicators:**")
            if avg_transaction < 30:
                st.write("- Low average transaction value suggests upselling opportunities")
            elif avg_transaction > 100:
                st.write("- High average value indicates premium customer base")
            
            if total_transactions < 50:
                st.write("- Low transaction volume - focus on customer acquisition")
            elif total_transactions > 1000:
                st.write("- High volume business - optimize operational efficiency")
        
        with col2:
            st.write("**Data Quality Assessment:**")
            if data_quality_pct > 95:
                st.write("- Excellent data quality")
            elif data_quality_pct > 80:
                st.write("- Good data quality")
            else:
                st.write("- Data quality needs improvement")
            
            if 'transaction_type_name' in valid_data.columns:
                if unique_types == 1:
                    st.write("- Single transaction type - consider diversification")
                elif unique_types > 5:
                    st.write("- Diverse transaction portfolio")
        
        # Immediate recommendations based on quick analysis
        st.subheader("Immediate Opportunities")
        
        quick_recs = []
        
        if avg_transaction < 30:
            quick_recs.append("Upsell Opportunity: Low average transaction value - implement bundle offers")
        
        if total_transactions < 50:
            quick_recs.append("Growth Focus: Low transaction volume - consider customer acquisition campaigns")
        
        if 'transaction_type_name' in valid_data.columns:
            type_counts = valid_data['transaction_type_name'].value_counts()
            if len(type_counts) == 1:
                quick_recs.append("Diversify: Only one transaction type detected - expand service offerings")
        
        if data_quality_pct < 80:
            quick_recs.append("Data Quality: Improve data collection processes to reduce invalid records")
        
        if quick_recs:
            for rec in quick_recs:
                st.success(rec)
        else:
            st.info("Your transaction patterns look balanced. Continue monitoring for optimization opportunities.")
    
    # Data Patterns
    with st.expander("Data Patterns Analysis"):
        if 'created_at' in transactions_df.columns:
            try:
                transactions_df['date'] = pd.to_datetime(transactions_df['created_at']).dt.date
                daily_patterns = transactions_df.groupby('date').size()
                
                if len(daily_patterns) > 1:
                    st.write("Daily Transaction Pattern:")
                    fig = px.line(
                        x=daily_patterns.index,
                        y=daily_patterns.values,
                        title="Transaction Volume Over Time",
                        labels={'x': 'Date', 'y': 'Transactions'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"Single day analysis: {len(transactions_df)} transactions on {daily_patterns.index[0]}")
            except:
                st.write("Unable to analyze date patterns")
        
        if 'transaction_type_name' in transactions_df.columns:
            st.write("Transaction Type Distribution:")
            type_dist = transactions_df['transaction_type_name'].value_counts()
            fig = px.bar(
                x=type_dist.index,
                y=type_dist.values,
                title="Transactions by Type"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No transaction data available for analysis. Please check your database connection.")

# Tips section
with st.expander("How to Improve Your Analysis"):
    st.markdown("""
    **For Better Insights:**
    - Ensure transaction amounts are properly formatted
    - Include transaction type categories
    - Add customer information for segmentation
    - Track transaction timestamps for trend analysis
    - Monitor fee structures for optimization
    
    **Common Optimization Areas:**
    - Transaction volume growth
    - Average transaction value improvement  
    - Revenue stream diversification
    - Peak hour resource allocation
    - Fee structure optimization
    """)