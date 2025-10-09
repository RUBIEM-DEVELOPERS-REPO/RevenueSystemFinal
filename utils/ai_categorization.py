import json
import pandas as pd
import numpy as np
from openai import OpenAI

def suggest_category_ai(name: str, client):
    """Get AI suggestions for transaction categorization"""
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

def analyze_revenue_lifecycle(merged_df):
    """Analyze revenue across customer lifecycle stages"""
    if merged_df.empty:
        return None
    
    lifecycle_data = {}
    
    # Basic revenue metrics
    total_revenue = merged_df['amount'].sum() if 'amount' in merged_df.columns else 0
    total_transactions = len(merged_df)
    
    # Revenue by category
    if 'category_name' in merged_df.columns:
        category_revenue = merged_df.groupby('category_name')['amount'].sum().sort_values(ascending=False)
        lifecycle_data['category_revenue'] = category_revenue
    else:
        category_revenue = pd.Series()
    
    # Customer behavior analysis
    if 'customer_id' in merged_df.columns:
        customer_metrics = merged_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean'],
            'created_at': ['min', 'max']
        }).round(2)
        
        lifecycle_data['customer_metrics'] = customer_metrics
        lifecycle_data['total_customers'] = len(customer_metrics)
        
        # Customer segmentation
        if len(customer_metrics) > 0:
            high_value = customer_metrics[('amount', 'sum')] > customer_metrics[('amount', 'sum')].quantile(0.8)
            lifecycle_data['high_value_customers'] = high_value.sum()
        else:
            lifecycle_data['high_value_customers'] = 0
    else:
        lifecycle_data['total_customers'] = 0
        lifecycle_data['high_value_customers'] = 0
    
    # Transaction frequency analysis
    if 'created_at' in merged_df.columns:
        merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')
        daily_transactions = merged_df.groupby(merged_df['created_at'].dt.date).size()
        lifecycle_data['avg_daily_transactions'] = daily_transactions.mean() if len(daily_transactions) > 0 else 0
        lifecycle_data['revenue_trend'] = merged_df.groupby(merged_df['created_at'].dt.date)['amount'].sum() if 'amount' in merged_df.columns else pd.Series()
    else:
        lifecycle_data['avg_daily_transactions'] = 0
        lifecycle_data['revenue_trend'] = pd.Series()
    
    lifecycle_data['total_revenue'] = total_revenue
    lifecycle_data['total_transactions'] = total_transactions
    
    return lifecycle_data

import pandas as pd
import numpy as np
import json
from openai import OpenAI

def suggest_category_ai(name: str, client):
    """Get AI suggestions for transaction categorization"""
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

def analyze_revenue_lifecycle(merged_df):
    """Analyze revenue across customer lifecycle stages"""
    if merged_df.empty:
        return None
    
    lifecycle_data = {}
    
    # Basic revenue metrics
    total_revenue = merged_df['amount'].sum() if 'amount' in merged_df.columns else 0
    total_transactions = len(merged_df)
    
    # Revenue by category (acquisition stage proxy)
    if 'category_name' in merged_df.columns:
        category_revenue = merged_df.groupby('category_name')['amount'].sum().sort_values(ascending=False)
        lifecycle_data['category_revenue'] = category_revenue
    else:
        category_revenue = pd.Series()
    
    # Customer behavior analysis (if customer data exists)
    if 'customer_id' in merged_df.columns:
        customer_metrics = merged_df.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean'],
            'created_at': ['min', 'max']
        }).round(2)
        
        lifecycle_data['customer_metrics'] = customer_metrics
        lifecycle_data['total_customers'] = len(customer_metrics)
        
        # Customer segmentation
        if len(customer_metrics) > 0:
            high_value = customer_metrics[('amount', 'sum')] > customer_metrics[('amount', 'sum')].quantile(0.8)
            lifecycle_data['high_value_customers'] = high_value.sum()
        else:
            lifecycle_data['high_value_customers'] = 0
    else:
        lifecycle_data['total_customers'] = 0
        lifecycle_data['high_value_customers'] = 0
    
    # Transaction frequency analysis (retention proxy)
    if 'created_at' in merged_df.columns:
        merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')
        daily_transactions = merged_df.groupby(merged_df['created_at'].dt.date).size()
        lifecycle_data['avg_daily_transactions'] = daily_transactions.mean() if len(daily_transactions) > 0 else 0
        lifecycle_data['revenue_trend'] = merged_df.groupby(merged_df['created_at'].dt.date)['amount'].sum() if 'amount' in merged_df.columns else pd.Series()
    else:
        lifecycle_data['avg_daily_transactions'] = 0
        lifecycle_data['revenue_trend'] = pd.Series()
    
    lifecycle_data['total_revenue'] = total_revenue
    lifecycle_data['total_transactions'] = total_transactions
    
    return lifecycle_data

def ai_insights_with_severity(trend_df, anomalies_df, client):
    """Generate AI-powered insights with severity scoring for anomalies"""
    if not client or trend_df.empty:
        return None
        
    sample = trend_df.tail(30).to_dict(orient="records")
    
    if not anomalies_df.empty:
        anomalies_sample = anomalies_df.tail(10).to_dict(orient="records")
    else:
        anomalies_sample = []
    
    prompt = f"""
    As a senior financial analyst, analyze this transaction data and provide:
    1. Key revenue insights and trends
    2. Anomaly analysis with severity assessment
    3. Recommended investigation priorities
    
    Transaction Trends:
    {json.dumps(sample, default=str)}
    
    Detected Anomalies:
    {json.dumps(anomalies_sample, default=str)}
    
    Respond with JSON:
    {{
        "revenue_insights": ["list of key insights"],
        "critical_anomalies": [
            {{
                "description": "anomaly description",
                "severity": "high/medium/low",
                "recommended_action": "action needed",
                "risk_score": 0.95
            }}
        ],
        "investigation_priority": ["ordered list of transaction IDs to investigate"],
        "business_impact": "summary of potential business impact"
    }}
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a risk analysis expert. Provide actionable insights with clear severity scoring."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
        )
        content = resp.choices[0].message.content
        return _safe_json_parse(content)
    except Exception:
        return None

def _safe_json_parse(text):
    """Safely parse JSON from text"""
    import re
    import json
    
    if not isinstance(text, str):
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}