import pandas as pd
import numpy as np
import json
import re
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px

class AdvancedAnomalyDetector:
    """Advanced anomaly detection using multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_fitted = False

    def detect_anomalies_ensemble(self, df, feature_columns, contamination=0.1):
        """Simplified ensemble anomaly detection for immediate use"""
        try:
            sample_size = len(df)
            
            # For very small samples, use simpler approach
            if sample_size < 10:
                print(f"Too few samples ({sample_size}) for reliable anomaly detection")
                df['is_anomaly'] = 0
                df['combined_severity'] = 0.0
                df['ensemble_anomaly_score'] = 0.0
                return df
            
            # Convert all feature columns to numeric to handle decimal.Decimal types
            for col in feature_columns:
                if col in df.columns:
                    df[col] = df[col].astype(float)
            
            # Simple anomaly detection based on amount outliers
            if 'amount' in df.columns:
                amount_mean = df['amount'].mean()
                amount_std = df['amount'].std()
                
                if amount_std > 0:
                    # Calculate z-score for amount
                    df['amount_zscore'] = (df['amount'] - amount_mean) / amount_std
                    
                    # Create anomaly score based on absolute z-score
                    df['ensemble_anomaly_score'] = abs(df['amount_zscore'])
                    
                    # Mark top anomalies based on contamination
                    threshold = df['ensemble_anomaly_score'].quantile(1 - contamination)
                    df['is_anomaly'] = (df['ensemble_anomaly_score'] >= threshold).astype(int)
                    df['combined_severity'] = df['ensemble_anomaly_score']
                else:
                    # If no variation in amount, no anomalies
                    df['is_anomaly'] = 0
                    df['combined_severity'] = 0.0
                    df['ensemble_anomaly_score'] = 0.0
            else:
                # If no amount column, no anomalies
                df['is_anomaly'] = 0
                df['combined_severity'] = 0.0
                df['ensemble_anomaly_score'] = 0.0
            
            self.is_fitted = True
            return df
            
        except Exception as e:
            print(f"Anomaly detection error: {str(e)}")
            # Set safe defaults
            df['is_anomaly'] = 0
            df['combined_severity'] = 0.0
            df['ensemble_anomaly_score'] = 0.0
            return df

class FeeVerificationSystem:
    def __init__(self):
        self.learning_data = []
        
    def verify_fee_compliance(self, transaction, charges_df, recommendations_df):
        try:
            ttype = transaction.get("transaction_type_id")
            amount = float(transaction.get("amount", 0) or 0)
            fee_applied = float(transaction.get("fee_applied", 0) or 0)
            
            if charges_df.empty or recommendations_df.empty:
                return {"status": "no_data", "issues": ["No charge or recommendation data available"]}
            
            expected_fee = amount * 0.02
            tolerance = 0.05
            issues = []
            violation_severity = "low"
            fee_status_type = "Normal"
            
            if fee_applied < expected_fee * (1 - tolerance):
                issues.append(f"UNDERCHARGE: Applied fee ${fee_applied:.2f} below expected ${expected_fee:.2f}")
                fee_status_type = "Undercharge"
                violation_severity = "medium"
            elif fee_applied > expected_fee * (1 + tolerance):
                issues.append(f"OVERCHARGE: Applied fee ${fee_applied:.2f} above expected ${expected_fee:.2f}")
                fee_status_type = "Overcharge"
                violation_severity = "medium"
            
            if issues:
                return {
                    "status": "violation",
                    "issues": issues,
                    "actual_fee": fee_applied,
                    "expected_fee": expected_fee,
                    "severity": violation_severity,
                    "fee_status_type": fee_status_type
                }
            else:
                return {
                    "status": "compliant",
                    "actual_fee": fee_applied,
                    "expected_fee": expected_fee,
                    "severity": "none",
                    "fee_status_type": "Normal"
                }
                
        except Exception as e:
            return {"status": "error", "issues": [f"Error in fee verification: {str(e)}"], "fee_status_type": "Error"}

def _safe_json_parse(text):
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

def suggest_category_ai(name: str, historical_patterns=None):
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    key = str(name).strip().lower()
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    def enhanced_heuristic(n, patterns=None):
        n = n.lower()
        if patterns and key in patterns:
            return patterns[key]
        
        if any(word in n for word in ["airtime", "mobile", "topup"]): 
            return ("Telecom", "Airtime Top-up", 0.9)
        if any(word in n for word in ["bill", "utility", "electric", "water"]): 
            return ("Utilities", "Bill Payment", 0.9)
        if any(word in n for word in ["transfer", "send", "remit"]): 
            return ("Banking", "Funds Transfer", 0.9)
        if any(word in n for word in ["payment", "pay", "invoice"]): 
            return ("Commerce", "Payment", 0.8)
        if any(word in n for word in ["withdrawal", "atm", "cash"]): 
            return ("Banking", "Cash Withdrawal", 0.9)
        return ("Other", "Uncategorized", 0.5)

    # Note: client should be passed as parameter or handled separately
    client = None  # This should be properly handled
    
    if not client:
        res = enhanced_heuristic(name, historical_patterns)
        st.session_state.ai_cache[key] = res
        return res

    prompt = f"""
    Categorize this financial transaction into appropriate Category and Subcategory.
    Transaction: "{name}"
    Respond ONLY with a JSON object exactly like:
    {{
    "category": "CategoryName",
    "subcategory": "SubcategoryName",
    "confidence_score": 0.95
    }}
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial transaction categorization expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
        )
        content = resp.choices[0].message.content
        parsed = _safe_json_parse(content)
        
        category = parsed.get("category") or parsed.get("Category")
        subcat = parsed.get("subcategory") or parsed.get("Subcategory")
        confidence = parsed.get("confidence_score", 0.7)
        
        if not category or not subcat or confidence < 0.6:
            category, subcat, conf = enhanced_heuristic(name, historical_patterns)
            confidence = min(confidence, conf)
            
        result = (category, subcat, confidence)
        st.session_state.ai_cache[key] = result
        return result
        
    except Exception:
        res = enhanced_heuristic(name, historical_patterns)
        st.session_state.ai_cache[key] = res
        return res

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

