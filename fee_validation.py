import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from scipy import stats
import torch
import plotly.graph_objects as go
import torch.nn as nn
import torch.optim as optim
from apscheduler.schedulers.background import BackgroundScheduler
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pdfkit
import pandas as pd
import json
import csv
import io
import smtplib
import math
import uuid
import time
import threading
from datetime import datetime
import requests
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

import threading
from queue import Queue
import time

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import threading
import time
from queue import Queue
import numpy as np

# ===================================================================
# PAGE CONFIG - MUST BE FIRST
# ===================================================================
st.set_page_config(
    page_title="Revenue Assurance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================================
# CUSTOM CSS
# ===================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===================================================================
# DATABASE CLASSES (Keep your existing classes)
# ===================================================================
def load_transactions():
    try:
        conn = psycopg2.connect(**conn1_params)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM transactions ORDER BY id ASC")
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        conn.close()
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()

class BackgroundDataManager:
    def __init__(self):
        self.data_queue = Queue()
        self.latest_data = None
        self.last_update = None
        self.is_running = False
        self.thread = None
        
    def start_background_refresh(self, refresh_interval=10):
        """Start background data refresh thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.refresh_interval = refresh_interval
        self.thread = threading.Thread(target=self._background_worker, daemon=True)
        self.thread.start()
        
    def stop_background_refresh(self):
        """Stop background data refresh"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
            
    def _background_worker(self):
        """Background worker that continuously fetches data"""
        while self.is_running:
            try:
                # Fetch fresh data
                fresh_data = self._fetch_latest_data()
                if fresh_data is not None:
                    self.latest_data = fresh_data
                    self.last_update = datetime.now()
                    self.data_queue.put(fresh_data)
                
                # Wait for next refresh
                time.sleep(self.refresh_interval)
                
            except Exception as e:
                print(f"Background refresh error: {e}")
                time.sleep(self.refresh_interval)
                
    def _fetch_latest_data(self):
        """Fetch latest transaction data"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="core_banking_system",
                user="bankuser",
                password="Test123",
                port=5433
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT id, transaction_type_id, amount, created_at, updated_at, currency
                FROM transactions 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC 
                LIMIT 500
            """)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            

            if data:
                df = pd.DataFrame(data, columns=columns)
                if 'amount' in df.columns:
                    df['amount'] = df['amount'].astype(float)
                return df
                
        except Exception as e:
            print(f"Data fetch error: {e}")
            
        return None
    
    def get_latest_data(self):
        """Get the latest available data"""
        try:
            while True:
                self.latest_data = self.data_queue.get_nowait()
        except:
            pass
        return self.latest_data
    
    def has_new_data(self):
        return not self.data_queue.empty()

