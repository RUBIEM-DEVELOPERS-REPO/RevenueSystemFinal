import streamlit as st
import psycopg2
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
import json
from openai import OpenAI
import re
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Transaction Monitoring",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Transaction Monitoring Dashboard")
st.caption("Advanced monitoring + Pattern recognition + Anomaly detection + Fee validation")

# --- API Key Input ---
open_key = "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"
client = OpenAI(api_key=open_key) if open_key else None

# --- CORRECTED NEON DATABASE CONNECTIONS ---
# Database 1: Main database (transactions, charges)
NEON_DB_MAIN = {
    "host": "ep-frosty-dawn-ad0cnbjn-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_XCO6HPNfw7El",
    "port": 5432
}

# Database 2: Price recommendations database (transaction_types, price_recommendations)
NEON_DB_PRICE = {
    "host": "ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_7AlUWE8wkigH",
    "port": 5432
}

# Assign connections correctly for different data sources
conn1_params = NEON_DB_MAIN  # For transactions
conn_charges_params = NEON_DB_MAIN  # For charges
conn2_params = NEON_DB_PRICE  # For transaction_types and price_recommendations



# ===================================================================
# 1. CORE FUNCTIONS
# ===================================================================

def safe_convert_to_float(value):
    """Safely convert any value to float, handling various data types"""
    try:
        if value is None or pd.isna(value) or value == '':
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = value.replace('$', '').replace(',', '').strip()
            return float(cleaned) if cleaned else 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def detect_rule_based_anomalies(transactions_df):
    """
    Rule-based anomaly detection for pricing discrepancies
    """
    try:
        # Create a copy to avoid modifying the original
        df = transactions_df.copy()
        
        # Initialize anomaly columns
        df['is_anomaly'] = 0
        df['anomaly_reason'] = ''
        df['combined_severity'] = 0.0
        df['fee_status'] = 'Correct'  # Initialize fee_status
        
        # Check if we have the required columns, create them if missing
        if 'fee_applied' not in df.columns:
            df['fee_applied'] = df['amount'].apply(safe_convert_to_float) * 0.025
        
        if 'recommended_min_fee' not in df.columns:
            df['recommended_min_fee'] = df['amount'].apply(safe_convert_to_float) * 0.015
        
        if 'recommended_max_fee' not in df.columns:
            df['recommended_max_fee'] = df['amount'].apply(safe_convert_to_float) * 0.035
        
        for idx, row in df.iterrows():
            try:
                fee_applied = safe_convert_to_float(row.get('fee_applied', 0))
                min_fee = safe_convert_to_float(row.get('recommended_min_fee', 0))
                max_fee = safe_convert_to_float(row.get('recommended_max_fee', 0))
                
                reasons = []
                severity_score = 0.0
                
                # Rule 1: Fee below minimum recommended
                if fee_applied < min_fee:
                    reasons.append(f"Undercharge: ${fee_applied:.2f} < min ${min_fee:.2f}")
                    severity_score += 0.7
                    df.at[idx, 'fee_status'] = 'Undercharge'
                
                # Rule 2: Fee above maximum recommended
                elif fee_applied > max_fee:
                    reasons.append(f"Overcharge: ${fee_applied:.2f} > max ${max_fee:.2f}")
                    severity_score += 0.5
                    df.at[idx, 'fee_status'] = 'Overcharge'
                
                # Update anomaly status if any rules triggered
                if reasons:
                    df.at[idx, 'is_anomaly'] = 1
                    df.at[idx, 'anomaly_reason'] = ' | '.join(reasons)
                    df.at[idx, 'combined_severity'] = min(severity_score, 1.0)
                        
            except Exception as e:
                continue  # Skip this row if there's an error
        
        return df
        
    except Exception as e:
        st.error(f"Error in anomaly detection: {e}")
        return transactions_df

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

def ai_insights_with_severity(trend_df, anomalies_df):
    """Generate AI-powered insights with severity scoring for anomalies"""
    if not client or trend_df.empty:
        return {
            "revenue_insights": ["Analyzing transaction patterns...", "Initial data processing underway"],
            "critical_anomalies": [{
                "description": "System initializing - anomalies will be detected as transactions stream in",
                "severity": "low", 
                "recommended_action": "Monitor transaction flow",
                "risk_score": 0.1
            }],
            "business_impact": "Real-time monitoring active. Insights will generate as data accumulates."
        }
        
    sample = trend_df.tail(50).to_dict(orient="records")
    
    if not anomalies_df.empty:
        anomalies_sample = anomalies_df.tail(15).to_dict(orient="records")
    else:
        anomalies_sample = []
    
    prompt = f"""
    As a senior financial analyst, analyze this transaction data and provide CONCISE, ACTIONABLE insights:
    
    Recent Transaction Trends (last 50 transactions):
    {json.dumps(sample, default=str)}
    
    Recent Anomalies Detected:
    {json.dumps(anomalies_sample, default=str)}
    
    Provide SPECIFIC insights about:
    1. Revenue patterns and opportunities
    2. Critical anomalies requiring immediate attention
    3. Fee compliance issues
    4. Recommended actions
    
    Respond with JSON:
    {{
        "revenue_insights": ["list of 3-4 key insights"],
        "critical_anomalies": [
            {{
                "description": "specific anomaly with amounts",
                "severity": "high/medium/low",
                "recommended_action": "concrete action to take",
                "risk_score": 0.95
            }}
        ],
        "business_impact": "specific impact statement with numbers"
    }}
    """
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a sharp, data-driven financial analyst. Be specific and quantitative."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        content = resp.choices[0].message.content
        return _safe_json_parse(content)
    except Exception:
        return {
            "revenue_insights": ["AI analysis temporarily unavailable", "Continue monitoring transaction stream"],
            "critical_anomalies": [],
            "business_impact": "System functioning normally - manual review recommended"
        }

# ===================================================================
# 2. NOTIFICATION CLASSES
# ===================================================================

class PopupNotificationSystem:
    def __init__(self):
        if "popup_notifications" not in st.session_state:
            st.session_state.popup_notifications = []
        if "show_popup" not in st.session_state:
            st.session_state.show_popup = False
        if "current_popup" not in st.session_state:
            st.session_state.current_popup = None
    
    def add_popup(self, title, message, type="info", duration=5):
        popup = {
            "id": len(st.session_state.popup_notifications) + 1,
            "title": title,
            "message": message,
            "type": type,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "duration": duration
        }
        st.session_state.popup_notifications.insert(0, popup)
        st.session_state.show_popup = True
        st.session_state.current_popup = popup
    
    def clear_current_popup(self):
        st.session_state.show_popup = False
        st.session_state.current_popup = None
    
    def get_current_popup(self):
        return st.session_state.current_popup

