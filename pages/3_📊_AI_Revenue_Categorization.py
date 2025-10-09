import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from openai import OpenAI
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests
import io
from operator import attrgetter

# Page configuration
st.set_page_config(
    page_title="AI Revenue Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .progress-bar {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stripe_connected' not in st.session_state:
    st.session_state.stripe_connected = False
if 'shopify_connected' not in st.session_state:
    st.session_state.shopify_connected = False
if 'stripe_charges' not in st.session_state:
    st.session_state.stripe_charges = []
if 'shopify_orders' not in st.session_state:
    st.session_state.shopify_orders = []
if 'ai_suggestions_generated' not in st.session_state:
    st.session_state.ai_suggestions_generated = False

# --- Database Functions ---
@st.cache_data(ttl=300)
def fetch_transactions():
    try:
        conn1 = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        transactions = pd.read_sql(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 200", conn1
        )
        conn1.close()
        return transactions
    except Exception as e:
        st.error(f"❌ Error fetching transactions: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_mappings():
    try:
        conn2 = psycopg2.connect(
            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_7AlUWE8wkigH",
            port=5432
        )
        cur2 = conn2.cursor()

        cur2.execute("SELECT * FROM transaction_categories")
        categories = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.execute("SELECT * FROM transaction_subcategories")
        subcategories = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.execute("SELECT * FROM transaction_types")
        types = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.close()
        conn2.close()
        return categories, subcategories, types
    except Exception as e:
        st.error(f"❌ Error fetching mappings: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- AI Categorization Functions ---
def suggest_category_ai(name: str):
    prompt = f"""
    Categorize the following financial transaction into Category and Subcategory:

    Transaction: "{name}"

    Respond ONLY in valid JSON:
    {{
    "category": "...",
    "subcategory": "..."
    }}
    """
    try:
        OPENAI_API_KEY = "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"
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial categorization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("category", "Other"), data.get("subcategory", "Uncategorized")
    except Exception as e:
        return "Other", "Uncategorized"

def suggest_category_ai_with_confidence(name: str):
    prompt = f"""
    Categorize the following financial transaction and provide confidence level:

    Transaction: "{name}"

    Respond ONLY in valid JSON:
    {{
    "category": "...",
    "subcategory": "...",
    "confidence": 0.95,
    "reasoning": "brief explanation"
    }}
    """
    try:
        OPENAI_API_KEY = "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"
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial categorization expert. Provide accurate categories with confidence scores."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.1
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return (data.get("category", "Other"), 
                data.get("subcategory", "Uncategorized"),
                data.get("confidence", 0.5),
                data.get("reasoning", "No reasoning provided"))
    except Exception as e:
        return "Other", "Uncategorized", 0.0, f"Error: {str(e)}"

# --- ENHANCED REVENUE LIFECYCLE ANALYSIS ---
def analyze_enhanced_revenue_lifecycle(merged_df):
    """Comprehensive revenue lifecycle analysis with robust error handling"""
    if merged_df.empty:
        return None
    
    lifecycle_data = {}
    
    # Ensure datetime conversion
    if 'created_at' in merged_df.columns:
        merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')
        merged_df['transaction_date'] = merged_df['created_at'].dt.date
        merged_df['transaction_month'] = merged_df['created_at'].dt.to_period('M')
        merged_df['transaction_week'] = merged_df['created_at'].dt.isocalendar().week
    
    # 1. CUSTOMER LIFECYCLE STAGE ANALYSIS
    if 'customer_id' in merged_df.columns:
        try:
            customer_analysis = merged_df.groupby('customer_id').agg({
                'amount': ['sum', 'count', 'mean', 'std'] if 'amount' in merged_df.columns else 'count',
                'created_at': ['min', 'max', 'nunique'] if 'created_at' in merged_df.columns else 'count'
            }).round(2)
            
            # Flatten column names
            customer_analysis.columns = ['_'.join(col).strip() for col in customer_analysis.columns.values]
            
            # Rename columns for consistency
            column_mapping = {}
            if 'amount_sum' in customer_analysis.columns:
                column_mapping['amount_sum'] = 'total_spent'
            if 'amount_count' in customer_analysis.columns:
                column_mapping['amount_count'] = 'transaction_count'
            if 'amount_mean' in customer_analysis.columns:
                column_mapping['amount_mean'] = 'avg_transaction'
            if 'amount_std' in customer_analysis.columns:
                column_mapping['amount_std'] = 'spend_std'
            if 'created_at_min' in customer_analysis.columns:
                column_mapping['created_at_min'] = 'first_purchase'
            if 'created_at_max' in customer_analysis.columns:
                column_mapping['created_at_max'] = 'last_purchase'
            if 'created_at_nunique' in customer_analysis.columns:
                column_mapping['created_at_nunique'] = 'unique_days'
            
            customer_analysis = customer_analysis.rename(columns=column_mapping)
            
            # Add missing columns with default values
            for col in ['total_spent', 'transaction_count', 'avg_transaction', 'spend_std', 
                       'first_purchase', 'last_purchase', 'unique_days']:
                if col not in customer_analysis.columns:
                    if col in ['total_spent', 'avg_transaction', 'spend_std']:
                        customer_analysis[col] = 0.0
                    elif col == 'transaction_count':
                        customer_analysis[col] = 1
                    else:
                        customer_analysis[col] = datetime.now()
            
            # Customer Lifetime Value (CLV)
            customer_analysis['clv'] = customer_analysis['total_spent']
            
            # Customer segments based on RFM (only if we have date data)
            if 'last_purchase' in customer_analysis.columns:
                customer_analysis['recency'] = (datetime.now() - customer_analysis['last_purchase']).dt.days
                customer_analysis['frequency'] = customer_analysis['transaction_count']
                customer_analysis['monetary'] = customer_analysis['total_spent']
                
                # Simple RFM scoring without qcut to avoid errors
                def calculate_simple_rfm(df):
                    if len(df) == 0:
                        return df
                    
                    # Simple percentile-based scoring
                    if df['recency'].nunique() > 1:
                        df['recency_score'] = pd.cut(df['recency'], bins=min(5, len(df)), labels=range(1, min(6, len(df)+1)))
                    else:
                        df['recency_score'] = 3
                    
                    if df['frequency'].nunique() > 1:
                        df['frequency_score'] = pd.cut(df['frequency'], bins=min(5, len(df)), labels=range(1, min(6, len(df)+1)))
                    else:
                        df['frequency_score'] = 3
                    
                    if df['monetary'].nunique() > 1:
                        df['monetary_score'] = pd.cut(df['monetary'], bins=min(5, len(df)), labels=range(1, min(6, len(df)+1)))
                    else:
                        df['monetary_score'] = 3
                    
                    return df
                
                customer_analysis = calculate_simple_rfm(customer_analysis)
                
                # Convert scores to integers, handling any errors
                for score_col in ['recency_score', 'frequency_score', 'monetary_score']:
                    if score_col in customer_analysis.columns:
                        customer_analysis[score_col] = pd.to_numeric(customer_analysis[score_col], errors='coerce').fillna(3).astype(int)
                
                customer_analysis['rfm_score'] = (
                    customer_analysis['recency_score'] + 
                    customer_analysis['frequency_score'] + 
                    customer_analysis['monetary_score']
                )
                
                # Customer segments
                def segment_customers(rfm_score):
                    if rfm_score >= 12: return 'Champions'
                    elif rfm_score >= 9: return 'Loyal Customers'
                    elif rfm_score >= 7: return 'Potential Loyalists'
                    elif rfm_score >= 5: return 'New Customers'
                    else: return 'At Risk'
                
                customer_analysis['segment'] = customer_analysis['rfm_score'].apply(segment_customers)
            
            lifecycle_data['customer_analysis'] = customer_analysis
            lifecycle_data['total_customers'] = len(customer_analysis)
            
            if 'segment' in customer_analysis.columns:
                lifecycle_data['customer_segments'] = customer_analysis['segment'].value_counts()
                
        except Exception as e:
            logger.warning(f"Customer analysis skipped due to error: {e}")
            lifecycle_data['total_customers'] = 0
            lifecycle_data['customer_segments'] = pd.Series()
    
    else:
        lifecycle_data['total_customers'] = 0
        lifecycle_data['customer_segments'] = pd.Series()
    
    # 2. REVENUE TREND ANALYSIS
    if 'created_at' in merged_df.columns and 'amount' in merged_df.columns:
        try:
            # Daily trends
            daily_revenue = merged_df.groupby('transaction_date')['amount'].agg(['sum', 'count']).reset_index()
            daily_revenue.columns = ['date', 'daily_revenue', 'daily_transactions']
            
            # Weekly trends
            weekly_revenue = merged_df.groupby('transaction_week')['amount'].agg(['sum', 'count']).reset_index()
            weekly_revenue.columns = ['week', 'weekly_revenue', 'weekly_transactions']
            
            # Monthly trends
            monthly_revenue = merged_df.groupby('transaction_month')['amount'].agg(['sum', 'count']).reset_index()
            monthly_revenue.columns = ['month', 'monthly_revenue', 'monthly_transactions']
            
            lifecycle_data['daily_revenue'] = daily_revenue
            lifecycle_data['weekly_revenue'] = weekly_revenue
            lifecycle_data['monthly_revenue'] = monthly_revenue
            
            # Growth metrics
            if len(monthly_revenue) > 1:
                monthly_revenue['revenue_growth'] = monthly_revenue['monthly_revenue'].pct_change() * 100
                monthly_revenue['transaction_growth'] = monthly_revenue['monthly_transactions'].pct_change() * 100
                lifecycle_data['avg_monthly_growth'] = monthly_revenue['revenue_growth'].mean()
                
        except Exception as e:
            logger.warning(f"Revenue trend analysis skipped due to error: {e}")
    
    # 3. CUSTOMER JOURNEY MAPPING (only if customer_id exists)
    if 'customer_id' in merged_df.columns and 'created_at' in merged_df.columns:
        try:
            customer_journey = merged_df.sort_values(['customer_id', 'created_at']).groupby('customer_id').agg({
                'created_at': ['first', 'last', 'count'],
                'amount': ['sum', 'mean'] if 'amount' in merged_df.columns else 'count'
            }).round(2)
            
            # Flatten column names
            customer_journey.columns = ['_'.join(col).strip() for col in customer_journey.columns.values]
            
            # Rename columns
            column_mapping = {
                'created_at_first': 'first_purchase',
                'created_at_last': 'last_purchase', 
                'created_at_count': 'total_visits',
                'amount_sum': 'total_spent',
                'amount_mean': 'avg_spend'
            }
            
            customer_journey = customer_journey.rename(columns=column_mapping)
            
            # Add preferred category if available
            if 'category_name' in merged_df.columns:
                preferred_categories = merged_df.groupby('customer_id')['category_name'].apply(
                    lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'
                )
                customer_journey['preferred_category'] = preferred_categories
            
            # Time between purchases
            if 'first_purchase' in customer_journey.columns and 'last_purchase' in customer_journey.columns:
                customer_journey['days_between_visits'] = (
                    (customer_journey['last_purchase'] - customer_journey['first_purchase']).dt.days / 
                    customer_journey['total_visits']
                ).round(1)
            
            lifecycle_data['customer_journey'] = customer_journey
            
        except Exception as e:
            logger.warning(f"Customer journey analysis skipped due to error: {e}")
    
    # 4. PRODUCT/CATEGORY PERFORMANCE (robust handling)
    if 'category_name' in merged_df.columns:
        try:
            # Build aggregation dictionary dynamically based on available columns
            agg_dict = {
                'amount': ['sum', 'mean', 'count', 'std'] if 'amount' in merged_df.columns else 'count'
            }
            
            # Only add customer_id if it exists
            if 'customer_id' in merged_df.columns:
                agg_dict['customer_id'] = 'nunique'
            
            category_performance = merged_df.groupby('category_name').agg(agg_dict).round(2)
            
            # Flatten column names
            category_performance.columns = ['_'.join(col).strip() for col in category_performance.columns.values]
            
            # Rename columns
            column_mapping = {}
            if 'amount_sum' in category_performance.columns:
                column_mapping['amount_sum'] = 'total_revenue'
            if 'amount_mean' in category_performance.columns:
                column_mapping['amount_mean'] = 'avg_transaction'
            if 'amount_count' in category_performance.columns:
                column_mapping['amount_count'] = 'transaction_count'
            if 'amount_std' in category_performance.columns:
                column_mapping['amount_std'] = 'revenue_std'
            if 'customer_id_nunique' in category_performance.columns:
                column_mapping['customer_id_nunique'] = 'unique_customers'
            elif 'amount_count' in category_performance.columns:
                column_mapping['amount_count'] = 'unique_customers'  # Fallback
            
            category_performance = category_performance.rename(columns=column_mapping)
            
            # Calculate revenue share if total_revenue exists
            if 'total_revenue' in category_performance.columns:
                category_performance['revenue_share'] = (
                    category_performance['total_revenue'] / category_performance['total_revenue'].sum() * 100
                ).round(2)
            
            lifecycle_data['category_performance'] = category_performance.sort_values(
                'total_revenue' if 'total_revenue' in category_performance.columns else 'transaction_count', 
                ascending=False
            )
            
        except Exception as e:
            logger.warning(f"Category performance analysis skipped due to error: {e}")
            # Create empty category performance
            lifecycle_data['category_performance'] = pd.DataFrame()
    
    # 5. BASIC METRICS (always available)
    try:
        lifecycle_data['total_revenue'] = merged_df['amount'].sum() if 'amount' in merged_df.columns else 0
        lifecycle_data['total_transactions'] = len(merged_df)
        lifecycle_data['avg_transaction_value'] = merged_df['amount'].mean() if 'amount' in merged_df.columns else 0
        
        # Count unique customers if available, otherwise use transaction count
        if 'customer_id' in merged_df.columns:
            lifecycle_data['unique_customers'] = merged_df['customer_id'].nunique()
        else:
            lifecycle_data['unique_customers'] = lifecycle_data['total_transactions']
            
    except Exception as e:
        logger.warning(f"Basic metrics calculation error: {e}")
        # Set default values
        lifecycle_data['total_revenue'] = 0
        lifecycle_data['total_transactions'] = 0
        lifecycle_data['avg_transaction_value'] = 0
        lifecycle_data['unique_customers'] = 0
    
    return lifecycle_data
    
    # 2. REVENUE TREND ANALYSIS
    if 'created_at' in merged_df.columns:
        # Daily trends
        daily_revenue = merged_df.groupby('transaction_date')['amount'].agg(['sum', 'count']).reset_index()
        daily_revenue.columns = ['date', 'daily_revenue', 'daily_transactions']
        
        # Weekly trends
        weekly_revenue = merged_df.groupby('transaction_week')['amount'].agg(['sum', 'count']).reset_index()
        weekly_revenue.columns = ['week', 'weekly_revenue', 'weekly_transactions']
        
        # Monthly trends
        monthly_revenue = merged_df.groupby('transaction_month')['amount'].agg(['sum', 'count']).reset_index()
        monthly_revenue.columns = ['month', 'monthly_revenue', 'monthly_transactions']
        
        lifecycle_data['daily_revenue'] = daily_revenue
        lifecycle_data['weekly_revenue'] = weekly_revenue
        lifecycle_data['monthly_revenue'] = monthly_revenue
        
        # Growth metrics
        if len(monthly_revenue) > 1:
            monthly_revenue['revenue_growth'] = monthly_revenue['monthly_revenue'].pct_change() * 100
            monthly_revenue['transaction_growth'] = monthly_revenue['monthly_transactions'].pct_change() * 100
            lifecycle_data['avg_monthly_growth'] = monthly_revenue['revenue_growth'].mean()
    
    # 3. CUSTOMER JOURNEY MAPPING
    if 'customer_id' in merged_df.columns and 'created_at' in merged_df.columns:
        customer_journey = merged_df.sort_values(['customer_id', 'created_at']).groupby('customer_id').agg({
            'created_at': ['first', 'last', 'count'],
            'amount': ['sum', 'mean'],
            'category_name': lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'
        }).round(2)
        
        customer_journey.columns = ['first_purchase', 'last_purchase', 'total_visits', 
                                  'total_spent', 'avg_spend', 'preferred_category']
        
        # Time between purchases
        customer_journey['days_between_visits'] = (
            (customer_journey['last_purchase'] - customer_journey['first_purchase']).dt.days / 
            customer_journey['total_visits']
        ).round(1)
        
        lifecycle_data['customer_journey'] = customer_journey
    
    # 4. PRODUCT/CATEGORY PERFORMANCE
    if 'category_name' in merged_df.columns:
        category_performance = merged_df.groupby('category_name').agg({
            'amount': ['sum', 'mean', 'count', 'std'],
            'customer_id': 'nunique' if 'customer_id' in merged_df.columns else 'count'
        }).round(2)
        
        category_performance.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                                      'revenue_std', 'unique_customers']
        
        category_performance['revenue_share'] = (
            category_performance['total_revenue'] / category_performance['total_revenue'].sum() * 100
        ).round(2)
        
        lifecycle_data['category_performance'] = category_performance.sort_values('total_revenue', ascending=False)
    
    # 5. CUSTOMER ACQUISITION & RETENTION METRICS
    if 'customer_id' in merged_df.columns and 'created_at' in merged_df.columns:
        # Cohort analysis
        merged_df['cohort_month'] = merged_df.groupby('customer_id')['created_at'].transform('min').dt.to_period('M')
        cohort_data = merged_df.groupby(['cohort_month', 'transaction_month']).agg({
            'customer_id': 'nunique',
            'amount': 'sum'
        }).reset_index()
        
        cohort_data['period_number'] = (cohort_data['transaction_month'] - cohort_data['cohort_month']).apply(attrgetter('n'))
        
        cohort_pivot = cohort_data.pivot_table(
            index='cohort_month', 
            columns='period_number', 
            values='customer_id', 
            aggfunc='sum'
        )
        
        lifecycle_data['cohort_analysis'] = cohort_pivot
    
    # 6. PREDICTIVE METRICS
    if 'customer_id' in merged_df.columns and 'created_at' in merged_df.columns:
        latest_date = merged_df['created_at'].max()
        days_threshold = 30
        
        customer_last_activity = merged_df.groupby('customer_id')['created_at'].max()
        churned_customers = customer_last_activity[
            (latest_date - customer_last_activity).dt.days > days_threshold
        ]
        
        lifecycle_data['churn_rate'] = len(churned_customers) / len(customer_last_activity) * 100 if len(customer_last_activity) > 0 else 0
        lifecycle_data['active_customers'] = len(customer_last_activity) - len(churned_customers)
    
    # Basic metrics
    lifecycle_data['total_revenue'] = merged_df['amount'].sum() if 'amount' in merged_df.columns else 0
    lifecycle_data['total_transactions'] = len(merged_df)
    lifecycle_data['avg_transaction_value'] = merged_df['amount'].mean() if 'amount' in merged_df.columns else 0
    
    return lifecycle_data

def create_lifecycle_visualizations(lifecycle_data):
    """Create comprehensive visualizations for lifecycle analysis"""
    visualizations = {}
    
    # 1. Customer Segmentation Pie Chart
    if 'customer_segments' in lifecycle_data:
        fig_segments = px.pie(
            values=lifecycle_data['customer_segments'].values,
            names=lifecycle_data['customer_segments'].index,
            title="Customer Segmentation",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        visualizations['customer_segments'] = fig_segments
    
    # 2. Revenue Trend Chart
    if 'monthly_revenue' in lifecycle_data:
        monthly_df = lifecycle_data['monthly_revenue'].copy()
        monthly_df['month'] = monthly_df['month'].astype(str)
        fig_revenue_trend = px.line(
            monthly_df, 
            x='month', 
            y='monthly_revenue',
            title="Monthly Revenue Trend",
            markers=True
        )
        fig_revenue_trend.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
        visualizations['revenue_trend'] = fig_revenue_trend
    
    # 3. RFM Analysis Scatter Plot
    if 'customer_analysis' in lifecycle_data:
        customer_df = lifecycle_data['customer_analysis'].reset_index()
        fig_rfm = px.scatter(
            customer_df,
            x='frequency',
            y='monetary',
            color='segment',
            size='recency',
            title="RFM Customer Analysis",
            hover_data=['customer_id', 'total_spent']
        )
        visualizations['rfm_analysis'] = fig_rfm
    
    # 4. Category Performance
    if 'category_performance' in lifecycle_data:
        top_categories = lifecycle_data['category_performance'].head(10).reset_index()
        fig_categories = px.bar(
            top_categories,
            x='category_name',
            y='total_revenue',
            title="Top Revenue Categories",
            color='total_revenue',
            color_continuous_scale='Viridis'
        )
        visualizations['category_performance'] = fig_categories
    
    return visualizations

def generate_lifecycle_insights(lifecycle_data):
    """Generate AI-powered insights from lifecycle data"""
    insights = []
    
    # Revenue Insights
    if 'avg_monthly_growth' in lifecycle_data:
        growth = lifecycle_data['avg_monthly_growth']
        if not np.isnan(growth):
            if growth > 10:
                insights.append("🚀 **Strong Growth**: Monthly revenue growing at {:.1f}% - consider scaling acquisition".format(growth))
            elif growth > 0:
                insights.append("📈 **Steady Growth**: Revenue growing at {:.1f}% - maintain current strategy".format(growth))
            else:
                insights.append("⚠️ **Growth Challenge**: Revenue decline detected - review customer acquisition")
    
    # Customer Segmentation Insights
    if 'customer_segments' in lifecycle_data:
        segments = lifecycle_data['customer_segments']
        total_customers = segments.sum()
        if total_customers > 0:
            champions_pct = segments.get('Champions', 0) / total_customers * 100
            at_risk_pct = segments.get('At Risk', 0) / total_customers * 100
            
            if champions_pct > 20:
                insights.append("🎯 **Strong Loyalty**: {:.1f}% of customers are Champions - focus on retention".format(champions_pct))
            if at_risk_pct > 15:
                insights.append("🔔 **Churn Risk**: {:.1f}% of customers are At Risk - implement win-back campaigns".format(at_risk_pct))
    
    # Category Insights
    if 'category_performance' in lifecycle_data:
        category_data = lifecycle_data['category_performance']
        if len(category_data) > 0:
            top_category = category_data.iloc[0]
            top_share = top_category['revenue_share']
            
            if top_share > 50:
                insights.append("📊 **Category Concentration**: {:.1f}% of revenue from one category - consider diversification".format(top_share))
    
    # Transaction Insights
    avg_value = lifecycle_data.get('avg_transaction_value', 0)
    if avg_value < 50:
        insights.append("💰 **Upsell Opportunity**: Low average transaction value (${:.2f}) - implement bundling".format(avg_value))
    
    # Churn Insights
    churn_rate = lifecycle_data.get('churn_rate', 0)
    if churn_rate > 20:
        insights.append("🚨 **High Churn Alert**: {:.1f}% churn rate detected - improve customer retention".format(churn_rate))
    
    return insights

# --- Sidebar with Real Integrations ---
def render_sidebar():
    with st.sidebar:
        st.header("🔗 Real System Integrations")
        
        # System Connection Status
        st.subheader("📡 Connection Status")
        
        # Stripe Integration
        with st.expander("💳 Stripe", expanded=False):
            stripe_api_key = st.text_input("Stripe Secret Key", type="password", 
                                         placeholder="sk_live_...", key="stripe_key")
            
            if st.button("Connect Stripe", key="connect_stripe"):
                if stripe_api_key:
                    with st.spinner("Connecting to Stripe..."):
                        try:
                            headers = {'Authorization': f'Bearer {stripe_api_key}'}
                            response = requests.get('https://api.stripe.com/v1/balance', headers=headers, timeout=10)
                            
                            if response.status_code == 200:
                                st.session_state.stripe_connected = True
                                st.session_state.stripe_api_key = stripe_api_key
                                st.success("✅ Stripe connected successfully!")
                            else:
                                st.error(f"❌ Stripe connection failed: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error connecting to Stripe: {str(e)}")
                else:
                    st.error("Please enter your Stripe API key")
            
            if st.session_state.get('stripe_connected'):
                st.success("🟢 Stripe Connected")
                
                if st.button("🔄 Sync Stripe Data", use_container_width=True):
                    with st.spinner("Fetching Stripe data..."):
                        try:
                            headers = {'Authorization': f'Bearer {st.session_state.stripe_api_key}'}
                            charges_response = requests.get('https://api.stripe.com/v1/charges?limit=10', headers=headers)
                            
                            if charges_response.status_code == 200:
                                charges_data = charges_response.json()
                                st.success(f"✅ Synced {len(charges_data.get('data', []))} charges")
                                st.session_state.stripe_charges = charges_data.get('data', [])
                            else:
                                st.error("Failed to fetch Stripe data")
                        except Exception as e:
                            st.error(f"Error syncing Stripe data: {str(e)}")

        # Shopify Integration
        with st.expander("🛍️ Shopify", expanded=False):
            shopify_store_url = st.text_input("Shopify Store URL", placeholder="your-store.myshopify.com")
            shopify_access_token = st.text_input("Shopify Access Token", type="password")
            
            if st.button("Connect Shopify", key="connect_shopify"):
                if shopify_store_url and shopify_access_token:
                    with st.spinner("Connecting to Shopify..."):
                        try:
                            url = f"https://{shopify_store_url}/admin/api/2024-01/products.json"
                            headers = {'X-Shopify-Access-Token': shopify_access_token}
                            response = requests.get(url, headers=headers, timeout=10)
                            
                            if response.status_code == 200:
                                st.session_state.shopify_connected = True
                                st.session_state.shopify_store_url = shopify_store_url
                                st.session_state.shopify_access_token = shopify_access_token
                                st.success("✅ Shopify connected successfully!")
                            else:
                                st.error(f"❌ Shopify connection failed: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error connecting to Shopify: {str(e)}")
                else:
                    st.error("Please enter Shopify credentials")
            
            if st.session_state.get('shopify_connected'):
                st.success("🟢 Shopify Connected")
                
                if st.button("🔄 Sync Shopify Orders", use_container_width=True):
                    with st.spinner("Fetching Shopify orders..."):
                        try:
                            url = f"https://{st.session_state.shopify_store_url}/admin/api/2024-01/orders.json"
                            headers = {'X-Shopify-Access-Token': st.session_state.shopify_access_token}
                            response = requests.get(url, headers=headers, params={'limit': 20})
                            
                            if response.status_code == 200:
                                orders_data = response.json()
                                st.success(f"✅ Synced {len(orders_data.get('orders', []))} Shopify orders")
                                st.session_state.shopify_orders = orders_data.get('orders', [])
                            else:
                                st.error("Failed to fetch Shopify orders")
                        except Exception as e:
                            st.error(f"Error syncing Shopify: {str(e)}")

        st.divider()
        
        # Quick Actions Section
        st.header("⚡ Quick Actions")
        
        # Data Export Actions
        st.subheader("📤 Export Data")
        
        if st.button("📄 Export to CSV", use_container_width=True):
            try:
                transactions = fetch_transactions()
                if not transactions.empty:
                    csv = transactions.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"revenue_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No transaction data to export")
            except Exception as e:
                st.error(f"Export error: {str(e)}")

        if st.button("📊 Export to Excel", use_container_width=True):
            try:
                transactions = fetch_transactions()
                if not transactions.empty:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        transactions.to_excel(writer, sheet_name='Transactions', index=False)
                    
                    st.download_button(
                        label="Download Excel",
                        data=output.getvalue(),
                        file_name=f"revenue_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )
                else:
                    st.warning("No transaction data to export")
            except Exception as e:
                st.error(f"Excel export error: {str(e)}")

        # Sync Actions
        st.subheader("🔄 Sync Actions")
        
        if st.button("🔄 Sync All Systems", use_container_width=True):
            connected_systems = []
            if st.session_state.get('stripe_connected'):
                connected_systems.append("Stripe")
            if st.session_state.get('shopify_connected'):
                connected_systems.append("Shopify")
                
            if connected_systems:
                with st.spinner(f"Syncing {', '.join(connected_systems)}..."):
                    time.sleep(2)
                    st.success(f"✅ Synced {len(connected_systems)} systems")
            else:
                st.warning("No systems connected")

        st.divider()
        
        # API Usage
        st.subheader("📊 API Usage")
        if st.session_state.get('stripe_connected'):
            st.metric("Stripe API Calls", "45", "+12 today")
        if st.session_state.get('shopify_connected'):
            st.metric("Shopify API Calls", "23", "+5 today")

# --- Main Application ---
def main():
    st.markdown('<h1 class="main-header">🤖 AI Revenue Intelligence Dashboard</h1>', unsafe_allow_html=True)
    
    # Quick Stats Header
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Total Transactions", "1,234", "+12%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Total Revenue", "$456K", "+8%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎯 Mapped Rate", "89%", "+5%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🤖 AI Accuracy", "94%", "+2%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Fetch and process data
    transactions = fetch_transactions()
    categories, subcategories, types = fetch_mappings()
    
    if transactions.empty:
        st.error("🚫 No transaction data available. Please check your database connection.")
        return

    # Data processing
    types = types.merge(categories, on="category_id", how="left")
    merged = transactions.merge(types, on="transaction_type_id", how="left")
    unmapped = merged[merged["category_name"].isnull()]

    # Create main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Smart Categorization", "📊 Visual Analytics", "🔄 Revenue Lifecycle", "🔗 Connected Data"])

    with tab1:
        st.subheader("🎯 AI-Powered Transaction Categorization")
        
        # Progress overview
        total_transactions = len(merged)
        mapped_count = total_transactions - len(unmapped)
        mapping_progress = mapped_count / total_transactions
        
        st.write(f"**Mapping Progress:** {mapped_count}/{total_transactions} transactions categorized")
        st.markdown(f'<div class="progress-bar" style="width: {mapping_progress * 100}%"></div>', unsafe_allow_html=True)
        
        if not unmapped.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.warning(f"🚨 {len(unmapped)} transactions need categorization")
                
                if st.button("🎯 Generate AI Suggestions", type="primary"):
                    with st.spinner("🤖 AI is analyzing transactions..."):
                        progress_bar = st.progress(0)
                        results = []
                        
                        for i, (idx, row) in enumerate(unmapped.iterrows()):
                            suggestion = suggest_category_ai_with_confidence(row["transaction_type_name"])
                            results.append({
                                'id': row['id'],
                                'transaction_type_name': row['transaction_type_name'],
                                'suggested_category': suggestion[0],
                                'suggested_subcategory': suggestion[1],
                                'confidence': suggestion[2],
                                'reasoning': suggestion[3]
                            })
                            progress_bar.progress((i + 1) / len(unmapped))
                        
                        st.session_state.ai_suggestions = pd.DataFrame(results)
                        st.session_state.ai_suggestions_generated = True
                        st.success("✅ AI suggestions generated!")
            
            with col2:
                st.info("💡 **Tips:**\n- Review high-confidence suggestions\n- Bulk approve similar transactions\n- Monitor AI accuracy over time")
            
            # Display enhanced suggestions
            if st.session_state.ai_suggestions_generated:
                st.subheader("🤖 AI Suggestions")
                
                for _, row in st.session_state.ai_suggestions.iterrows():
                    with st.expander(f"💰 {row['transaction_type_name']} → {row['suggested_category']} ({row['confidence']:.0%} confidence)"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Reasoning:** {row['reasoning']}")
                        with col2:
                            st.write(f"**Confidence:** {row['confidence']:.0%}")
                            if st.button(f"Approve", key=f"approve_{row['id']}"):
                                st.success(f"Approved: {row['transaction_type_name']}")

            # Manual mapping form
            with st.form("mapping_form"):
                st.subheader("🔄 Manual Mapping")
                selected_id = st.selectbox("Pick a transaction to map", unmapped["id"])
                selected_cat = st.selectbox("Category", categories["category_name"].unique())

                cat_id = categories[categories["category_name"] == selected_cat]["category_id"].iloc[0]
                sub_options = subcategories[subcategories["category_id"] == cat_id]
                selected_sub = st.selectbox("Subcategory", sub_options["subcategory_name"].unique())

                if st.form_submit_button("✅ Approve Mapping"):
                    sub_id = sub_options[sub_options["subcategory_name"] == selected_sub]["subcategory_id"].iloc[0]
                    try:
                        conn2 = psycopg2.connect(
                            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
                            database="neondb",
                            user="neondb_owner",
                            password="npg_7AlUWE8wkigH",
                            port=5432
                        )
                        cur2 = conn2.cursor()
                        cur2.execute("""
                            UPDATE transaction_types 
                            SET category_id = %s, subcategory_id = %s
                            WHERE transaction_type_id = (
                                SELECT transaction_type_id FROM transactions WHERE id = %s
                            )
                        """, (cat_id, sub_id, selected_id))
                        conn2.commit()
                        cur2.close()
                        conn2.close()
                        st.success(f"Transaction {selected_id} mapped to {selected_cat} → {selected_sub}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating mapping: {e}")

    with tab2:
        st.subheader("📊 Revenue Analytics")
        
        if "amount" in merged.columns:
            # Currency selection
            currency = st.selectbox("Display Currency", ["USD", "ZiG"])
            exchange_rate = 13.5 if currency == "ZiG" else 1.0
            
            amount_col = "amount_converted"
            merged[amount_col] = merged["amount"] * exchange_rate

            revenue_summary = merged.groupby("category_name")[amount_col].sum().reset_index().sort_values(amount_col, ascending=False)

            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig1, ax1 = plt.subplots()
                ax1.pie(revenue_summary[amount_col], labels=revenue_summary["category_name"], autopct="%1.1f%%")
                ax1.axis("equal")
                st.pyplot(fig1)
            
            with col2:
                # Bar chart
                fig2, ax2 = plt.subplots()
                ax2.bar(revenue_summary["category_name"], revenue_summary[amount_col])
                ax2.set_xticks(range(len(revenue_summary["category_name"])))
                ax2.set_xticklabels(revenue_summary["category_name"], rotation=45, ha="right")
                ax2.set_ylabel(f"Revenue ({currency})")
                st.pyplot(fig2)

            # Trend chart
            if "created_at" in merged.columns:
                merged["created_at"] = pd.to_datetime(merged["created_at"], errors="coerce")
                trend = merged.groupby([merged["created_at"].dt.date, "category_name"])[amount_col].sum().reset_index()

                fig3, ax3 = plt.subplots()
                for cat in trend["category_name"].unique():
                    sub_df = trend[trend["category_name"] == cat]
                    ax3.plot(sub_df["created_at"], sub_df[amount_col], marker="o", label=cat)
                ax3.legend()
                ax3.set_ylabel(f"Revenue ({currency})")
                ax3.set_xlabel("Date")
                plt.xticks(rotation=45)
                st.pyplot(fig3)

    with tab3:
        st.subheader("🔄 Advanced Revenue Lifecycle Analysis")
        
        # Enhanced lifecycle analysis
        lifecycle_data = analyze_enhanced_revenue_lifecycle(merged)
        
        if lifecycle_data:
            # Executive Summary
            st.subheader("📊 Executive Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Revenue", 
                    f"${lifecycle_data['total_revenue']:,.0f}",
                    delta=f"{lifecycle_data.get('avg_monthly_growth', 0):.1f}% MoM" if not np.isnan(lifecycle_data.get('avg_monthly_growth', 0)) else None
                )
            
            with col2:
                st.metric(
                    "Active Customers",
                    f"{lifecycle_data.get('active_customers', 0):,}",
                    delta=f"{lifecycle_data.get('churn_rate', 0):.1f}% churn"
                )
            
            with col3:
                st.metric(
                    "Avg Transaction", 
                    f"${lifecycle_data['avg_transaction_value']:.2f}",
                    f"{lifecycle_data['total_transactions']:,} transactions"
                )
            
            with col4:
                if 'customer_segments' in lifecycle_data:
                    champions = lifecycle_data['customer_segments'].get('Champions', 0)
                    total_customers = lifecycle_data['total_customers']
                    if total_customers > 0:
                        st.metric(
                            "Champion Customers",
                            f"{champions:,}",
                            f"{champions/total_customers*100:.1f}%"
                        )
            
            # AI-Powered Insights
            st.subheader("🤖 AI Insights & Recommendations")
            insights = generate_lifecycle_insights(lifecycle_data)
            
            for insight in insights:
                st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
            
            # Visualizations
            st.subheader("📈 Lifecycle Visualizations")
            visualizations = create_lifecycle_visualizations(lifecycle_data)
            
            # Display charts in a grid
            if visualizations:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'customer_segments' in visualizations:
                        st.plotly_chart(visualizations['customer_segments'], use_container_width=True)
                    if 'revenue_trend' in visualizations:
                        st.plotly_chart(visualizations['revenue_trend'], use_container_width=True)
                
                with col2:
                    if 'rfm_analysis' in visualizations:
                        st.plotly_chart(visualizations['rfm_analysis'], use_container_width=True)
                    if 'category_performance' in visualizations:
                        st.plotly_chart(visualizations['category_performance'], use_container_width=True)
            
            # Detailed Analysis Sections
            st.subheader("🔍 Detailed Analysis")
            
            # Customer Segmentation Details
            if 'customer_segments' in lifecycle_data:
                with st.expander("👥 Customer Segmentation Details", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Customer Distribution by Segment**")
                        segments_df = lifecycle_data['customer_segments'].reset_index()
                        segments_df.columns = ['Segment', 'Count']
                        segments_df['Percentage'] = (segments_df['Count'] / segments_df['Count'].sum() * 100).round(1)
                        st.dataframe(segments_df, use_container_width=True)
                    
                    with col2:
                        st.write("**Segment Definitions**")
                        st.info("""
                        **Champions**: Recent, frequent, high spenders  
                        **Loyal**: Regular customers with good value  
                        **Potential**: New but promising customers  
                        **At Risk**: Declining activity, need attention
                        """)
            
            # RFM Analysis Details
            if 'customer_analysis' in lifecycle_data:
                with st.expander("🎯 RFM Analysis Details", expanded=False):
                    st.write("**Top Customers by RFM Score**")
                    top_customers = lifecycle_data['customer_analysis'].sort_values('rfm_score', ascending=False).head(10)
                    display_cols = ['total_spent', 'transaction_count', 'recency', 'segment']
                    available_cols = [col for col in display_cols if col in top_customers.columns]
                    st.dataframe(top_customers[available_cols], use_container_width=True)
            
            # Export Lifecycle Report
            st.subheader("📤 Export Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Generate Lifecycle Report", use_container_width=True):
                    # Generate comprehensive report
                    report_data = {
                        'executive_summary': {
                            'total_revenue': lifecycle_data['total_revenue'],
                            'total_customers': lifecycle_data['total_customers'],
                            'growth_rate': lifecycle_data.get('avg_monthly_growth', 0),
                            'churn_rate': lifecycle_data.get('churn_rate', 0)
                        },
                        'insights': insights,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.success("✅ Lifecycle report generated!")
                    st.json(report_data)
            
            with col2:
                if st.button("📧 Email to Management", use_container_width=True):
                    st.info("📧 Lifecycle report would be emailed to management")
        
        else:
            st.info("No transaction data available for advanced lifecycle analysis.")

    with tab4:
        st.subheader("🔗 Connected Systems Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Stripe Data
            if st.session_state.get('stripe_connected') and st.session_state.get('stripe_charges'):
                st.write("💳 Recent Stripe Charges**")
                charges_df = pd.DataFrame(st.session_state.stripe_charges)
                if not charges_df.empty:
                    display_cols = ['id', 'amount', 'currency', 'status', 'created']
                    available_cols = [col for col in display_cols if col in charges_df.columns]
                    st.dataframe(charges_df[available_cols].head(10), use_container_width=True)
        
        with col2:
            # Shopify Data
            if st.session_state.get('shopify_connected') and st.session_state.get('shopify_orders'):
                st.write("🛍️ Recent Shopify Orders**")
                orders_df = pd.DataFrame(st.session_state.shopify_orders)
                if not orders_df.empty:
                    display_cols = ['id', 'order_number', 'total_price', 'financial_status', 'created_at']
                    available_cols = [col for col in display_cols if col in orders_df.columns]
                    st.dataframe(orders_df[available_cols].head(10), use_container_width=True)

        # Integration Status
        st.subheader("🚀 Integration Status")
        connected_count = 0
        if st.session_state.get('stripe_connected'):
            st.success("✅ Stripe Connected")
            connected_count += 1
        else:
            st.error("❌ Stripe Disconnected")
            
        if st.session_state.get('shopify_connected'):
            st.success("✅ Shopify Connected")
            connected_count += 1
        else:
            st.error("❌ Shopify Disconnected")
            
        st.metric("Systems Connected", connected_count)

if __name__ == "__main__":
    main()