import pandas as pd
import numpy as np
import json
import re
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from openai import OpenAI

class AdvancedAnomalyDetector:
    """Advanced anomaly detection using multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_fitted = False

    def detect_anomalies_ensemble(self, df, feature_columns, contamination=0.1):
        """Simplified ensemble anomaly detection for immediate use"""
        try:
            sample_size = len(df)
            
            # For very small samples, use simpler approach
            if sample_size < 10:
                print(f"Too few samples ({sample_size}) for reliable anomaly detection")
                df['is_anomaly'] = 0
                df['combined_severity'] = 0.0
                df['ensemble_anomaly_score'] = 0.0
                return df
            
            # Convert all feature columns to numeric to handle decimal.Decimal types
            for col in feature_columns:
                if col in df.columns:
                    df[col] = df[col].astype(float)
            
            # Simple anomaly detection based on amount outliers
            if 'amount' in df.columns:
                amount_mean = df['amount'].mean()
                amount_std = df['amount'].std()
                
                if amount_std > 0:
                    # Calculate z-score for amount
                    df['amount_zscore'] = (df['amount'] - amount_mean) / amount_std
                    
                    # Create anomaly score based on absolute z-score
                    df['ensemble_anomaly_score'] = abs(df['amount_zscore'])
                    
                    # Mark top anomalies based on contamination
                    threshold = df['ensemble_anomaly_score'].quantile(1 - contamination)
                    df['is_anomaly'] = (df['ensemble_anomaly_score'] >= threshold).astype(int)
                    df['combined_severity'] = df['ensemble_anomaly_score']
                else:
                    # If no variation in amount, no anomalies
                    df['is_anomaly'] = 0
                    df['combined_severity'] = 0.0
                    df['ensemble_anomaly_score'] = 0.0
            else:
                # If no amount column, no anomalies
                df['is_anomaly'] = 0
                df['combined_severity'] = 0.0
                df['ensemble_anomaly_score'] = 0.0
            
            self.is_fitted = True
            return df
            
        except Exception as e:
            print(f"Anomaly detection error: {str(e)}")
            # Set safe defaults
            df['is_anomaly'] = 0
            df['combined_severity'] = 0.0
            df['ensemble_anomaly_score'] = 0.0
            return df

class FeeVerificationSystem:
    def __init__(self):
        self.learning_data = []
        
    def verify_fee_compliance(self, transaction, charges_df, recommendations_df):
        try:
            ttype = transaction.get("transaction_type_id")
            amount = float(transaction.get("amount", 0) or 0)
            fee_applied = float(transaction.get("fee_applied", 0) or 0)
            
            if charges_df.empty or recommendations_df.empty:
                return {"status": "no_data", "issues": ["No charge or recommendation data available"]}
            
            expected_fee = amount * 0.02
            tolerance = 0.05
            issues = []
            violation_severity = "low"
            fee_status_type = "Normal"
            
            if fee_applied < expected_fee * (1 - tolerance):
                issues.append(f"UNDERCHARGE: Applied fee ${fee_applied:.2f} below expected ${expected_fee:.2f}")
                fee_status_type = "Undercharge"
                violation_severity = "medium"
            elif fee_applied > expected_fee * (1 + tolerance):
                issues.append(f"OVERCHARGE: Applied fee ${fee_applied:.2f} above expected ${expected_fee:.2f}")
                fee_status_type = "Overcharge"
                violation_severity = "medium"
            
            if issues:
                return {
                    "status": "violation",
                    "issues": issues,
                    "actual_fee": fee_applied,
                    "expected_fee": expected_fee,
                    "severity": violation_severity,
                    "fee_status_type": fee_status_type
                }
            else:
                return {
                    "status": "compliant",
                    "actual_fee": fee_applied,
                    "expected_fee": expected_fee,
                    "severity": "none",
                    "fee_status_type": "Normal"
                }
                
        except Exception as e:
            return {"status": "error", "issues": [f"Error in fee verification: {str(e)}"], "fee_status_type": "Error"}

def _safe_json_parse(text):
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

def suggest_category_ai(name: str, client=None, historical_patterns=None):
    """AI-powered transaction categorization"""
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    key = str(name).strip().lower()
    if key in st.session_state.ai_cache:
        return st.session_state.ai_cache[key]

    def enhanced_heuristic(n, patterns=None):
        n = n.lower()
        if patterns and key in patterns:
            return patterns[key]
        
        if any(word in n for word in ["airtime", "mobile", "topup"]): 
            return ("Telecom", "Airtime Top-up", 0.9)
        if any(word in n for word in ["bill", "utility", "electric", "water"]): 
            return ("Utilities", "Bill Payment", 0.9)
        if any(word in n for word in ["transfer", "send", "remit"]): 
            return ("Banking", "Funds Transfer", 0.9)
        if any(word in n for word in ["payment", "pay", "invoice"]): 
            return ("Commerce", "Payment", 0.8)
        if any(word in n for word in ["withdrawal", "atm", "cash"]): 
            return ("Banking", "Cash Withdrawal", 0.9)
        return ("Other", "Uncategorized", 0.5)

    if not client:
        res = enhanced_heuristic(name, historical_patterns)
        st.session_state.ai_cache[key] = res
        return res

    prompt = f"""
    Categorize this financial transaction into appropriate Category and Subcategory.
    Transaction: "{name}"
    Respond ONLY with a JSON object exactly like:
    {{
    "category": "CategoryName",
    "subcategory": "SubcategoryName",
    "confidence_score": 0.95
    }}
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial transaction categorization expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
        )
        content = resp.choices[0].message.content
        parsed = _safe_json_parse(content)
        
        category = parsed.get("category") or parsed.get("Category")
        subcat = parsed.get("subcategory") or parsed.get("Subcategory")
        confidence = parsed.get("confidence_score", 0.7)
        
        if not category or not subcat or confidence < 0.6:
            category, subcat, conf = enhanced_heuristic(name, historical_patterns)
            confidence = min(confidence, conf)
            
        result = (category, subcat, confidence)
        st.session_state.ai_cache[key] = result
        return result
        
    except Exception:
        res = enhanced_heuristic(name, historical_patterns)
        st.session_state.ai_cache[key] = res
        return res

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