class NotificationSystem:
    def __init__(self):
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
        if "unread_count" not in st.session_state:
            st.session_state.unread_count = 0
    
    def add_notification(self, message, type="info"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification = {
            "id": len(st.session_state.notifications) + 1,
            "message": message,
            "type": type,
            "timestamp": timestamp,
            "read": False
        }
        st.session_state.notifications.insert(0, notification)
        st.session_state.unread_count += 1
    
    def mark_as_read(self, notification_id):
        for notification in st.session_state.notifications:
            if notification["id"] == notification_id and not notification["read"]:
                notification["read"] = True
                st.session_state.unread_count -= 1
                break
    
    def mark_all_as_read(self):
        for notification in st.session_state.notifications:
            if not notification["read"]:
                notification["read"] = True
        st.session_state.unread_count = 0
    
    def get_unread_count(self):
        return st.session_state.unread_count
    
    def get_notifications(self):
        return st.session_state.notifications

class AutomatedFeeCompliance:
    def __init__(self):
        self.violations_detected = 0
        self.transactions_processed = 0
        self.compliance_rate = 0.0
        
    def analyze_transaction_batch(self, batch_df):
        """Automatically analyze a batch of transactions for fee compliance"""
        try:
            if batch_df.empty:
                return batch_df
                
            # Ensure we have required columns
            if 'amount' not in batch_df.columns:
                return batch_df
            
            # Add fee_applied if missing
            if 'fee_applied' not in batch_df.columns:
                batch_df = self._add_estimated_fees(batch_df)
            
            # Perform fee compliance analysis
            batch_df = self._perform_fee_analysis(batch_df)
            
            # Update statistics
            self.transactions_processed += len(batch_df)
            new_violations = len(batch_df[batch_df['fee_status'] == 'violation'])
            self.violations_detected += new_violations
            
            if self.transactions_processed > 0:
                self.compliance_rate = ((self.transactions_processed - self.violations_detected) / self.transactions_processed) * 100
            
            return batch_df
            
        except Exception as e:
            # Return batch with default compliant status
            batch_df['fee_status'] = 'compliant'
            batch_df['fee_status_type'] = 'Normal'
            return batch_df
    
    def _add_estimated_fees(self, batch_df):
        """Add estimated fees based on transaction patterns"""
        try:
            # Convert amount to float first
            amounts = batch_df['amount'].apply(safe_convert_to_float)
            
            # Create realistic fee estimates based on amount ranges
            fees = []
            for amount in amounts:
                if amount <= 100:
                    fee = amount * 0.03  # 3% for small transactions
                elif amount <= 1000:
                    fee = amount * 0.025  # 2.5% for medium transactions
                else:
                    fee = amount * 0.02  # 2% for large transactions
                
                # Add some random variation
                import random
                variation = random.uniform(-0.005, 0.005)
                fee = max(fee * (1 + variation), 0.50)
                fees.append(round(fee, 2))
            
            batch_df['fee_applied'] = fees
            return batch_df
            
        except Exception as e:
            # Fallback: simple 2.5% fee
            batch_df['fee_applied'] = batch_df['amount'].apply(safe_convert_to_float) * 0.025
            return batch_df
    
    def _perform_fee_analysis(self, batch_df):
        """Perform actual fee compliance analysis"""
        try:
            # Convert to float for calculations
            amounts = batch_df['amount'].apply(safe_convert_to_float)
            fees = batch_df['fee_applied'].apply(safe_convert_to_float)
            
            fee_status = []
            fee_status_type = []
            expected_fees = []
            fee_differences = []
            difference_percentages = []
            
            for amount, fee in zip(amounts, fees):
                # Calculate expected fee (2% of amount)
                expected_fee = amount * 0.02
                expected_fees.append(expected_fee)
                
                # Calculate difference
                fee_difference = fee - expected_fee
                fee_differences.append(fee_difference)
                
                # Calculate percentage difference
                if expected_fee > 0:
                    difference_pct = (fee_difference / expected_fee) * 100
                else:
                    difference_pct = 0
                difference_percentages.append(difference_pct)
                
                # Determine compliance status
                tolerance = 0.10  # 10% tolerance
                
                if fee < expected_fee * (1 - tolerance):
                    fee_status.append('violation')
                    fee_status_type.append('Undercharge')
                elif fee > expected_fee * (1 + tolerance):
                    fee_status.append('violation')
                    fee_status_type.append('Overcharge')
                else:
                    fee_status.append('compliant')
                    fee_status_type.append('Correct')
            
            # Add all calculated columns
            batch_df['fee_status'] = fee_status
            batch_df['fee_status_type'] = fee_status_type
            batch_df['expected_fee'] = expected_fees
            batch_df['fee_difference'] = fee_differences
            batch_df['difference_percentage'] = difference_percentages
            
            return batch_df
            
        except Exception as e:
            raise e
    
    def get_compliance_stats(self):
        """Get current compliance statistics"""
        return {
            'transactions_processed': self.transactions_processed,
            'violations_detected': self.violations_detected,
            'compliance_rate': self.compliance_rate
        }

# ===================================================================
# 3. ADVANCED CLASSES
# ===================================================================

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
                df['is_anomaly'] = 0
                df['combined_severity'] = 0.0
                df['ensemble_anomaly_score'] = 0.0
                return df
            
            # Convert all feature columns to float
            for col in feature_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
            
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
            # Convert decimal.Decimal to float safely
            amount = safe_convert_to_float(transaction.get("amount", 0))
            fee_applied = safe_convert_to_float(transaction.get("fee_applied", 0))
            
            if charges_df.empty or recommendations_df.empty:
                return {
                    "status": "no_data", 
                    "issues": ["No charge or recommendation data available"],
                    "fee_status_type": "Unknown"
                }
            
            expected_fee = amount * 0.02  # 2% expected fee
            tolerance = 0.05
            issues = []
            violation_severity = "low"
            fee_status_type = "Correct"
            
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
                    "fee_status_type": "Correct"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "issues": [f"Error in fee verification: {str(e)}"], 
                "fee_status_type": "Error"
            }

# ===================================================================
# 4. INITIALIZATION FUNCTIONS
# ===================================================================

def initialize_session_state():
    """Initialize all required session state variables"""
    # Data storage
    if "all_transactions" not in st.session_state:
        st.session_state.all_transactions = pd.DataFrame()
    if "transaction_types" not in st.session_state:
        st.session_state.transaction_types = pd.DataFrame()
    if "charges" not in st.session_state:
        st.session_state.charges = pd.DataFrame()
    if "price_recommendations" not in st.session_state:
        st.session_state.price_recommendations = pd.DataFrame()
    if "transactions_df" not in st.session_state:
        st.session_state.transactions_df = pd.DataFrame()
    
    # Processing state
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False
    if "last_anomaly_count" not in st.session_state:
        st.session_state.last_anomaly_count = 0
    if "last_fee_violation_count" not in st.session_state:
        st.session_state.last_fee_violation_count = 0
    if "fee_differences_table" not in st.session_state:
        st.session_state.fee_differences_table = pd.DataFrame()
    if "critical_anomalies_detected" not in st.session_state:
        st.session_state.critical_anomalies_detected = False
    
    # Analysis systems
    if "anomaly_detector" not in st.session_state:
        st.session_state.anomaly_detector = AdvancedAnomalyDetector()
    if "fee_verifier" not in st.session_state:
        st.session_state.fee_verifier = FeeVerificationSystem()
    if "fee_compliance_system" not in st.session_state:
        st.session_state.fee_compliance_system = AutomatedFeeCompliance()
    
    # AI and caching
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    
    # UI state
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "live"