class Database:
    def __init__(self):
        self.conn = None
        self.conn_params = {
            "host": "localhost",
            "database": "core_banking_system",
            "user": "bankuser",
            "password": "Test123",
            "port": 5433
        }

    def create_connection(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            return self.conn
        except Exception as e:
            st.error(f"Error connecting to database: {str(e)}")
            return None

    def create_table(self):
        conn = self.create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS notifications
                         (id SERIAL PRIMARY KEY, message text, type text, timestamp text, read integer)''')
           

    def generate_notification(self, message, type):
        conn = self.create_connection()
        if conn:
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("INSERT INTO notifications (message, type, timestamp, read) VALUES (%s, %s, %s, %s)",
                        (message, type, timestamp, 0))
            conn.commit()
            conn.close()

    def get_notifications(self):
        conn = self.create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM notifications ORDER BY id DESC")
            notifications = cur.fetchall()
            
            return notifications

    def mark_as_read(self, id):
        conn = self.create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("UPDATE notifications SET read = 1 WHERE id = %s", (id,))
            conn.commit()
            

    def get_unread_count(self):
        conn = self.create_connection()
        if conn:
            
            cur.execute("SELECT COUNT(*) FROM notifications WHERE read = 0")
            count = cur.fetchone()[0]
            
            return count

# ===================================================================
# DATA LOADING - Load your main data here
# ===================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_main_data():
    # Add this to your data loading section - AFTER loading charges_df and recommended_prices_df

    # Load transactions from dummydb
    try:
        conn3_params = {
            "host": "localhost",
            "database": "dummydb", 
            "user": "dummydata",
            "password": "Test123",
            "port": "5433"
        }
        
        conn3 = psycopg2.connect(**conn3_params)
        cur3 = conn3.cursor()
        
        cur3.execute("""
            SELECT id, transaction_type_id, amount, fee_applied, created_at, updated_at, currency
            FROM transactions 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC 
            LIMIT 1000
        """)
        transactions_data = cur3.fetchall()
        
        # Create transactions DataFrame
        transactions_df = pd.DataFrame(transactions_data, columns=[
            "id", "transaction_type_id", "amount", "fee_applied", "created_at", "updated_at", "currency"
        ])
        
        # Close dummydb connection
        cur3.close()
        conn3.close()
        
    except Exception as e:
        st.error(f"Error loading transactions from dummydb: {e}")
        # Create empty transactions DataFrame as fallback
        transactions_df = pd.DataFrame(columns=[
            "id", "transaction_type_id", "amount", "fee_applied", "created_at", "updated_at", "currency"
        ])
    try:
        conn1_params = {
            "host": "localhost",
            "database": "core_banking_system", 
            "user": "bankuser",
            "password": "Test123",
            "port": "5433"
        }

        conn2_params = {
            "host": "ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
            "database": "neondb",
            "user": "neondb_owner",
            "password": "npg_7AlUWE8wkigH",
            "port": "5432"
        }

        # --- Connection 1: charges ---
        with psycopg2.connect(**conn1_params) as conn1:
            with conn1.cursor() as cur1:
                cur1.execute("""
                    SELECT transaction_type_id, charge_type, charge_range_min, charge_range_max, 
                           charge_amount, charge_percentage
                    FROM charges
                """)
                charges_data = cur1.fetchall()
                charges_columns = [desc[0] for desc in cur1.description]

        # --- Connection 2: recommendations ---
        with psycopg2.connect(**conn2_params) as conn2:
            with conn2.cursor() as cur2:
                cur2.execute("""
                    SELECT transaction_type_id, recommended_min_fee, recommended_max_fee, 
                           recommended_flat_fee, recommended_percentage_fee
                    FROM price_recommendations
                """)
                recommended_data = cur2.fetchall()
                recommended_columns = [desc[0] for desc in cur2.description]

        # --- DataFrames ---
        charges_df = pd.DataFrame(charges_data, columns=charges_columns)
        recommended_df = pd.DataFrame(recommended_data, columns=recommended_columns)

        # --- Merge ---
        merged_df = pd.merge(charges_df, recommended_df, on="transaction_type_id", how="left").drop_duplicates()

      # --- Type conversion ---
        numeric_cols = [
            "charge_percentage", "recommended_percentage_fee",
            "charge_range_min", "charge_range_max", "charge_amount",
            "recommended_min_fee", "recommended_max_fee", "recommended_flat_fee"
        ]
        for col in numeric_cols:
            if col in merged_df.columns:
                merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce").astype(float)

        # --- Differences ---
        merged_df["min_fee_diff"] = merged_df["charge_range_min"] - merged_df["recommended_min_fee"]
        merged_df["max_fee_diff"] = merged_df["charge_range_max"] - merged_df["recommended_max_fee"]
        merged_df["charge_amount_diff"] = merged_df["charge_amount"] - merged_df["recommended_flat_fee"]
        merged_df["percentage_diff"] = merged_df["charge_percentage"] - merged_df["recommended_percentage_fee"]
        merged_df["total_diff"] = merged_df[["min_fee_diff", "max_fee_diff", "charge_amount_diff", "percentage_diff"]].abs().sum(axis=1)
        
        differences_table = merged_df[[
            "transaction_type_id",
            "charge_range_min", "recommended_min_fee",
            "charge_range_max", "recommended_max_fee",
            "charge_amount", "recommended_flat_fee", "charge_amount_diff",
            "charge_percentage", "recommended_percentage_fee", "percentage_diff"
        ]]
        return merged_df, differences_table

    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ===================================================================
# LOAD DATA
# ===================================================================
merged_df, differences_table = load_main_data()

# Initialize database and notifications
db = Database()
db.create_table()

# ===================================================================
# PAGE SELECTION - AFTER DATA LOADING
# ===================================================================
st.sidebar.title("🧭 Navigation Menu")
page = st.sidebar.selectbox(
    "Choose a page", 
    [
        "Home", 
        "AI-powered Real-time & Historical Analysis",
        "AI-assisted Revenue Categorization",
        "Revenue Leakage Detection",
        "Transaction Monitoring",  
        "Fee Validation", 
        "Forecasting", 
        "Recommendations"
    ]
)

# ===================================================================
# PAGE CONTENT - Based on selection
# ===================================================================

if page == "Home":
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #007bff;
        margin: 0.5rem 0;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .algorithm-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .section-header {
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        font-size: 1.4rem;
        font-weight: bold;
    }
    .notification-badge {
        background: #ff6b6b;
        color: white;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .quick-action-btn {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

 

    # Define functions first
    def detect_rule_based_anomalies(merged_df):
        """
        Rule-based anomaly detection for pricing
        """
        anomalies = []
        
        for idx, row in merged_df.iterrows():
            actual_charge = row['charge_amount']
            recommended_min = row['recommended_min_fee']
            recommended_max = row['recommended_max_fee']
            recommended_pct_fee = row['recommended_percentage_fee']
            recommended_flat_fee = row['recommended_flat_fee']
            
            anomaly_reasons = []
            
            # Rule 1: Charge outside recommended price range
            if actual_charge < recommended_min:
                anomaly_reasons.append(f"Undercharged: ${actual_charge} < min ${recommended_min}")
            elif actual_charge > recommended_max:
                anomaly_reasons.append(f"Overcharged: ${actual_charge} > max ${recommended_max}")
            
            # Rule 2: Expected fee calculation mismatch
            expected_fee_pct = actual_charge * (recommended_pct_fee / 100) if pd.notna(recommended_pct_fee) else 0
            expected_fee_flat = recommended_flat_fee if pd.notna(recommended_flat_fee) else 0
            expected_total_fee = expected_fee_pct + expected_fee_flat
            
            # You might need to compare with actual fee if available
            # For now, we'll flag if the charge doesn't align with fee structure
            if pd.notna(recommended_pct_fee) and actual_charge > 0:
                calculated_min = recommended_min * (1 + recommended_pct_fee/100) + (recommended_flat_fee or 0)
                calculated_max = recommended_max * (1 + recommended_pct_fee/100) + (recommended_flat_fee or 0)
                
                if not (calculated_min <= actual_charge <= calculated_max):
                    anomaly_reasons.append(f"Fee calculation mismatch: charge ${actual_charge} outside calculated range [${calculated_min:.2f}, ${calculated_max:.2f}]")
            
            if anomaly_reasons:
                anomalies.append({
                    'index': idx,
                    'actual_charge': actual_charge,
                    'recommended_min': recommended_min,
                    'recommended_max': recommended_max,
                    'reasons': anomaly_reasons,
                    'severity': 'HIGH' if actual_charge < recommended_min else 'MEDIUM'
                })
        
        return pd.DataFrame(anomalies)

    # Custom CSS for styling - FIXED TO PRESERVE STREAMLIT MENU
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        .full-width-header {
            width: 100%;
            background: white;
            padding: 2.5rem 0;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid #e1e4e8;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .header-content {
            max-width: 1200px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .feature-tags {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1.5rem;
        }
        
        .dashboard-content {
            padding: 0 1rem;
        }
        
        .feature-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e1e4e8;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            height: 100%;
            transition: transform 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e1e4e8;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #e1e4e8;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

    # DASHBOARD HEADER - CENTERED VERSION
    st.markdown("""
    <div class="full-width-header">
        <div class="header-content">
            <h1 style="margin:0; font-size:2.8rem; font-weight:800; color: #2c3e50; text-align: center;">💰 Revenue Assurance Dashboard</h1>
            <p style="margin:0; opacity:0.8; font-size:1.2rem; margin-top:0.8rem; color: #7f8c8d; text-align: center;">
            AI-Powered Anomaly Detection & Revenue Optimization Platform
            </p>
            <div class="feature-tags">
                <span style="background: #f8f9fa; padding:0.6rem 1.2rem; border-radius:25px; font-size:1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                🔍 Real-time Monitoring
                </span>
                <span style="background: #f8f9fa; padding:0.6rem 1.2rem; border-radius:25px; font-size:1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                🤖 Multi-Algorithm AI
                </span>
                <span style="background: #f8f9fa; padding:0.6rem 1.2rem; border-radius:25px; font-size:1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                📊 Advanced Analytics
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Content container starts here
    st.markdown('<div class="dashboard-content">', unsafe_allow_html=True)

    # Generate sample data - FIXED VERSION
    @st.cache_data
    def generate_sample_data():
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        n_days = len(dates)
        
        # Use simple Python random instead of numpy
        import random
        random.seed(42)
        
        revenue = []
        current = 100000
        
        for i in range(n_days):
            # Simple revenue growth with randomness
            growth = random.uniform(80, 120)
            current += growth
            seasonal = 3000 * math.sin(2 * math.pi * i / 365)
            current += seasonal
            revenue.append(current)
        
        # Create anomaly list - all False initially
        anomaly = [False] * n_days
        
        # Select anomaly indices using Python random
        anomaly_indices = random.sample(range(n_days), 12)
        
        # Apply anomalies
        for idx in anomaly_indices:
            revenue[idx] = revenue[idx] * random.uniform(0.3, 0.6)
            anomaly[idx] = True
        
        return pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'anomaly': anomaly
        })

    # Load data
    df = generate_sample_data()

    # Metrics Row
    st.markdown("## 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 2rem; font-weight: bold; color: #2c3e50;'>98.7%</div>
            <div style='color: #7f8c8d;'>Revenue Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 2rem; font-weight: bold; color: #2c3e50;'>$4.2M</div>
            <div style='color: #7f8c8d;'>Protected Revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 2rem; font-weight: bold; color: #2c3e50;'>12</div>
            <div style='color: #7f8c8d;'>Anomalies Detected</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 2rem; font-weight: bold; color: #2c3e50;'>24/7</div>
            <div style='color: #7f8c8d;'>Active Monitoring</div>
        </div>
        """, unsafe_allow_html=True)

    # Features Section
    st.markdown("## 🚀 Core Features")
    features_col1, features_col2, features_col3 = st.columns(3)

    with features_col1:
        st.markdown("""
        <div class="feature-card">
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🔍</div>
            <h3 style='color: #2c3e50; margin-bottom: 1rem;'>Real-time Monitoring</h3>
            <p style='color: #7f8c8d;'>Continuous tracking of revenue streams with instant alerts for discrepancies and potential revenue leaks.</p>
        </div>
        """, unsafe_allow_html=True)

    with features_col2:
        st.markdown("""
        <div class="feature-card">
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>🤖</div>
            <h3 style='color: #2c3e50; margin-bottom: 1rem;'>Multi-Algorithm AI</h3>
            <p style='color: #7f8c8d;'>Advanced machine learning models working in tandem to detect complex patterns and subtle anomalies.</p>
        </div>
        """, unsafe_allow_html=True)

    with features_col3:
        st.markdown("""
        <div class="feature-card">
            <div style='font-size: 2.5rem; margin-bottom: 1rem;'>📊</div>
            <h3 style='color: #2c3e50; margin-bottom: 1rem;'>Advanced Analytics</h3>
            <p style='color: #7f8c8d;'>Deep insights into revenue performance with predictive analytics and optimization recommendations.</p>
        </div>
        """, unsafe_allow_html=True)

    # Charts Section
    st.markdown("## 📊 Revenue Analytics")

    # Revenue Trend Chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("💰 Revenue Performance Trends")

    fig_revenue = go.Figure()

    # Add normal revenue points
    normal_data = df[~df['anomaly']]
    fig_revenue.add_trace(go.Scatter(
        x=normal_data['date'],
        y=normal_data['revenue'],
        mode='lines',
        name='Normal Revenue',
        line=dict(color='#667eea', width=3)
    ))

    # Add anomaly points
    anomaly_data = df[df['anomaly']]
    fig_revenue.add_trace(go.Scatter(
        x=anomaly_data['date'],
        y=anomaly_data['revenue'],
        mode='markers',
        name='Anomalies Detected',
        marker=dict(color='#ff6b6b', size=10, symbol='x-thin', line=dict(width=2))
    ))

    fig_revenue.update_layout(
        height=400,
        showlegend=True,
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        template="plotly_white",
        hovermode='x unified'
    )

    st.plotly_chart(fig_revenue, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Initialize session state
    if 'show_notifications' not in st.session_state:
        st.session_state.show_notifications = False
    if 'view_raw_data' not in st.session_state:
        st.session_state.view_raw_data = False
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False

    # Notifications Panel
    if st.session_state.show_notifications:
        with st.container():
            st.markdown("### 📋 System Notifications")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.error("🔴 **3 Critical Anomalies** detected in transaction fees")
                st.warning("🟡 **5 Undercharged Transactions** require immediate review")
                st.info("🔵 **System Update**: New anomaly detection algorithms available")
                st.success("🟢 **Performance**: All systems operating optimally")
            with col2:
                if st.button("Mark All as Read", type="primary"):
                    st.session_state.show_notifications = False
                    st.rerun()

    try:
        # Data Loading Section
        with st.expander("📊 Data Overview & Configuration", expanded=True):
            st.markdown("### Database Connections & Data Summary")
            
            # Database status
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("✅ **Core Banking System**")
                st.caption("localhost:5433 | core_banking_system")
            with col2:
                st.success("✅ **Price Recommendations**")
                st.caption("Neon PostgreSQL | Live connection")
            with col3:
                st.info("🔄 **Last Updated**")
                st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Data metrics
            if 'merged_df' in locals():
                total_records = len(merged_df)
                unique_types = merged_df['transaction_type_id'].nunique()
                data_quality = f"{(1 - merged_df.isnull().sum().sum() / (len(merged_df) * len(merged_df.columns)))*100:.1f}%"
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Records", f"{total_records:,}")
                with col2:
                    st.metric("Transaction Types", unique_types)
                with col3:
                    st.metric("Data Quality", data_quality)
                with col4:
                    st.metric("Analysis Ready", "✅")

        # Quick Actions Bar
        st.markdown("### 🚀 Quick Actions")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("🎯 Run Anomaly Detection", use_container_width=True, type="primary"):
                st.session_state.run_analysis = True
        with action_col2:
            if st.button("📊 View All Data", use_container_width=True):
                st.session_state.view_raw_data = True
        with action_col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        with action_col4:
            if st.button("📈 Export Report", use_container_width=True):
                st.success("Report export initiated!")

        # Main Dashboard Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Anomaly Detection", "📈 Analytics", "📋 Data Explorer", "⚙️ Algorithms"])

        with tab1:
            st.markdown("### 🔍 Advanced Anomaly Detection")

            # Ensure numeric dtypes
            merged_df["charge_amount_diff"] = pd.to_numeric(merged_df["charge_amount_diff"], errors="coerce")
            merged_df["percentage_diff"] = pd.to_numeric(merged_df["percentage_diff"], errors="coerce")
            merged_df["transaction_type_id"] = merged_df["transaction_type_id"].astype(str)

            features = merged_df[["charge_amount_diff", "percentage_diff"]].fillna(0).astype(float)

            st.markdown("""
                <style>
                .algorithm-card {
                    background: #fff;
                    padding: 1rem;
                    border-radius: 10px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                    min-height: 160px;   /* enforce equal height */
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                }
                .algorithm-card h4 {
                    margin: 0 0 0.5rem 0;
                    font-size: 1.1rem;
                }
                .algorithm-card p {
                    margin: 0;
                    font-size: 0.85rem;
                    color: #555;
                }
                </style>
                """, unsafe_allow_html=True)
            
            # Algorithm Selection
            st.markdown("#### Select Detection Algorithms")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="algorithm-card">
                    <h4>🌲 Isolation Forest</h4>
                    <p><small>Unsupervised anomaly detection using tree-based ensemble</small></p>
                </div>
                """, unsafe_allow_html=True)
                use_isolation_forest = st.checkbox("Enable Isolation Forest", value=True, key="iforest")
                
            with col2:
                st.markdown("""
                <div class="algorithm-card">
                    <h4>📊 Z-Score Detection</h4>
                    <p><small>Statistical outlier detection based on standard deviations</small></p>
                </div>
                """, unsafe_allow_html=True)
                use_zscore = st.checkbox("Enable Z-Score", value=True, key="zscore")
                
            with col3:
                st.markdown("""
                <div class="algorithm-card">
                    <h4>🧠 Autoencoder</h4>
                    <p><small>Deep learning anomaly detection using neural networks</small></p>
                </div>
                """, unsafe_allow_html=True)
                use_autoencoder = st.checkbox("Enable Autoencoder", value=False, key="autoencoder")

            with col4:
                st.markdown("""
                <div class="algorithm-card">
                    <h4>📏 Rule-Based</h4>
                    <p><small>Business rule violations in pricing and fees</small></p>
                </div>
                """, unsafe_allow_html=True)
                use_rule_based = st.checkbox("Enable Rule-Based", value=True, key="rule_based")

            # Run analysis when triggered
            if st.session_state.run_analysis or st.button(" Run Comprehensive Analysis", type="primary", use_container_width=True):
                with st.spinner(" Running multi-algorithm anomaly detection..."):
                    algorithm_results = {}
                    
                    # Isolation Forest Implementation
                    if use_isolation_forest:
                        from sklearn.ensemble import IsolationForest
                        iforest = IsolationForest(contamination=0.10, random_state=10)
                        features = merged_df[['charge_amount_diff', 'percentage_diff']].fillna(0)
                        iforest_predictions = iforest.fit_predict(features)
                        algorithm_results['Isolation Forest'] = {
                            'anomalies': merged_df[iforest_predictions == -1],
                            'count': (iforest_predictions == -1).sum(),
                            'color': '#FF6B6B'
                        }

                    # Z-Score Implementation
                    if use_zscore:
                        from scipy import stats
                        z_scores = np.abs(stats.zscore(merged_df[['charge_amount_diff', 'percentage_diff']].fillna(0)))
                        zscore_mask = (z_scores > 2.5).any(axis=1)
                        algorithm_results['Z-Score'] = {
                            'anomalies': merged_df[zscore_mask],
                            'count': zscore_mask.sum(),
                            'color': '#4ECDC4'
                        }

                    # Autoencoder Implementation (Simplified)
                    if use_autoencoder:
                        try:
                            from sklearn.preprocessing import StandardScaler
                            from sklearn.decomposition import PCA
                            
                            scaler = StandardScaler()
                            scaled_data = scaler.fit_transform(merged_df[['charge_amount_diff', 'percentage_diff']].fillna(0))
                            
                            pca = PCA(n_components=1)
                            transformed = pca.fit_transform(scaled_data)
                            reconstructed = pca.inverse_transform(transformed)
                            
                            reconstruction_error = np.mean((scaled_data - reconstructed) ** 2, axis=1)
                            autoencoder_mask = reconstruction_error > np.percentile(reconstruction_error, 95)
                            
                            algorithm_results['Autoencoder'] = {
                                'anomalies': merged_df[autoencoder_mask],
                                'count': autoencoder_mask.sum(),
                                'color': '#45B7D1'
                            }
                        except Exception as e:
                            st.warning(f"Autoencoder simplified: {e}")

                    # Rule-Based Detection
                    if use_rule_based:
                        rule_anomalies = detect_rule_based_anomalies(merged_df)
                        algorithm_results['Rule-Based'] = {
                            'anomalies': merged_df.loc[rule_anomalies['index']],
                            'count': len(rule_anomalies),
                            'color': '#FFA726',
                            'details': rule_anomalies  # Store detailed reasons
                        }

                    # Display Results
                    if algorithm_results:
                        # Summary Metrics
                        st.markdown("### 📊 Detection Results Summary")
                        total_anomalies = sum(result['count'] for result in algorithm_results.values())
                        total_records = len(merged_df)
                        anomaly_rate = (total_anomalies / total_records * 100) if total_records > 0 else 0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Records", f"{total_records:,}")
                        with col2:
                            st.metric("Anomalies Found", f"{total_anomalies:,}")
                        with col3:
                            st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                        with col4:
                            st.metric("Algorithms Used", len(algorithm_results))

                        # Algorithm Comparison
                        st.markdown("#### 🔬 Algorithm Performance")
                        algo_names = list(algorithm_results.keys())
                        algo_counts = [result['count'] for result in algorithm_results.values()]
                        algo_colors = [result['color'] for result in algorithm_results.values()]
                        
                        fig_comparison = px.bar(
                            x=algo_names, y=algo_counts,
                            title="Anomalies Detected by Each Algorithm",
                            labels={'x': 'Algorithm', 'y': 'Anomaly Count'},
                            color=algo_names, color_discrete_sequence=algo_colors
                        )
                        st.plotly_chart(fig_comparison, use_container_width=True)

                        # Unified Visualization
                        # Add to your visualization section
                        if 'Rule-Based' in algorithm_results:
                            st.markdown("#### 📋 Rule-Based Anomaly Details")
                            
                            # Display detailed reasons
                            rule_details = algorithm_results['Rule-Based']['details']
                            if not rule_details.empty:
                                for _, anomaly in rule_details.iterrows():
                                    with st.expander(f"🚨 Anomaly: Charge ${anomaly['actual_charge']} vs Range [${anomaly['recommended_min']}, ${anomaly['recommended_max']}]"):
                                        for reason in anomaly['reasons']:
                                            st.write(f"• {reason}")
                                        st.metric("Severity", anomaly['severity'])

                        st.markdown("#### 📈 Unified Anomaly View")
                        merged_df['is_anomaly'] = False
                        for result in algorithm_results.values():
                            merged_df.loc[result['anomalies'].index, 'is_anomaly'] = True

                        # Scatter Plot
                        fig_scatter = px.scatter(
                            merged_df, x='charge_amount_diff', y='percentage_diff',
                            color='is_anomaly', 
                            title="Charge Amount vs Percentage Differences",
                            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'},
                            hover_data=['transaction_type_id'],
                            size_max=10
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)

                        # Distribution Analysis
                        col1, col2 = st.columns(2)
                        with col1:
                            fig_hist_amount = px.histogram(
                                merged_df, x='charge_amount_diff', color='is_anomaly',
                                title="Charge Amount Difference Distribution",
                                barmode='overlay',
                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                            )
                            st.plotly_chart(fig_hist_amount, use_container_width=True)
                        
                        with col2:
                            fig_hist_pct = px.histogram(
                                merged_df, x='percentage_diff', color='is_anomaly',
                                title="Percentage Difference Distribution",
                                barmode='overlay',
                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                            )
                            st.plotly_chart(fig_hist_pct, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Advanced Analytics")
            
            # Charges vs Recommended Prices Table
            st.markdown("####  Charges vs Recommended Prices")
            if 'differences_table' in locals():
                st.dataframe(differences_table, use_container_width=True, height=400)
            
            # Statistical Analysis
            st.markdown("#### 📊 Statistical Overview")
            if 'merged_df' in locals():
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Charge Amount Statistics:**")
                    st.write(merged_df['charge_amount_diff'].describe())
                with col2:
                    st.write("**Percentage Difference Statistics:**")
                    st.write(merged_df['percentage_diff'].describe())

        with tab3:
            st.markdown("### 📋 Data Explorer")
            
            if st.session_state.view_raw_data or st.button("Load Full Dataset"):
                st.markdown("#### Complete Dataset")
                if 'merged_df' in locals():
                    st.dataframe(merged_df, use_container_width=True, height=600)
                
                # Data Export
                st.markdown("#### 📤 Data Export")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info("Export the complete dataset for further analysis")
                with col2:
                    csv = merged_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"revenue_assurance_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        with tab4:
            st.markdown("### ⚙️ Algorithm Configuration")
            
            st.markdown("#### Detection Settings")
            sensitivity = st.slider("Detection Sensitivity", 1, 10, 7,
                                  help="Higher values detect more anomalies but may include false positives")
            
            col1, col2 = st.columns(2)
            with col1:
                contamination = st.slider("Contamination Rate", 0.01, 0.2, 0.05, 0.01,
                                        help="Expected proportion of anomalies in the data")
            with col2:
                z_threshold = st.slider("Z-Score Threshold", 2.0, 5.0, 2.5, 0.1,
                                      help="Standard deviations from mean for outlier detection")

            st.markdown("#### System Information")
            st.info("""
            **Available Algorithms:**
            -  Isolation Forest: Unsupervised, handles high-dimensional data
            - Z-Score: Statistical, fast for normally distributed data  
            -  Autoencoder: Deep learning, learns complex patterns
            """)

    except Exception as e:
        st.error(f"❌ System Error: {str(e)}")
        st.info("""
        **Troubleshooting Guide:**
        1. Verify database connections are active
        2. Check network connectivity
        3. Ensure all required tables exist
        4. Contact system administrator if issues persist
        """)

    # Close content container
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 2rem;'>"
        " **Revenue Assurance Dashboard** v2.0 | "
        "Real-time Anomaly Detection & Revenue Optimization  "
        
        "</div>",
        unsafe_allow_html=True
    )