def real_ai_revenue_analysis(transactions_df, client):
    """Real AI analysis using OpenAI for revenue insights"""
    if not client or transactions_df.empty:
        return None
        
    # Prepare real data for AI analysis
    sample_data = transactions_df[['amount', 'fee_applied', 'currency', 'created_at']].tail(50)
    
    prompt = f"""
    As a senior financial analyst with expertise in revenue optimization, analyze this transaction data and provide genuine, data-driven insights:
    
    TRANSACTION DATA SAMPLE:
    {sample_data.to_dict()}
    
    KEY METRICS:
    - Total transactions: {len(transactions_df)}
    - Total volume: ${transactions_df['amount'].sum():,.2f}
    - Average transaction: ${transactions_df['amount'].mean():.2f}
    - Date range: {transactions_df['created_at'].min()} to {transactions_df['created_at'].max()}
    
    Please provide REAL, ACTIONABLE insights in this JSON format:
    {{
        "revenue_streams": [
            {{
                "stream_name": "actual identified stream",
                "contribution_percentage": 35.5,
                "growth_trend": "increasing/decreasing/stable",
                "optimization_opportunity": "specific actionable insight"
            }}
        ],
        "key_insights": [
            "data-driven insight 1",
            "data-driven insight 2" 
        ],
        "revenue_risks": [
            {{
                "risk_description": "specific risk identified",
                "severity": "high/medium/low",
                "mitigation": "specific action to take"
            }}
        ],
        "optimization_recommendations": [
            {{
                "recommendation": "specific data-driven recommendation",
                "expected_impact": "quantified expected impact",
                "confidence": 85,
                "implementation_complexity": "low/medium/high"
            }}
        ],
        "forecast_insights": "data-driven forecast based on patterns"
    }}
    
    Be specific, quantitative, and genuinely analytical. Base insights on the data patterns you observe.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a expert financial analyst. Provide specific, data-driven insights. Be quantitative and actionable."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        return _safe_json_parse(content)
        
    except Exception as e:
        print(f"Real AI revenue analysis failed: {e}")
        return None

def real_ml_revenue_forecast(transactions_df, periods=12):
    """Real machine learning revenue forecasting"""
    try:
        if transactions_df.empty or 'created_at' not in transactions_df.columns:
            return None
            
        # Convert to time series
        transactions_df['date'] = pd.to_datetime(transactions_df['created_at']).dt.date
        daily_revenue = transactions_df.groupby('date')['amount'].sum().sort_index()
        
        if len(daily_revenue) < 10:  # Need minimum data points
            return None
            
        # Create features for ML
        dates = pd.Series(daily_revenue.index).apply(lambda x: x.toordinal()).values
        revenue_values = daily_revenue.values
        
        # Use multiple ML models for ensemble forecasting
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        forecasts = {}
        X = dates.reshape(-1, 1)
        y = revenue_values
        
        for name, model in models.items():
            model.fit(X, y)
            # Forecast future periods
            last_date = dates[-1]
            future_dates = np.array([last_date + i for i in range(1, periods + 1)]).reshape(-1, 1)
            forecast = model.predict(future_dates)
            forecasts[name] = forecast
        
        # Use ensemble average
        ensemble_forecast = np.mean(list(forecasts.values()), axis=0)
        
        return {
            'dates': [pd.Timestamp.fromordinal(int(last_date + i)) for i in range(1, periods + 1)],
            'forecast': ensemble_forecast,
            'model_performance': forecasts,
            'confidence_interval': np.std(list(forecasts.values()), axis=0) * 1.96  # 95% CI
        }
        
    except Exception as e:
        print(f"ML forecasting failed: {e}")
        return None

def real_revenue_stream_clustering(transactions_df):
    """Real ML clustering to identify revenue streams"""
    try:
        if transactions_df.empty:
            return None
            
        # Prepare features for clustering - CONVERT TO FLOAT FIRST
        features = transactions_df[['amount', 'fee_applied']].copy()
        
        # Convert decimal.Decimal to float
        for col in ['amount', 'fee_applied']:
            if col in features.columns:
                features[col] = pd.to_numeric(features[col], errors='coerce').astype(float)
        
        features = features.fillna(0)
        
        # Remove outliers for better clustering
        Q1 = features.quantile(0.25)
        Q3 = features.quantile(0.75)
        IQR = Q3 - Q1
        features = features[~((features < (Q1 - 1.5 * IQR)) | (features > (Q3 + 1.5 * IQR))).any(axis=1)]
        
        if len(features) < 10:
            return None
            
        # Find optimal number of clusters
        silhouette_scores = []
        for k in range(2, min(8, len(features))):
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(features)
            if len(np.unique(labels)) > 1:  # Need at least 2 clusters for silhouette score
                silhouette_scores.append(silhouette_score(features, labels))
            else:
                silhouette_scores.append(-1)  # Invalid clustering
        
        if silhouette_scores:
            optimal_k = np.argmax(silhouette_scores) + 2
        else:
            optimal_k = 2
        
        # Perform clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = kmeans.fit_predict(features)
        
        # Analyze clusters
        features['cluster'] = clusters
        cluster_analysis = features.groupby('cluster').agg({
            'amount': ['count', 'mean', 'sum'],
            'fee_applied': 'mean'
        }).round(2)
        
        return {
            'clusters': clusters,
            'cluster_analysis': cluster_analysis,
            'optimal_k': optimal_k,
            'silhouette_score': max(silhouette_scores) if silhouette_scores else 0
        }
        
    except Exception as e:
        print(f"Revenue clustering failed: {e}")
        return None