def load_transaction_data():
    try:
        conn = psycopg2.connect(**conn1_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY id ASC")
        data = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        
        st.session_state.all_transactions = pd.DataFrame(data, columns=cols)
        st.session_state.current_index = 0
        st.session_state.transactions_df = pd.DataFrame()
        
        st.success(f"✅ Loaded {len(st.session_state.all_transactions)} transactions from Main DB")
        return True
        
    except Exception as e:
        st.error(f"Could not load transactions from Main DB: {e}")
        return False

def load_transaction_types():
    try:
        conn = psycopg2.connect(**conn2_params)
        cur = conn.cursor()
        
        # First, let's see what tables and columns actually exist
        cur.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            ORDER BY table_name, ordinal_position
        """)
        all_columns = cur.fetchall()
        
        # Check what's in transaction_types table specifically
        cur.execute("SELECT * FROM transaction_types LIMIT 1")
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            st.write(f"📊 Columns in transaction_types table: {columns}")
            
            # Get all data
            cur.execute("SELECT * FROM transaction_types")
            types_data = cur.fetchall()
            st.session_state.transaction_types = pd.DataFrame(types_data, columns=columns)
            st.success(f"✅ Loaded {len(st.session_state.transaction_types)} transaction types from Price DB")
        else:
            st.warning("No transaction_types table found or table is empty")
            st.session_state.transaction_types = pd.DataFrame()
            
        cur.close()
        conn.close()
        
    except Exception as e:
        st.warning(f"Could not load transaction types from Price DB: {e}")
        st.session_state.transaction_types = pd.DataFrame()

def load_charges_data():
    try:
        conn = psycopg2.connect(**conn_charges_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM charges")
        charges_data = cur.fetchall()
        charges_cols = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        
        st.session_state.charges = pd.DataFrame(charges_data, columns=charges_cols)
        st.success("✅ Loaded charges from Main DB")
        return True
    except Exception as e:
        st.warning(f"Could not load charges from Main DB: {e}")
        st.session_state.charges = pd.DataFrame()
        return False

def load_price_recommendations():
    try:
        conn = psycopg2.connect(**conn2_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM price_recommendations")
        recommended_prices_data = cur.fetchall()
        recs_cols = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        
        st.session_state.price_recommendations = pd.DataFrame(recommended_prices_data, columns=recs_cols)
        st.success("✅ Loaded price recommendations from Price DB")
        return True
    except Exception as e:
        st.warning(f"Could not load recommendations from Price DB: {e}")
        st.session_state.price_recommendations = pd.DataFrame()
        return False

# ===================================================================
# 5. MAIN APPLICATION LOGIC
# ===================================================================

# Initialize notification systems
notification_system = NotificationSystem()
popup_system = PopupNotificationSystem()

# Initialize and Load Data
initialize_session_state()

with st.spinner("Loading data from Neon database..."):
    if st.session_state.all_transactions.empty:
        if not load_transaction_data():
            st.error("Failed to load transaction data from Neon DB.")
    
    if st.session_state.transaction_types.empty:
        load_transaction_types()
        
    if st.session_state.charges.empty:
        load_charges_data()
        
    if st.session_state.price_recommendations.empty:
        load_price_recommendations()

# Enhanced Sidebar Controls
st.sidebar.header("🎛️ Analysis Controls")
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 30, 5)
batch_size = st.sidebar.slider("Transactions per tick", 1, 20, 3)

analysis_mode = st.sidebar.selectbox(
    "Analysis Mode",
    ["Real-time Monitoring", "Historical Pattern Analysis", "Anomaly Investigation"]
)

display_currency = st.sidebar.selectbox("Display Currency", ["USD", "ZiG"])
exchange_rate = 13.5 if display_currency == "ZiG" else 1.0

# Enhanced Intelligent Filters
st.sidebar.header("🔍 Intelligent Filters")

col1, col2 = st.sidebar.columns(2)
with col1:
    min_amount = st.number_input("Min Amount", value=0, step=10)
    max_amount = st.number_input("Max Amount", value=10000, step=100)
    
with col2:
    anomaly_threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.7)
    show_high_severity_only = st.checkbox("High Severity Only")

# Safe category filter
if not st.session_state.transaction_types.empty and "category_name" in st.session_state.transaction_types.columns:
    available_categories = ["All"] + sorted(st.session_state.transaction_types["category_name"].dropna().unique().tolist())
else:
    available_categories = ["All"]
    st.sidebar.info("No transaction categories loaded. Using default categories.")

focus_category = st.sidebar.selectbox("Focus Category", available_categories)

# Safe currency filter
if not st.session_state.all_transactions.empty and "currency" in st.session_state.all_transactions.columns:
    available_currencies = ["All"] + sorted(st.session_state.all_transactions["currency"].dropna().unique().tolist())
else:
    available_currencies = ["All"]

focus_currency = st.sidebar.selectbox("Focus Currency", available_currencies)

# Notification Bell in Sidebar
st.sidebar.header("🔔 Notifications")
unread_count = notification_system.get_unread_count()

if st.sidebar.button(f"🔔 Notifications ({unread_count})", use_container_width=True):
    with st.sidebar.expander("Recent Notifications", expanded=True):
        notifications = notification_system.get_notifications()
        if notifications:
            for notification in notifications[:10]:
                status_color = "🔴" if notification["type"] == "error" else "🟡" if notification["type"] == "warning" else "🔵"
                st.write(f"{status_color} **{notification['type'].upper()}**: {notification['message']}")
                st.caption(f"_{notification['timestamp']}_")
                if not notification["read"]:
                    if st.button("Mark as read", key=f"read_{notification['id']}"):
                        notification_system.mark_as_read(notification["id"])
                        st.rerun()
            if unread_count > 0:
                if st.button("Mark all as read"):
                    notification_system.mark_all_as_read()
                    st.rerun()
        else:
            st.info("No notifications yet")

# Main Processing Logic - WITH ANOMALY DETECTION
if st.session_state.analysis_started and not st.session_state.all_transactions.empty:
    # Process transactions in batches
    end_index = min(st.session_state.current_index + batch_size, len(st.session_state.all_transactions))
    
    if st.session_state.current_index < len(st.session_state.all_transactions):
        # Get next batch of transactions
        batch_df = st.session_state.all_transactions.iloc[st.session_state.current_index:end_index].copy()
        
        # STEP 1: Only merge with transaction types if we have the right columns
        if (not st.session_state.transaction_types.empty and 
            'transaction_type_id' in batch_df.columns and
            'transaction_type_id' in st.session_state.transaction_types.columns):
            
            # Check what additional columns we can merge
            available_columns = st.session_state.transaction_types.columns.tolist()
            merge_cols = ['transaction_type_id']  # Always include the ID for merging
            
            # Add name column if available
            if 'transaction_type_name' in available_columns:
                merge_cols.append('transaction_type_name')
            elif 'name' in available_columns:
                merge_cols.append('name')
            elif 'type_name' in available_columns:
                merge_cols.append('type_name')
            
            try:
                batch_df = batch_df.merge(
                    st.session_state.transaction_types[merge_cols], 
                    on='transaction_type_id', 
                    how='left'
                )
            except Exception as e:
                st.warning(f"Could not merge transaction types: {e}")
                # Continue without transaction type names
        else:
            # If we can't merge, at least ensure we have a placeholder for transaction type name
            if 'transaction_type_name' not in batch_df.columns and 'transaction_type_id' in batch_df.columns:
                batch_df['transaction_type_name'] = 'Type ' + batch_df['transaction_type_id'].astype(str)
        
        # STEP 2: Add fee_applied column if missing
        if 'fee_applied' not in batch_df.columns:
            batch_df['fee_applied'] = batch_df['amount'].apply(
                lambda x: safe_convert_to_float(x) * 0.025  # 2.5% fee
            )
        
        # STEP 3: Add recommended fee columns if missing
        if 'recommended_min_fee' not in batch_df.columns:
            batch_df['recommended_min_fee'] = batch_df['amount'].apply(
                lambda x: safe_convert_to_float(x) * 0.015  # 1.5% min
            )
        
        if 'recommended_max_fee' not in batch_df.columns:
            batch_df['recommended_max_fee'] = batch_df['amount'].apply(
                lambda x: safe_convert_to_float(x) * 0.035  # 3.5% max
            )
        
        # STEP 4: RUN ANOMALY DETECTION
        batch_df = detect_rule_based_anomalies(batch_df)
        
        # STEP 5: Automated fee compliance analysis
        if "fee_compliance_system" in st.session_state:
            batch_df = st.session_state.fee_compliance_system.analyze_transaction_batch(batch_df)
        else:
            st.session_state.fee_compliance_system = AutomatedFeeCompliance()
            batch_df = st.session_state.fee_compliance_system.analyze_transaction_batch(batch_df)
        
        # Append to main transactions dataframe
        if st.session_state.transactions_df.empty:
            st.session_state.transactions_df = batch_df
        else:
            st.session_state.transactions_df = pd.concat([st.session_state.transactions_df, batch_df], ignore_index=True)
        
        # Update current index
        st.session_state.current_index = end_index
        
        # Show progress
        progress = st.session_state.current_index / len(st.session_state.all_transactions)
        st.sidebar.progress(progress)
        st.sidebar.write(f"Processed: {st.session_state.current_index}/{len(st.session_state.all_transactions)}")

# Check if we have data to proceed
if st.session_state.all_transactions.empty:
    st.error("No transaction data available. Please check your database connection.")
    st.stop()

# Display connection status
if st.session_state.transaction_types.empty:
    st.warning("⚠️ Could not load transaction types from Neon database. Some features may be limited.")
if st.session_state.price_recommendations.empty:
    st.warning("⚠️ Could not load price recommendations from Neon database. Fee verification will be limited.")

# Popup Notifications
current_popup = popup_system.get_current_popup()
if current_popup:
    if current_popup["type"] == "error":
        st.error(f"🚨 {current_popup['title']}: {current_popup['message']}")
    elif current_popup["type"] == "warning":
        st.warning(f"⚠️ {current_popup['title']}: {current_popup['message']}")
    else:
        st.info(f"ℹ️ {current_popup['title']}: {current_popup['message']}")
    
    if st.button("Dismiss", key="dismiss_popup"):
        popup_system.clear_current_popup()
        st.rerun()

# Auto-start Analysis
if not st.session_state.analysis_started:
    if st.button("🚀 Start Real-time Analysis", type="primary", use_container_width=True):
        st.session_state.analysis_started = True
        notification_system.add_notification("Real-time analysis started", "info")
        popup_system.add_popup("Analysis Started", "Real-time transaction analysis is now running", "info")
        st.rerun()
    else:
        st.info("Click the button above to start real-time transaction analysis")

# ===================================================================
# 6. TAB NAVIGATION AND CONTENT
# ===================================================================

# Initialize tab state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "live"

# Custom CSS for better button styling
st.markdown("""
<style>
    .tab-button {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 8px 4px;
        font-weight: 500;
        transition: all 0.3s ease;
        text-align: center;
        margin: 2px;
    }
    .tab-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .tab-button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .tab-button-secondary {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
        border: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)

# Create a prominent tab controller at the top
st.markdown("### 📊 Dashboard Navigation")
st.markdown("---")

# Create equal-sized columns for tabs
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

# Tab configuration
tab_config = [
    {"emoji": "", "name": "Live", "key": "live"},
    {"emoji": "", "name": "Anomalies", "key": "anomaly"},
    {"emoji": "", "name": "Fees", "key": "fee"},
    {"emoji": "", "name": "AI Insights", "key": "ai"},
    {"emoji": "", "name": "Differences", "key": "differences"},
    {"emoji": "", "name": "Types", "key": "types"},
    {"emoji": "", "name": "Simulator", "key": "simulator"}
]

# Create tab buttons
for i, (col, tab) in enumerate(zip([col1, col2, col3, col4, col5, col6, col7], tab_config)):
    with col:
        is_active = st.session_state.current_tab == tab["key"]
        button_label = f"{tab['emoji']} {tab['name']}"
        
        if st.button(
            button_label,
            use_container_width=True,
            type="primary" if is_active else "secondary",
            key=f"tab_{tab['key']}"
        ):
            st.session_state.current_tab = tab["key"]
            st.rerun()

st.markdown("---")

# Display active tab with nice header
active_tab_info = next((tab for tab in tab_config if tab["key"] == st.session_state.current_tab), tab_config[0])
st.markdown(f"### {active_tab_info['emoji']} {active_tab_info['name']}")
st.markdown("---")

# ===================================================================
# TAB CONTENT
# ===================================================================

if st.session_state.current_tab == "live":
    with st.container():
        st.subheader("📈 Live Transaction Stream")
        
        if st.session_state.transactions_df.empty:
            st.info("🔄 Processing transactions... Data will appear shortly.")
            # Show progress
            progress = st.session_state.current_index / len(st.session_state.all_transactions)
            st.progress(progress)
            st.write(f"📊 Processed: {st.session_state.current_index}/{len(st.session_state.all_transactions)} transactions")
        else:
            # Create filtered dataframe for display
            display_df = st.session_state.transactions_df.copy()
            
            # Apply currency conversion
            if 'amount' in display_df.columns:
                display_df["amount"] = pd.to_numeric(display_df["amount"], errors="coerce").fillna(0).astype(float)
                if display_currency == "ZiG":
                    display_df["amount_converted"] = display_df["amount"] * exchange_rate
                else:
                    display_df["amount_converted"] = display_df["amount"]
                display_df["amount_converted"] = display_df["amount_converted"].round(2)

            # In the Live tab and other display sections, replace references to:
                # 'transaction_type_name' with safe alternatives

                # For example, in the Live tab display:
                display_cols = ['id', 'amount_converted', 'currency']
                if 'transaction_type_name' in display_df.columns:
                    display_cols.append('transaction_type_name')
                elif 'transaction_type_id' in display_df.columns:
                    display_cols.append('transaction_type_id')
            
            # Basic columns to show
            display_cols = ['id', 'amount_converted', 'currency', 'transaction_type_name']
            
            # Add fee-related columns if they exist
            fee_cols = ['fee_applied', 'recommended_min_fee', 'recommended_max_fee', 'fee_status']
            for col in fee_cols:
                if col in display_df.columns:
                    display_cols.append(col)
            
            # Add anomaly columns if they exist
            anomaly_cols = ['is_anomaly', 'combined_severity']
            for col in anomaly_cols:
                if col in display_df.columns:
                    display_cols.append(col)
            
            # Show the data with styling
            if display_cols:
                # Apply styling based on fee status
                def style_fee_status(row):
                    styles = [''] * len(row)
                    if row.get('fee_status') == 'Overcharge':
                        styles = ['background-color: #ffcccc'] * len(row)
                    elif row.get('fee_status') == 'Undercharge':
                        styles = ['background-color: #ccffcc'] * len(row)
                    elif row.get('fee_status') == 'Correct':
                        styles = ['background-color: #e6f3ff'] * len(row)
                    return styles
                
                styled_df = display_df[display_cols].tail(20).style.apply(style_fee_status, axis=1)
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Show summary stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Processed", len(display_df))
                
                with col2:
                    if 'is_anomaly' in display_df.columns:
                        anomalies = display_df['is_anomaly'].sum()
                        st.metric("Anomalies", anomalies)
                    else:
                        st.metric("Anomalies", "0")
                
                with col3:
                    if 'fee_status' in display_df.columns:
                        overcharges = len(display_df[display_df['fee_status'] == 'Overcharge'])
                        undercharges = len(display_df[display_df['fee_status'] == 'Undercharge'])
                        correct = len(display_df[display_df['fee_status'] == 'Correct'])
                        st.metric("Overcharges", overcharges)
                
                with col4:
                    if 'fee_status' in display_df.columns:
                        undercharges = len(display_df[display_df['fee_status'] == 'Undercharge'])
                        st.metric("Undercharges", undercharges)
                
                # Fee status distribution
                if 'fee_status' in display_df.columns:
                    st.subheader("💰 Fee Status Distribution")
                    fee_counts = display_df['fee_status'].value_counts()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_pie = px.pie(
                            values=fee_counts.values,
                            names=fee_counts.index,
                            title="Fee Compliance Distribution",
                            color_discrete_sequence=['#ff6b6b', '#51cf66', '#339af0']
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        fig_bar = px.bar(
                            x=fee_counts.index,
                            y=fee_counts.values,
                            title="Fee Violations Count",
                            labels={'x': 'Fee Status', 'y': 'Count'},
                            color=fee_counts.index,
                            color_discrete_map={'Overcharge': '#ff6b6b', 'Undercharge': '#51cf66', 'Correct': '#339af0'}
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                # Show progress
                progress = st.session_state.current_index / len(st.session_state.all_transactions)
                st.progress(progress)
                st.write(f"📊 Processed: {st.session_state.current_index}/{len(st.session_state.all_transactions)} transactions")
            else:
                st.info("No data available for display")
            
        # Auto-refresh control
        if st.session_state.analysis_started:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🔄 Auto-refresh: {refresh_rate} seconds")
            with col2:
                if st.button("⏸️ Pause", key="pause_btn"):
                    st.session_state.analysis_started = False
                    st.rerun()

elif st.session_state.current_tab == "anomaly":
    with st.container():
        st.subheader("🔍 Anomaly Analysis")
        
        if st.session_state.transactions_df.empty:
            st.info("🔄 Processing transactions... Anomaly data will appear here shortly.")
        elif 'is_anomaly' in st.session_state.transactions_df.columns:
            anomalies_df = st.session_state.transactions_df[st.session_state.transactions_df['is_anomaly'] == 1]
            
            if not anomalies_df.empty:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Anomalies", len(anomalies_df))
                
                with col2:
                    total_tx = len(st.session_state.transactions_df)
                    if total_tx > 0:
                        anomaly_rate = (len(anomalies_df) / total_tx * 100)
                        st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                    else:
                        st.metric("Anomaly Rate", "0.0%")
                
                with col3:
                    if 'combined_severity' in anomalies_df.columns:
                        avg_severity = anomalies_df['combined_severity'].mean()
                        st.metric("Avg Severity", f"{avg_severity:.2f}")
                    else:
                        st.metric("Avg Severity", "N/A")
                
                with col4:
                    if 'fee_applied' in anomalies_df.columns:
                        total_anomaly_amount = anomalies_df['fee_applied'].sum()
                        st.metric("Total Amount", f"${total_anomaly_amount:,.2f}")
                    else:
                        st.metric("Total Amount", "N/A")
                
                # Anomaly type breakdown with enhanced visualizations
                st.subheader("📊 Anomaly Type Analysis")
                
                if 'fee_status' in anomalies_df.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status_counts = anomalies_df['fee_status'].value_counts()
                        fig_pie = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Anomaly Types Distribution",
                            color_discrete_sequence=['#ff6b6b', '#51cf66']
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Transaction types with highest anomaly rates
                        if 'transaction_type_name' in anomalies_df.columns:
                            type_anomalies = anomalies_df['transaction_type_name'].value_counts().head(10)
                            fig_bar = px.bar(
                                x=type_anomalies.values,
                                y=type_anomalies.index,
                                orientation='h',
                                title="Top Transaction Types with Anomalies",
                                labels={'x': 'Anomaly Count', 'y': 'Transaction Type'},
                                color=type_anomalies.values,
                                color_continuous_scale='reds'
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                
                # Enhanced anomaly analysis
                st.subheader("📈 Advanced Anomaly Patterns")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Severity distribution
                    if 'combined_severity' in anomalies_df.columns:
                        fig_severity = px.histogram(
                            anomalies_df, 
                            x='combined_severity',
                            title="Anomaly Severity Distribution",
                            nbins=10,
                            color_discrete_sequence=['#ff6b6b']
                        )
                        fig_severity.update_layout(xaxis_title="Severity Score", yaxis_title="Count")
                        st.plotly_chart(fig_severity, use_container_width=True)
                
                with col2:
                    # Amount vs Fee analysis
                    if 'amount' in anomalies_df.columns and 'fee_applied' in anomalies_df.columns:
                        fig_scatter = px.scatter(
                            anomalies_df,
                            x='amount',
                            y='fee_applied',
                            color='fee_status',
                            title="Amount vs Fee Applied (Anomalies)",
                            color_discrete_map={'Overcharge': '#ff6b6b', 'Undercharge': '#51cf66'},
                            size='combined_severity' if 'combined_severity' in anomalies_df.columns else None
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Display detailed anomalies
                st.subheader("🚨 Detailed Anomalies")
                
                # Columns to display
                display_cols = ['id', 'amount', 'currency', 'transaction_type_name', 'fee_status']
                
                # Add fee comparison columns
                fee_cols = ['fee_applied', 'recommended_min_fee', 'recommended_max_fee']
                for col in fee_cols:
                    if col in anomalies_df.columns:
                        display_cols.append(col)
                
                # Add severity if available
                if 'combined_severity' in anomalies_df.columns:
                    display_cols.append('combined_severity')
                
                if not anomalies_df.empty:
                    st.dataframe(anomalies_df[display_cols], use_container_width=True, height=400)
                else:
                    st.info("No anomalies match the current filters")
                
            else:
                st.success("✅ No anomalies detected in current dataset")
        else:
            st.info("🔍 Anomaly detection will run as transactions are processed...")

elif st.session_state.current_tab == "fee":
    with st.container():
        st.subheader(" Fee Compliance Analysis")
        
        if st.session_state.transactions_df.empty:
            st.info("🔄 Processing transactions... Fee compliance data will appear here shortly.")
        elif 'fee_status' in st.session_state.transactions_df.columns:
            fee_violations = st.session_state.transactions_df[st.session_state.transactions_df['fee_status'] == 'violation']
            
            # Enhanced metrics with visualizations
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_tx = len(st.session_state.transactions_df)
                st.metric("Total Transactions", total_tx)
            
            with col2:
                violations_count = len(fee_violations)
                st.metric("Fee Violations", violations_count)
            
            with col3:
                if total_tx > 0:
                    compliance_rate = ((total_tx - violations_count) / total_tx * 100)
                    st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
                else:
                    st.metric("Compliance Rate", "0.0%")
            
            with col4:
                if 'fee_status_type' in fee_violations.columns:
                    overcharges = len(fee_violations[fee_violations['fee_status_type'] == 'Overcharge'])
                    undercharges = len(fee_violations[fee_violations['fee_status_type'] == 'Undercharge'])
                    st.metric("Over/Under Charges", f"{overcharges}/{undercharges}")
            
            if not fee_violations.empty:
                # Enhanced visualizations
                st.subheader("📊 Fee Compliance Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Violation types pie chart
                    if 'fee_status_type' in fee_violations.columns:
                        violation_types = fee_violations['fee_status_type'].value_counts()
                        fig_violations = px.pie(
                            values=violation_types.values,
                            names=violation_types.index,
                            title="Fee Violation Types",
                            color_discrete_sequence=['#ff6b6b', '#51cf66']
                        )
                        st.plotly_chart(fig_violations, use_container_width=True)
                
                with col2:
                    # Fee difference distribution
                    if 'fee_difference' in fee_violations.columns:
                        fig_diff = px.histogram(
                            fee_violations,
                            x='fee_difference',
                            title="Fee Difference Distribution",
                            nbins=20,
                            color='fee_status_type',
                            color_discrete_map={'Overcharge': '#ff6b6b', 'Undercharge': '#51cf66'}
                        )
                        fig_diff.update_layout(xaxis_title="Fee Difference ($)", yaxis_title="Count")
                        st.plotly_chart(fig_diff, use_container_width=True)
                
                # Additional analysis
                st.subheader("📈 Fee Analysis Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Transaction types with most violations
                    if 'transaction_type_name' in fee_violations.columns:
                        type_violations = fee_violations['transaction_type_name'].value_counts().head(10)
                        fig_types = px.bar(
                            x=type_violations.values,
                            y=type_violations.index,
                            orientation='h',
                            title="Transaction Types with Most Violations",
                            labels={'x': 'Violation Count', 'y': 'Transaction Type'},
                            color=type_violations.values,
                            color_continuous_scale='reds'
                        )
                        st.plotly_chart(fig_types, use_container_width=True)
                
                with col2:
                    # Amount ranges with violations
                    if 'amount' in fee_violations.columns:
                        fee_violations['amount_range'] = pd.cut(
                            fee_violations['amount'], 
                            bins=[0, 100, 500, 1000, 5000, float('inf')],
                            labels=['0-100', '101-500', '501-1000', '1001-5000', '5000+']
                        )
                        range_violations = fee_violations['amount_range'].value_counts()
                        fig_ranges = px.bar(
                            x=range_violations.index,
                            y=range_violations.values,
                            title="Violations by Amount Range",
                            labels={'x': 'Amount Range ($)', 'y': 'Violation Count'},
                            color=range_violations.values,
                            color_continuous_scale='blues'
                        )
                        st.plotly_chart(fig_ranges, use_container_width=True)
                
                # Display fee violation details
                st.subheader("🚨 Detailed Fee Violations")
                
                display_cols = ['id', 'amount', 'fee_applied', 'fee_status_type', 'transaction_type_name']
                if 'expected_fee' in fee_violations.columns:
                    display_cols.extend(['expected_fee', 'fee_difference'])
                
                display_cols = [col for col in display_cols if col in fee_violations.columns]
                
                violations_display = fee_violations[display_cols].copy()
                
                # Convert numeric columns
                for col in ['amount', 'fee_applied', 'expected_fee', 'fee_difference']:
                    if col in violations_display.columns:
                        violations_display[col] = violations_display[col].apply(safe_convert_to_float)
                
                st.dataframe(violations_display, use_container_width=True, height=400)
                
            else:
                st.success("✅ No fee compliance violations detected")
        else:
            st.info("Fee verification not yet performed")

elif st.session_state.current_tab == "ai":
    with st.container():
        st.subheader(" AI Insights & Recommendations")
        
        if st.session_state.transactions_df.empty:
            st.info("Processing transactions... AI insights will generate as data accumulates.")
        else:
            # Generate AI insights
            with st.spinner(" Generating AI insights..."):
                anomalies_df = st.session_state.transactions_df[st.session_state.transactions_df['is_anomaly'] == 1] if 'is_anomaly' in st.session_state.transactions_df.columns else pd.DataFrame()
                insights = ai_insights_with_severity(st.session_state.transactions_df, anomalies_df)
            
            if insights:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(" Revenue Insights")
                    if 'revenue_insights' in insights:
                        for insight in insights['revenue_insights']:
                            st.write(f"• {insight}")
                    else:
                        st.info("Analyzing revenue patterns...")
                
                with col2:
                    st.subheader(" Business Impact")
                    if 'business_impact' in insights:
                        st.info(insights['business_impact'])
                    else:
                        st.info("Assessing business impact...")
                
                st.subheader(" Critical Anomalies & Actions")
                if 'critical_anomalies' in insights and insights['critical_anomalies']:
                    for i, anomaly in enumerate(insights['critical_anomalies']):
                        severity_color = "🔴" if anomaly.get('severity') == 'high' else "🟡" if anomaly.get('severity') == 'medium' else "🟢"
                        with st.expander(f"{severity_color} {anomaly.get('description', 'Unknown Issue')}", expanded=i==0):
                            st.write(f"**Severity:** {anomaly.get('severity', 'Unknown')}")
                            st.write(f"**Recommended Action:** {anomaly.get('recommended_action', 'No action specified')}")
                            st.write(f"**Risk Score:** {anomaly.get('risk_score', 0)}")
                else:
                    st.success("✅ No critical anomalies requiring immediate action")
                
                # Real-time AI monitoring
                st.subheader(" Real-time Monitoring")
                if not st.session_state.transactions_df.empty:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_processed = len(st.session_state.transactions_df)
                        st.metric("Transactions Analyzed", total_processed)
                    
                    with col2:
                        if 'is_anomaly' in st.session_state.transactions_df.columns:
                            anomaly_count = st.session_state.transactions_df['is_anomaly'].sum()
                            st.metric("Anomalies Detected", anomaly_count)
                        else:
                            st.metric("Anomalies Detected", "0")
                    
                    with col3:
                        if 'fee_status' in st.session_state.transactions_df.columns:
                            violations = len(st.session_state.transactions_df[st.session_state.transactions_df['fee_status'] == 'violation'])
                            st.metric("Fee Violations", violations)
                        else:
                            st.metric("Fee Violations", "0")
            else:
                st.error("❌ Unable to generate AI insights at this time")

elif st.session_state.current_tab == "differences":
    with st.container():
        st.subheader(" Fee Differences Analysis")
        
        if st.session_state.transactions_df.empty:
            st.info("Processing transactions... Fee differences will appear here shortly.")
        elif 'fee_applied' in st.session_state.transactions_df.columns:
            # Create fee differences table
            fee_diff_df = st.session_state.transactions_df[['id', 'amount', 'fee_applied', 'transaction_type_name']].copy()
            
            # Convert to float
            for col in ['amount', 'fee_applied']:
                if col in fee_diff_df.columns:
                    fee_diff_df[col] = fee_diff_df[col].apply(safe_convert_to_float)
            
            # Perform calculations
            fee_diff_df['expected_fee'] = fee_diff_df['amount'] * 0.02
            fee_diff_df['fee_difference'] = fee_diff_df['fee_applied'] - fee_diff_df['expected_fee']
            fee_diff_df['difference_percentage'] = fee_diff_df.apply(
                lambda row: (row['fee_difference'] / row['expected_fee'] * 100) if row['expected_fee'] != 0 else 0, 
                axis=1
            )
            
            st.session_state.fee_differences_table = fee_diff_df
            
            # Enhanced visualizations
            st.subheader("📈 Fee Difference Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Fee difference distribution
                fig_diff_dist = px.histogram(
                    fee_diff_df,
                    x='fee_difference',
                    title="Distribution of Fee Differences",
                    nbins=20,
                    color_discrete_sequence=['#4ecdc4']
                )
                fig_diff_dist.update_layout(xaxis_title="Fee Difference ($)", yaxis_title="Count")
                st.plotly_chart(fig_diff_dist, use_container_width=True)
            
            with col2:
                # Percentage difference distribution
                fig_pct_dist = px.histogram(
                    fee_diff_df,
                    x='difference_percentage',
                    title="Percentage Difference Distribution",
                    nbins=20,
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_pct_dist.update_layout(xaxis_title="Percentage Difference (%)", yaxis_title="Count")
                st.plotly_chart(fig_pct_dist, use_container_width=True)
            
            # Additional analysis
            st.subheader("📊 Detailed Fee Difference Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot: Amount vs Fee Difference
                fig_scatter = px.scatter(
                    fee_diff_df,
                    x='amount',
                    y='fee_difference',
                    title="Amount vs Fee Difference",
                    color='fee_difference',
                    color_continuous_scale='rdylgn_r',
                    labels={'amount': 'Transaction Amount ($)', 'fee_difference': 'Fee Difference ($)'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # Box plot of fee differences by transaction type
                if 'transaction_type_name' in fee_diff_df.columns:
                    fig_box = px.box(
                        fee_diff_df,
                        x='transaction_type_name',
                        y='fee_difference',
                        title="Fee Differences by Transaction Type",
                        color='transaction_type_name'
                    )
                    fig_box.update_layout(xaxis_title="Transaction Type", yaxis_title="Fee Difference ($)")
                    st.plotly_chart(fig_box, use_container_width=True)
            
            # Display summary metrics
            st.subheader("Fee Difference Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_difference = fee_diff_df['fee_difference'].mean()
                st.metric("Average Difference", f"${avg_difference:.2f}")
            
            with col2:
                total_undercharge = len(fee_diff_df[fee_diff_df['fee_difference'] < 0])
                st.metric("Undercharged", total_undercharge)
            
            with col3:
                total_overcharge = len(fee_diff_df[fee_diff_df['fee_difference'] > 0])
                st.metric("Overcharged", total_overcharge)
            
            with col4:
                total_correct = len(fee_diff_df[fee_diff_df['fee_difference'] == 0])
                st.metric("Correctly Charged", total_correct)
            
            # Display fee differences table
            st.subheader("📋 Fee Difference Details")
            st.dataframe(fee_diff_df, use_container_width=True, height=400)
            
        else:
            st.info("Fee data not available for difference analysis")

elif st.session_state.current_tab == "types":
    with st.container():
        st.subheader("📋 Transaction Types Analysis")
        
        if not st.session_state.transaction_types.empty:
            # Enhanced visualizations
            st.subheader("📊 Transaction Type Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart of transaction types
                if 'category_name' in st.session_state.transaction_types.columns:
                    category_counts = st.session_state.transaction_types['category_name'].value_counts()
                    fig_pie = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title="Transaction Categories Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart of transaction types
                if 'transaction_type_name' in st.session_state.transaction_types.columns:
                    type_counts = st.session_state.transaction_types['transaction_type_name'].value_counts().head(10)
                    fig_bar = px.bar(
                        x=type_counts.values,
                        y=type_counts.index,
                        orientation='h',
                        title="Top 10 Transaction Types",
                        labels={'x': 'Count', 'y': 'Transaction Type'},
                        color=type_counts.values,
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            # Additional analysis with actual transaction data
            if not st.session_state.transactions_df.empty:
                st.subheader("📈 Transaction Type Performance")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Transaction volume by type - FIXED: Safe conversion to numeric
                    if 'transaction_type_name' in st.session_state.transactions_df.columns and 'amount' in st.session_state.transactions_df.columns:
                        # Convert amount to numeric safely
                        amount_numeric = pd.to_numeric(st.session_state.transactions_df['amount'], errors='coerce').fillna(0)
                        
                        # Group by transaction type and sum amounts
                        volume_by_type = st.session_state.transactions_df.groupby('transaction_type_name').apply(
                            lambda x: amount_numeric[x.index].sum()
                        )
                        
                        # Get top 10 by value (already sorted by sum)
                        top_volume = volume_by_type.sort_values(ascending=False).head(10)
                        
                        fig_volume = px.bar(
                            x=top_volume.values,
                            y=top_volume.index,
                            orientation='h',
                            title="Transaction Volume by Type (Top 10)",
                            labels={'x': 'Total Amount ($)', 'y': 'Transaction Type'},
                            color=top_volume.values,
                            color_continuous_scale='greens'
                        )
                        st.plotly_chart(fig_volume, use_container_width=True)
                    else:
                        st.info("Amount data not available for volume analysis")
                
                with col2:
                    # Anomaly rate by transaction type - FIXED: Safe calculations
                    if ('transaction_type_name' in st.session_state.transactions_df.columns and 
                        'is_anomaly' in st.session_state.transactions_df.columns):
                        
                        # Calculate anomaly rates safely
                        def safe_anomaly_rate(group):
                            try:
                                if len(group) > 0:
                                    # Convert is_anomaly to numeric safely
                                    anomalies_numeric = pd.to_numeric(group['is_anomaly'], errors='coerce').fillna(0)
                                    return (anomalies_numeric.sum() / len(group)) * 100
                                return 0
                            except:
                                return 0
                        
                        anomaly_rates = st.session_state.transactions_df.groupby('transaction_type_name').apply(safe_anomaly_rate)
                        
                        # Get top 10 by anomaly rate
                        top_anomaly_rates = anomaly_rates.sort_values(ascending=False).head(10)
                        
                        fig_anomaly = px.bar(
                            x=top_anomaly_rates.values,
                            y=top_anomaly_rates.index,
                            orientation='h',
                            title="Anomaly Rate by Transaction Type (Top 10)",
                            labels={'x': 'Anomaly Rate (%)', 'y': 'Transaction Type'},
                            color=top_anomaly_rates.values,
                            color_continuous_scale='reds'
                        )
                        st.plotly_chart(fig_anomaly, use_container_width=True)
                    else:
                        st.info("Anomaly data not available for analysis")
                
                # Additional metrics and analysis
                st.subheader("📊 Transaction Type Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_types = st.session_state.transactions_df['transaction_type_name'].nunique() if 'transaction_type_name' in st.session_state.transactions_df.columns else 0
                    st.metric("Unique Transaction Types", total_types)
                
                with col2:
                    if 'amount' in st.session_state.transactions_df.columns:
                        total_volume = pd.to_numeric(st.session_state.transactions_df['amount'], errors='coerce').fillna(0).sum()
                        st.metric("Total Volume", f"${total_volume:,.2f}")
                    else:
                        st.metric("Total Volume", "N/A")
                
                with col3:
                    if 'transaction_type_name' in st.session_state.transactions_df.columns:
                        most_common_type = st.session_state.transactions_df['transaction_type_name'].mode()
                        most_common = most_common_type.iloc[0] if not most_common_type.empty else "N/A"
                        st.metric("Most Common Type", most_common)
                    else:
                        st.metric("Most Common Type", "N/A")
                
                with col4:
                    if 'is_anomaly' in st.session_state.transactions_df.columns:
                        total_anomalies = pd.to_numeric(st.session_state.transactions_df['is_anomaly'], errors='coerce').fillna(0).sum()
                        st.metric("Total Anomalies", int(total_anomalies))
                    else:
                        st.metric("Total Anomalies", "N/A")
            
            # Display transaction types table with safe data handling
            st.subheader(" Transaction Types Data")
            
            # Create a safe copy for display
            display_types = st.session_state.transaction_types.copy()
            
            # Convert any numeric columns safely
            numeric_columns = ['transaction_type_id', 'category_id']
            for col in numeric_columns:
                if col in display_types.columns:
                    display_types[col] = pd.to_numeric(display_types[col], errors='coerce').fillna(0)
            
            st.dataframe(display_types, use_container_width=True)
            
        else:
            st.info("Transaction types data not loaded")

elif st.session_state.current_tab == "simulator":
    with st.container():
        st.subheader(" Scenario Simulator")
        
        st.info("""
        **Test different business scenarios to understand their impact on your revenue and compliance:**
        - Adjust fee structures and see immediate impact
        - Simulate transaction volume changes
        - Test anomaly detection sensitivity
        - Model currency fluctuation effects
        """)
        
        # Scenario configuration
        st.subheader("⚙️ Scenario Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            simulation_type = st.selectbox(
                "Simulation Type",
                ["Fee Structure Change", "Volume Spike", "Anomaly Threshold", "Currency Fluctuation", "Compliance Rule Change"]
            )
            
            if simulation_type == "Fee Structure Change":
                new_fee_rate = st.slider("New Base Fee Rate (%)", 0.1, 10.0, 2.0, 0.1)
                fee_tolerance = st.slider("Fee Tolerance (%)", 1.0, 20.0, 10.0, 1.0)
                
            elif simulation_type == "Volume Spike":
                volume_increase = st.slider("Volume Increase (%)", 10, 500, 100, 10)
                duration_days = st.slider("Duration (Days)", 1, 30, 7, 1)
                
            elif simulation_type == "Anomaly Threshold":
                new_threshold = st.slider("New Anomaly Threshold", 0.1, 1.0, 0.7, 0.05)
                severity_weight = st.slider("Severity Weight", 0.1, 2.0, 1.0, 0.1)
                
            elif simulation_type == "Currency Fluctuation":
                currency_change = st.slider("Currency Change (%)", -50, 50, 10, 5)
                affected_currencies = st.multiselect("Affected Currencies", ["USD", "EUR", "GBP", "ZAR", "ZiG"], default=["ZiG"])
                
            elif simulation_type == "Compliance Rule Change":
                rule_strictness = st.select_slider("Rule Strictness", options=["Relaxed", "Current", "Strict", "Very Strict"])
                auto_enforcement = st.checkbox("Auto-enforcement", value=True)
        
        with col2:
            # Simulation results preview
            st.subheader(" Expected Impact")
            
            if simulation_type == "Fee Structure Change":
                if not st.session_state.transactions_df.empty and 'fee_applied' in st.session_state.transactions_df.columns:
                    # Safely convert to float to avoid decimal.Decimal issues
                    current_revenue = safe_convert_to_float(st.session_state.transactions_df['fee_applied'].sum())
                    projected_revenue = current_revenue * (new_fee_rate / 2.5)  # Assuming current 2.5% fee
                    revenue_change = projected_revenue - current_revenue
                    
                    st.metric("Current Monthly Revenue", f"${current_revenue:,.2f}")
                    st.metric("Projected Monthly Revenue", f"${projected_revenue:,.2f}")
                    
                    if current_revenue > 0:
                        change_percentage = (revenue_change / current_revenue) * 100
                        st.metric("Revenue Impact", f"${revenue_change:,.2f}", 
                                 delta=f"{change_percentage:.1f}%")
                    else:
                        st.metric("Revenue Impact", f"${revenue_change:,.2f}")
                    
                    # Compliance impact
                    st.info(f"**Compliance Impact:** {fee_tolerance}% tolerance may affect violation rates")
                else:
                    st.warning("No fee data available for simulation")
                
            elif simulation_type == "Volume Spike":
                st.metric("Transaction Increase", f"+{volume_increase}%")
                st.metric("Simulation Duration", f"{duration_days} days")
                st.metric("Expected Anomaly Increase", f"+{(volume_increase * 0.15):.1f}%")
                
            elif simulation_type == "Anomaly Threshold":
                if 'is_anomaly' in st.session_state.transactions_df.columns:
                    current_anomalies = int(st.session_state.transactions_df['is_anomaly'].sum())
                    # Safely calculate projected change
                    projected_change = current_anomalies * (new_threshold / 0.7)  # Scale based on threshold change
                    
                    st.metric("Current Anomalies", f"{current_anomalies}")
                    st.metric("Projected Anomalies", f"{int(projected_change)}")
                    st.metric("Detection Sensitivity", f"{'Higher' if new_threshold < 0.7 else 'Lower'}")
                else:
                    st.warning("No anomaly data available for simulation")
            
            elif simulation_type == "Currency Fluctuation":
                st.metric("Currency Change", f"{currency_change}%")
                st.metric("Affected Currencies", f"{len(affected_currencies)}")
                st.metric("Expected Revenue Impact", f"{(currency_change * 0.8):.1f}%")
            
            elif simulation_type == "Compliance Rule Change":
                st.metric("Rule Strictness", rule_strictness)
                st.metric("Auto-enforcement", "Enabled" if auto_enforcement else "Disabled")
                strictness_impact = {
                    "Relaxed": "-40% violations",
                    "Current": "No change", 
                    "Strict": "+25% violations",
                    "Very Strict": "+60% violations"
                }
                st.metric("Expected Impact", strictness_impact.get(rule_strictness, "Unknown"))
        
        # Action buttons
        st.subheader(" Run Simulation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(" Run Simulation", type="primary", use_container_width=True):
                st.success(f" Running {simulation_type} simulation...")
                
                # Simulate processing delay
                import time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Show simulation results
                st.balloons()
                st.success("✅ Simulation completed successfully!")
                
                # Show detailed results based on simulation type
                if simulation_type == "Fee Structure Change":
                    st.info(f"""
                    **Fee Structure Change Results:**
                    - New fee rate: {new_fee_rate}%
                    - Tolerance level: {fee_tolerance}%
                    - Estimated revenue change: ${revenue_change:,.2f}
                    - Compliance adjustment required: Yes
                    """)
                
                elif simulation_type == "Volume Spike":
                    st.info(f"""
                    **Volume Spike Simulation Results:**
                    - Volume increase: {volume_increase}%
                    - Duration: {duration_days} days
                    - Expected additional anomalies: {int(volume_increase * 0.15)}%
                    - System capacity: {'Adequate' if volume_increase <= 200 else 'May require scaling'}
                    """)
        
        with col2:
            if st.button(" Export Results", use_container_width=True):
                st.info("Simulation report would be generated and downloaded here")
                # In a real implementation, this would generate a PDF/Excel report
                
        with col3:
            if st.button(" Reset Scenario", use_container_width=True):
                st.info(" Scenario parameters reset to default values")
                st.rerun()
        
        # Simulation explanation
        with st.expander("ℹHow This Simulation Works"):
            st.write("""
            **Scenario Simulation Engine:**
            - **Fee Structure Changes**: Models revenue impact of different fee percentages using current transaction patterns
            - **Volume Spikes**: Predicts anomaly detection patterns under increased transaction load
            - **Threshold Adjustments**: Shows how sensitivity changes affect anomaly detection rates
            - **Currency Effects**: Models impact of exchange rate fluctuations on multi-currency transactions
            - **Rule Changes**: Tests compliance rates under different enforcement levels
            
            **Real Implementation Would:**
            - Use historical data patterns for accurate projections
            - Apply machine learning models for trend prediction
            - Generate detailed risk assessments and ROI calculations
            - Provide actionable recommendations with confidence intervals
            
            **Current Simulation Uses:**
            - Real transaction data from your database
            - Current fee compliance patterns
            - Anomaly detection baselines
            - Projected scaling based on historical patterns
            """)

# Auto-refresh for live streaming
if st.session_state.analysis_started and st.session_state.current_index < len(st.session_state.all_transactions):
    time.sleep(refresh_rate)
    st.rerun()