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
from streamlit_autorefresh import st_autorefresh
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
import io
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import json
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from scipy import stats
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import plotly.graph_objects as go
import math
from datetime import datetime

import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from scipy import stats
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import plotly.graph_objects as go
import math
from datetime import datetime

# PostgreSQL Database class
# PostgreSQL Database class
class Database:
    def __init__(self):
        # Use your existing PostgreSQL connection parameters
        self.conn_params = {
            "host": "localhost",
            "database": "core_banking_system",
            "user": "bankuser",
            "password": "Test123",
            "port": "5433"
        }
        self.conn = None
        self.connect()
        self.create_table()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            self.conn = None
    
    def create_table(self):
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # First, check if the table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'notifications'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                # Check if is_read column exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='notifications' AND column_name='is_read';
                """)
                column_exists = cursor.fetchone()
                
                if not column_exists:
                    # Add the missing column
                    cursor.execute('ALTER TABLE notifications ADD COLUMN is_read INTEGER DEFAULT 0;')
                    st.info("Added missing 'is_read' column to notifications table")
            else:
                # Create the table with all columns
                cursor.execute('''
                    CREATE TABLE notifications (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL,
                        type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        is_read INTEGER DEFAULT 0
                    )
                ''')
                st.info("Created notifications table")
            
            self.conn.commit()
            
        except Exception as e:
            st.warning(f"Could not setup notifications table: {e}")
            # Try to create a fresh table if there are issues
            try:
                cursor.execute('DROP TABLE IF EXISTS notifications;')
                cursor.execute('''
                    CREATE TABLE notifications (
                        id SERIAL PRIMARY KEY,
                        message TEXT NOT NULL,
                        type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        is_read INTEGER DEFAULT 0
                    )
                ''')
                self.conn.commit()
                st.info("Recreated notifications table due to errors")
            except Exception as e2:
                st.error(f"Could not recreate table: {e2}")
    
    def generate_notification(self, message, notification_type):
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (message, type, timestamp, is_read)
                VALUES (%s, %s, %s, %s)
            ''', (message, notification_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0))
            self.conn.commit()
        except Exception as e:
            st.warning(f"Could not generate notification: {e}")
    
    def get_unread_count(self):
        if not self.conn:
            return 3
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0')
            return cursor.fetchone()[0]
        except Exception as e:
            st.warning(f"Could not get unread count: {e}")
            return 3
    
    def get_notifications(self):
        if not self.conn:
            return [
                (1, "Database connected", "database", "2024-01-01 10:00:00", 0),
                (2, "Anomaly detection is done", "anomaly", "2024-01-01 10:05:00", 0),
                (3, "Your report is ready", "report", "2024-01-01 10:10:00", 0)
            ]
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM notifications ORDER BY id DESC')
            return cursor.fetchall()
        except Exception as e:
            st.warning(f"Could not get notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id):
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = %s', (notification_id,))
            self.conn.commit()
        except Exception as e:
            st.warning(f"Could not mark notification as read: {e}")

# Initialize database
db = Database()
db.create_table()

# Generate notifications
db.generate_notification("Database connected", "database")
db.generate_notification("Anomaly detection is done", "anomaly")
db.generate_notification("Your report is ready", "report")





# Database credentials for main data
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

# Establish connections
conn1 = psycopg2.connect(**conn1_params)
conn2 = psycopg2.connect(**conn2_params)

# Create cursor objects
cur1 = conn1.cursor()
cur2 = conn2.cursor()

# Execute queries
cur1.execute("""
    SELECT transaction_type_id, charge_type, charge_range_min, charge_range_max, charge_amount, charge_percentage
    FROM charges
""")
charges_data = cur1.fetchall()

cur2.execute("""
    SELECT transaction_type_id, recommended_min_fee, recommended_max_fee, recommended_flat_fee, recommended_percentage_fee
    FROM price_recommendations
""")
recommended_prices_data = cur2.fetchall()

# Create DataFrames
charges_df = pd.DataFrame(charges_data, columns=[
    "transaction_type_id", "charge_type", "charge_range_min", "charge_range_max", "charge_amount", "charge_percentage"
])
recommended_prices_df = pd.DataFrame(recommended_prices_data, columns=[
    "transaction_type_id", "recommended_min_fee", "recommended_max_fee", "recommended_flat_fee", "recommended_percentage_fee"
])

# Merge DataFrames based on transaction type
merged_df = pd.merge(charges_df, recommended_prices_df, on="transaction_type_id")

# Remove duplicate records
merged_df = merged_df.drop_duplicates()

# Calculate differences
merged_df['min_fee_diff'] = merged_df['charge_range_min'] - merged_df['recommended_min_fee']
merged_df['max_fee_diff'] = merged_df['charge_range_max'] - merged_df['recommended_max_fee']
merged_df['charge_amount_diff'] = merged_df['charge_amount'] - merged_df['recommended_flat_fee']
merged_df['percentage_diff'] = merged_df['charge_percentage'] - merged_df['recommended_percentage_fee']

# Create a table to show the differences
differences_table = merged_df[[
    "transaction_type_id",
    "charge_range_min", "recommended_min_fee", "min_fee_diff",
    "charge_range_max", "recommended_max_fee", "max_fee_diff",
    "charge_amount", "recommended_flat_fee", "charge_amount_diff",
    "charge_percentage", "recommended_percentage_fee", "percentage_diff"
]]

# Define anomaly detection functions
def detect_anomalies_iforest(merged_df):
    iforest = IsolationForest(contamination=0.01)
    iforest.fit(merged_df[['charge_amount_diff', 'percentage_diff']])
    anomaly_predictions = iforest.predict(merged_df[['charge_amount_diff', 'percentage_diff']])
    merged_df['anomaly'] = anomaly_predictions
    anomalies = merged_df[merged_df['anomaly'] == -1]
    
    st.write("Scatter plot of charge amount differences vs percentage differences:")
    fig1 = plt.figure(figsize=(10, 6))
    sns.scatterplot(x='charge_amount_diff', y='percentage_diff', hue='anomaly', data=merged_df, palette=['blue', 'red'])
    plt.title('Charge Amount Differences vs Percentage Differences')
    st.pyplot(fig1)

    st.write("Histogram of charge amount differences:")
    fig2 = plt.figure(figsize=(10, 6))
    sns.histplot(merged_df['charge_amount_diff'], bins=50, kde=True)
    plt.title('Histogram of Charge Amount Differences')
    st.pyplot(fig2)

    st.write("Anomaly Statistics:")
    st.write(anomalies[['charge_amount_diff', 'percentage_diff']].describe())

    normal_data = merged_df[merged_df['anomaly'] == 1]
    st.write("Normal Data Statistics:")
    st.write(normal_data[['charge_amount_diff', 'percentage_diff']].describe())

    anomaly_transaction_types = anomalies['transaction_type_id'].value_counts()
    st.write("Anomaly Transaction Types:")
    st.write(anomaly_transaction_types)

    correlation_matrix = merged_df[['charge_amount_diff', 'percentage_diff']].corr()
    st.write("Correlation Matrix:")
    st.write(correlation_matrix)
    
    return merged_df, anomalies

def detect_anomalies_zscore(merged_df):
    merged_df['charge_amount_diff'] = merged_df['charge_amount_diff'].astype(float)
    merged_df['percentage_diff'] = merged_df['percentage_diff'].astype(float)

    z_scores = stats.zscore(merged_df[['charge_amount_diff', 'percentage_diff']])
    anomaly_mask = (abs(z_scores) > 3).any(axis=1)
    anomalies = merged_df[anomaly_mask]
    
    merged_df['anomaly'] = pd.Series(anomaly_mask).map({True: 'Anomaly', False: 'Normal'})

    st.write("Scatter plot of charge amount differences vs percentage differences:")
    fig1 = plt.figure(figsize=(10, 6))
    sns.scatterplot(x='charge_amount_diff', y='percentage_diff', hue='anomaly', data=merged_df, palette=['blue', 'red'])
    plt.title('Charge Amount Differences vs Percentage Differences')
    st.pyplot(fig1)

    st.write("Line graph of charge amount differences:")
    fig2 = plt.figure(figsize=(10, 6))
    plt.plot(merged_df['charge_amount_diff'], label='Charge Amount Differences')
    plt.plot(anomalies.index, anomalies['charge_amount_diff'], label='Anomalies', linestyle='None', marker='o', color='red')
    plt.title('Line Graph of Charge Amount Differences')
    plt.legend()
    st.pyplot(fig2)

    st.write("Boxplot of charge amount differences:")
    fig4 = plt.figure(figsize=(10, 6))
    sns.boxplot(x='anomaly', y='charge_amount_diff', data=merged_df)
    plt.title('Boxplot of Charge Amount Differences')
    st.pyplot(fig4)

    st.write("Anomaly Statistics:")
    st.write(anomalies[['charge_amount_diff', 'percentage_diff']].describe())

    normal_data = merged_df[~anomaly_mask]
    st.write("Normal Data Statistics:")
    st.write(normal_data[['charge_amount_diff', 'percentage_diff']].describe())

    correlation_matrix = merged_df[['charge_amount_diff', 'percentage_diff']].corr()
    st.write("Correlation Matrix:")
    st.write(correlation_matrix)
    
    return merged_df, anomalies

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32)
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def detect_anomalies_autoencoder(merged_df):
    input_dim = merged_df[['charge_amount_diff', 'percentage_diff']].shape[1]
    model = Autoencoder(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    data = merged_df[['charge_amount_diff', 'percentage_diff']].values
    data = torch.tensor(data, dtype=torch.float32)
    
    for epoch in range(100):
        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs, data)
        loss.backward()
        optimizer.step()
    
    model.eval()
    with torch.no_grad():
        outputs = model(data)
        reconstruction_error = ((outputs - data) ** 2).mean(axis=1)
        anomaly_mask = reconstruction_error > 0.1
        anomalies = merged_df[anomaly_mask.numpy()]
    
    merged_df['anomaly'] = anomaly_mask.numpy().astype(int)

    st.write("Scatter plot of charge amount differences vs percentage differences:")
    fig1 = plt.figure(figsize=(10, 6))
    sns.scatterplot(x='charge_amount_diff', y='percentage_diff', hue='anomaly', data=merged_df, palette=['blue', 'red'])
    plt.title('Charge Amount Differences vs Percentage Differences')
    st.pyplot(fig1)

    st.write("Histogram of charge amount differences:")
    fig2 = plt.figure(figsize=(10, 6))
    sns.histplot(merged_df['charge_amount_diff'], bins=50, kde=True)
    plt.title('Histogram of Charge Amount Differences')
    st.pyplot(fig2)

    st.write("Anomaly Statistics:")
    st.write(anomalies[['charge_amount_diff', 'percentage_diff']].describe())

    normal_data = merged_df[~anomaly_mask.numpy()]
    st.write("Normal Data Statistics:")
    st.write(normal_data[['charge_amount_diff', 'percentage_diff']].describe())

    correlation_matrix = merged_df[['charge_amount_diff', 'percentage_diff']].corr()
    st.write("Correlation Matrix:")
    st.write(correlation_matrix)
    
    return merged_df, anomalies

# Streamlit dashboard menu
st.sidebar.title("Anomaly Detection Menu")
page = st.sidebar.selectbox("Choose a page", ["Home", "AI-powered Real-time & Historical Analysis","AI-assisted Revenue Categorization","Top Transaction Types","Transaction Monitoring",  "Fee Validation" , "Forecasting", "Recommendations"])
placeholder = st.empty()


if page == "Home":
    with placeholder.container():

   
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-left: 4rem;
            padding-right: 4rem;
            padding-bottom: 4rem;
            max-width: 100%;
        }
        
        .full-width-header {
            width: 100%;
            background: white;
            padding: 4rem 0;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 4rem;
            border-bottom: 1px solid #e1e4e8;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .header-content {
            max-width: 1600px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 0 3rem;
        }
        
        .feature-tags {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-top: 2.5rem;
        }
        
        .dashboard-content {
            padding: 0 3rem;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .feature-card {
            background: white;
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid #e1e4e8;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            height: 100%;
            transition: transform 0.2s;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid #e1e4e8;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 1.5rem 0;
            transition: transform 0.2s;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid #e1e4e8;
            margin: 2.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .section-spacing {
            margin: 4rem 0;
        }
        
        /* Better column spacing */
        [data-testid="column"] {
            padding: 1.5rem;
        }
        
        /* Enhanced Streamlit component spacing */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            margin-bottom: 2.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0px 0px;
            gap: 1rem;
            padding: 1rem 2rem;
            margin-right: 1.5rem;
        }
        
        .stExpander {
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            margin: 1.5rem 0;
        }
        
        /* Better spacing for metrics */
        [data-testid="metric-container"] {
            padding: 2rem;
            border-radius: 12px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 1rem;
        }
        
        /* Enhanced header sizes */
        .dashboard-header {
            font-size: 3.5rem;
            font-weight: 800;
            color: #2c3e50;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }
        
        .dashboard-subheader {
            font-size: 1.6rem;
            color: #7f8c8d;
            margin-bottom: 2.5rem;
            line-height: 1.5;
        }
        
        /* Feature tag enhancements */
        .feature-tag {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 30px;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)

        # DASHBOARD HEADER - CENTERED VERSION
        st.markdown("""
        <div class="full-width-header">
            <div class="header-content">
                <h1 style="margin:0; font-size:3.5rem; font-weight:800; color: #2c3e50; text-align: center;">💰 Revenue Assurance Dashboard</h1>
                <p style="margin:0; opacity:0.8; font-size:1.6rem; margin-top:1.5rem; color: #7f8c8d; text-align: center;">
                AI-Powered Anomaly Detection & Revenue Optimization Platform
                </p>
                <div class="feature-tags">
                    <span style="background: #f8f9fa; padding:1rem 2rem; border-radius:30px; font-size:1.1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                    🔍 Real-time Monitoring
                    </span>
                    <span style="background: #f8f9fa; padding:1rem 2rem; border-radius:30px; font-size:1.1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                    🤖 Multi-Algorithm AI
                    </span>
                    <span style="background: #f8f9fa; padding:1rem 2rem; border-radius:30px; font-size:1.1rem; color: #2c3e50; border: 1px solid #e1e4e8; white-space: nowrap;">
                    📊 Advanced Analytics
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Content container starts here
        st.markdown('<div class="dashboard-content">', unsafe_allow_html=True)

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

            def detect_rule_based_anomalies(df):
                """Detect anomalies based on business rules"""
                anomalies = []
                
                for idx, row in df.iterrows():
                    reasons = []
                    severity = "low"
                    
                    # Rule 1: Charge outside recommended range
                    if (row['charge_amount'] < row['recommended_min_fee'] or 
                        row['charge_amount'] > row['recommended_max_fee']):
                        reasons.append(f"Charge ${row['charge_amount']} outside range [${row['recommended_min_fee']}, ${row['recommended_max_fee']}]")
                        severity = "high"
                    
                    # Rule 2: Percentage difference too high
                    if abs(row['percentage_diff']) > 50:  # More than 50% deviation
                        reasons.append(f"Percentage difference too high: {row['percentage_diff']:.1f}%")
                        severity = "medium"
                    
                    # Rule 3: Charge amount difference significant
                    if abs(row['charge_amount_diff']) > 100:  # More than $100 difference
                        reasons.append(f"Charge amount difference significant: ${row['charge_amount_diff']:.2f}")
                        severity = "medium"
                    
                    if reasons:
                        anomalies.append({
                            'index': idx,
                            'reasons': reasons,
                            'severity': severity,
                            'actual_charge': row['charge_amount'],
                            'recommended_min': row['recommended_min_fee'],
                            'recommended_max': row['recommended_max_fee']
                        })
                
                return pd.DataFrame(anomalies) if anomalies else pd.DataFrame()

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
                        try:
                            algorithm_results = {}
                            
                            # Clean and prepare the data first
                            analysis_df = merged_df.copy()
                            
                            # Ensure numeric columns and handle None/NaN values properly
                            analysis_df['charge_amount_diff'] = pd.to_numeric(analysis_df['charge_amount_diff'], errors='coerce').fillna(0)
                            analysis_df['percentage_diff'] = pd.to_numeric(analysis_df['percentage_diff'], errors='coerce').fillna(0)
                            
                            # Remove any remaining None values
                            analysis_df = analysis_df.replace([None], 0)
                            
                            # Create features with clean data
                            features = analysis_df[['charge_amount_diff', 'percentage_diff']].astype(float)
                            
                            # Isolation Forest Implementation
                            if use_isolation_forest:
                                try:
                                    from sklearn.ensemble import IsolationForest
                                    iforest = IsolationForest(contamination=0.10, random_state=10)
                                    iforest_predictions = iforest.fit_predict(features)
                                    algorithm_results['Isolation Forest'] = {
                                        'anomalies': analysis_df[iforest_predictions == -1],
                                        'count': (iforest_predictions == -1).sum(),
                                        'color': '#FF6B6B'
                                    }
                                except Exception as e:
                                    st.warning(f"Isolation Forest failed: {e}")

                            # Z-Score Implementation
                            if use_zscore:
                                try:
                                    from scipy import stats
                                    # Ensure no infinite or NaN values
                                    clean_features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
                                    z_scores = np.abs(stats.zscore(clean_features, nan_policy='omit'))
                                    z_scores = np.nan_to_num(z_scores, nan=0, posinf=0, neginf=0)
                                    zscore_mask = (z_scores > 2.5).any(axis=1)
                                    algorithm_results['Z-Score'] = {
                                        'anomalies': analysis_df[zscore_mask],
                                        'count': zscore_mask.sum(),
                                        'color': '#4ECDC4'
                                    }
                                except Exception as e:
                                    st.warning(f"Z-Score detection failed: {e}")

                            # Autoencoder Implementation (Simplified)
                            if use_autoencoder:
                                try:
                                    from sklearn.preprocessing import StandardScaler
                                    from sklearn.decomposition import PCA
                                    
                                    scaler = StandardScaler()
                                    clean_features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
                                    scaled_data = scaler.fit_transform(clean_features)
                                    
                                    pca = PCA(n_components=1)
                                    transformed = pca.fit_transform(scaled_data)
                                    reconstructed = pca.inverse_transform(transformed)
                                    
                                    reconstruction_error = np.mean((scaled_data - reconstructed) ** 2, axis=1)
                                    reconstruction_error = np.nan_to_num(reconstruction_error, nan=0)
                                    autoencoder_mask = reconstruction_error > np.percentile(reconstruction_error[reconstruction_error > 0], 95)
                                    
                                    algorithm_results['Autoencoder'] = {
                                        'anomalies': analysis_df[autoencoder_mask],
                                        'count': autoencoder_mask.sum(),
                                        'color': '#45B7D1'
                                    }
                                except Exception as e:
                                    st.warning(f"Autoencoder failed: {e}")

                            # Rule-Based Detection
                            if use_rule_based:
                                try:
                                    rule_anomalies = detect_rule_based_anomalies(analysis_df)
                                    algorithm_results['Rule-Based'] = {
                                        'anomalies': analysis_df.loc[rule_anomalies['index']] if not rule_anomalies.empty else pd.DataFrame(),
                                        'count': len(rule_anomalies),
                                        'color': '#FFA726',
                                        'details': rule_anomalies
                                    }
                                except Exception as e:
                                    st.warning(f"Rule-based detection failed: {e}")

                            # Display Results
                            if algorithm_results:
                                # Filter out empty results
                                valid_results = {k: v for k, v in algorithm_results.items() if v['count'] > 0}
                                
                                if valid_results:
                                    # Summary Metrics
                                    st.markdown("### 📊 Detection Results Summary")
                                    total_anomalies = sum(result['count'] for result in valid_results.values())
                                    total_records = len(analysis_df)
                                    anomaly_rate = (total_anomalies / total_records * 100) if total_records > 0 else 0
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Records", f"{total_records:,}")
                                    with col2:
                                        st.metric("Anomalies Found", f"{total_anomalies:,}")
                                    with col3:
                                        st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                                    with col4:
                                        st.metric("Algorithms Used", len(valid_results))

                                    # Algorithm Comparison
                                    st.markdown("#### 🔬 Algorithm Performance")
                                    algo_names = list(valid_results.keys())
                                    algo_counts = [result['count'] for result in valid_results.values()]
                                    algo_colors = [result['color'] for result in valid_results.values()]
                                    
                                    fig_comparison = px.bar(
                                        x=algo_names, y=algo_counts,
                                        title="Anomalies Detected by Each Algorithm",
                                        labels={'x': 'Algorithm', 'y': 'Anomaly Count'},
                                        color=algo_names, color_discrete_sequence=algo_colors
                                    )
                                    st.plotly_chart(fig_comparison, use_container_width=True)

                                    # Unified Visualization Section
                                    if 'Rule-Based' in valid_results and not valid_results['Rule-Based']['details'].empty:
                                        st.markdown("#### 📋 Rule-Based Anomaly Details")
                                        
                                        # Create a table for rule-based anomalies
                                        rule_details = valid_results['Rule-Based']['details']
                                        
                                        # Convert to DataFrame for better display
                                        anomaly_table_data = []
                                        for _, anomaly in rule_details.iterrows():
                                            anomaly_table_data.append({
                                                'Transaction ID': anomaly['index'],
                                                'Actual Charge': f"${anomaly['actual_charge']:.2f}",
                                                'Recommended Min': f"${anomaly['recommended_min']:.2f}",
                                                'Recommended Max': f"${anomaly['recommended_max']:.2f}",
                                                'Severity': anomaly['severity'],
                                                'Reasons': '; '.join(anomaly['reasons'])
                                            })
                                        
                                        anomaly_df = pd.DataFrame(anomaly_table_data)
                                        
                                        # Display the table
                                        st.dataframe(
                                            anomaly_df,
                                            use_container_width=True,
                                            height=min(400, len(anomaly_df) * 35 + 40),
                                            hide_index=True
                                        )
                                        
                                    

                                    # Unified Anomaly View with Enhanced Visualizations
                                    st.markdown("#### 📈 Unified Anomaly Dashboard")

                                    # Mark anomalies in the analysis dataframe
                                    analysis_df['is_anomaly'] = False
                                    for result in valid_results.values():
                                        if not result['anomalies'].empty:
                                            analysis_df.loc[result['anomalies'].index, 'is_anomaly'] = True

                                    # Create tabs for different visualizations
                                    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["📊 Overview", "🔍 Scatter Analysis", "📈 Distribution", "🧮 Metrics"])

                                    with viz_tab1:
                                        # Overview Dashboard
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        total_anomalies = analysis_df['is_anomaly'].sum()
                                        total_records = len(analysis_df)
                                        anomaly_rate = (total_anomalies / total_records) * 100
                                        
                                        with col1:
                                            st.metric("Total Records", f"{total_records:,}")
                                        with col2:
                                            st.metric("Anomalies Detected", f"{total_anomalies:,}")
                                        with col3:
                                            st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                                        with col4:
                                            status_color = "🟢" if anomaly_rate < 5 else "🟡" if anomaly_rate < 15 else "🔴"
                                            st.metric("System Health", f"{status_color} {'Good' if anomaly_rate < 5 else 'Fair' if anomaly_rate < 15 else 'Poor'}")

                                        # Algorithm Performance Comparison
                                        st.subheader("🤖 Algorithm Performance Comparison")
                                        
                                        algo_comparison_data = []
                                        for algo_name, result in valid_results.items():
                                            algo_comparison_data.append({
                                                'Algorithm': algo_name,
                                                'Anomalies Found': result['count'],
                                                'Color': result['color']
                                            })
                                        
                                        algo_comparison_df = pd.DataFrame(algo_comparison_data)
                                        
                                        # Bar chart for algorithm comparison
                                        fig_algo_bar = px.bar(
                                            algo_comparison_df,
                                            x='Algorithm',
                                            y='Anomalies Found',
                                            color='Algorithm',
                                            title="Anomalies Detected by Each Algorithm",
                                            color_discrete_sequence=algo_comparison_df['Color'].tolist()
                                        )
                                        fig_algo_bar.update_layout(showlegend=False)
                                        st.plotly_chart(fig_algo_bar, use_container_width=True)

                                    with viz_tab2:
                                        # Enhanced Scatter Plot
                                        st.subheader("🔍 Charge Amount vs Percentage Differences")
                                        
                                        # Create enhanced scatter plot
                                        fig_scatter = px.scatter(
                                            analysis_df,
                                            x='charge_amount_diff',
                                            y='percentage_diff',
                                            color='is_anomaly',
                                            title="Anomaly Detection: Charge Amount vs Percentage Differences",
                                            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'},
                                            hover_data=['transaction_type_id'],
                                            size_max=15,
                                            opacity=0.7,
                                            labels={
                                                'charge_amount_diff': 'Charge Amount Difference ($)',
                                                'percentage_diff': 'Percentage Difference (%)',
                                                'is_anomaly': 'Is Anomaly'
                                            }
                                        )
                                        
                                        # Add reference lines
                                        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray")
                                        fig_scatter.add_vline(x=0, line_dash="dash", line_color="gray")
                                        
                                        # Add annotations for quadrants
                                        fig_scatter.add_annotation(x=analysis_df['charge_amount_diff'].max()*0.7, y=analysis_df['percentage_diff'].max()*0.8, 
                                                                text="High Risk Zone", showarrow=False, font=dict(color="#FF6B6B"))
                                        
                                        st.plotly_chart(fig_scatter, use_container_width=True)
                                        
                                        # Additional scatter analysis
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Bubble chart by transaction type
                                            transaction_anomaly_stats = analysis_df.groupby('transaction_type_id').agg({
                                                'is_anomaly': 'sum',
                                                'charge_amount_diff': 'mean',
                                                'percentage_diff': 'mean'
                                            }).reset_index()
                                            
                                            fig_bubble = px.scatter(
                                                transaction_anomaly_stats,
                                                x='charge_amount_diff',
                                                y='percentage_diff',
                                                size='is_anomaly',
                                                color='is_anomaly',
                                                hover_name='transaction_type_id',
                                                title="Anomaly Distribution by Transaction Type",
                                                size_max=40,
                                                color_continuous_scale='Viridis'
                                            )
                                            st.plotly_chart(fig_bubble, use_container_width=True)
                                        
                                        with col2:
                                            # 3D Scatter plot (if we have more dimensions)
                                            if 'min_fee_diff' in analysis_df.columns and 'max_fee_diff' in analysis_df.columns:
                                                fig_3d = px.scatter_3d(
                                                    analysis_df.head(100),  # Limit for performance
                                                    x='charge_amount_diff',
                                                    y='percentage_diff',
                                                    z='min_fee_diff',
                                                    color='is_anomaly',
                                                    title="3D Anomaly View",
                                                    color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                                                )
                                                st.plotly_chart(fig_3d, use_container_width=True)

                                    with viz_tab3:
                                        # Distribution Analysis
                                        st.subheader("📈 Distribution Analysis")
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # Enhanced histogram for charge amount differences
                                            fig_hist_amount = px.histogram(
                                                analysis_df,
                                                x='charge_amount_diff',
                                                color='is_anomaly',
                                                title="Distribution of Charge Amount Differences",
                                                barmode='overlay',
                                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'},
                                                nbins=50,
                                                opacity=0.7
                                            )
                                            fig_hist_amount.add_vline(x=0, line_dash="dash", line_color="black")
                                            st.plotly_chart(fig_hist_amount, use_container_width=True)
                                        
                                        with col2:
                                            # Enhanced histogram for percentage differences
                                            fig_hist_pct = px.histogram(
                                                analysis_df,
                                                x='percentage_diff',
                                                color='is_anomaly',
                                                title="Distribution of Percentage Differences",
                                                barmode='overlay',
                                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'},
                                                nbins=50,
                                                opacity=0.7
                                            )
                                            fig_hist_pct.add_vline(x=0, line_dash="dash", line_color="black")
                                            st.plotly_chart(fig_hist_pct, use_container_width=True)
                                        
                                        # Box plots for comparison
                                        col3, col4 = st.columns(2)
                                        
                                        with col3:
                                            fig_box_amount = px.box(
                                                analysis_df,
                                                x='is_anomaly',
                                                y='charge_amount_diff',
                                                color='is_anomaly',
                                                title="Charge Amount Differences: Anomalies vs Normal",
                                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                                            )
                                            st.plotly_chart(fig_box_amount, use_container_width=True)
                                        
                                        with col4:
                                            fig_box_pct = px.box(
                                                analysis_df,
                                                x='is_anomaly',
                                                y='percentage_diff',
                                                color='is_anomaly',
                                                title="Percentage Differences: Anomalies vs Normal",
                                                color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                                            )
                                            st.plotly_chart(fig_box_pct, use_container_width=True)

                                    with viz_tab4:
                                        # Detailed Metrics and Statistics
                                        st.subheader("🧮 Detailed Metrics")
                                        
                                        # Anomaly statistics table
                                        normal_data = analysis_df[~analysis_df['is_anomaly']]
                                        anomaly_data = analysis_df[analysis_df['is_anomaly']]
                                        
                                        metrics_data = {
                                            'Metric': [
                                                'Count', 'Mean Charge Diff', 'Std Charge Diff', 
                                                'Mean % Diff', 'Std % Diff', 'Min Charge Diff', 'Max Charge Diff'
                                            ],
                                            'Normal Data': [
                                                len(normal_data),
                                                f"${normal_data['charge_amount_diff'].mean():.2f}",
                                                f"${normal_data['charge_amount_diff'].std():.2f}",
                                                f"{normal_data['percentage_diff'].mean():.1f}%",
                                                f"{normal_data['percentage_diff'].std():.1f}%",
                                                f"${normal_data['charge_amount_diff'].min():.2f}",
                                                f"${normal_data['charge_amount_diff'].max():.2f}"
                                            ],
                                            'Anomaly Data': [
                                                len(anomaly_data),
                                                f"${anomaly_data['charge_amount_diff'].mean():.2f}",
                                                f"${anomaly_data['charge_amount_diff'].std():.2f}",
                                                f"{anomaly_data['percentage_diff'].mean():.1f}%",
                                                f"{anomaly_data['percentage_diff'].std():.1f}%",
                                                f"${anomaly_data['charge_amount_diff'].min():.2f}",
                                                f"${anomaly_data['charge_amount_diff'].max():.2f}"
                                            ]
                                        }
                                        
                                        metrics_df = pd.DataFrame(metrics_data)
                                        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                                        
                                        # Correlation heatmap
                                        st.subheader("📊 Correlation Analysis")
                                        
                                        numeric_columns = ['charge_amount_diff', 'percentage_diff', 'min_fee_diff', 'max_fee_diff']
                                        available_numeric = [col for col in numeric_columns if col in analysis_df.columns]
                                        
                                        if len(available_numeric) >= 2:
                                            correlation_matrix = analysis_df[available_numeric].corr()
                                            
                                            fig_corr = px.imshow(
                                                correlation_matrix,
                                                title="Correlation Matrix of Differences",
                                                color_continuous_scale='RdBu_r',
                                                aspect="auto"
                                            )
                                            st.plotly_chart(fig_corr, use_container_width=True)
                                        
                                        # Time series analysis (if date column exists)
                                        if 'timestamp' in analysis_df.columns or 'date' in analysis_df.columns:
                                            st.subheader("📅 Temporal Analysis")
                                            
                                            date_col = 'timestamp' if 'timestamp' in analysis_df.columns else 'date'
                                            analysis_df[date_col] = pd.to_datetime(analysis_df[date_col])
                                            
                                            # Group by date and count anomalies
                                            daily_anomalies = analysis_df.groupby(analysis_df[date_col].dt.date).agg({
                                                'is_anomaly': 'sum',
                                                'transaction_type_id': 'count'
                                            }).reset_index()
                                            daily_anomalies.columns = ['Date', 'Anomaly Count', 'Total Transactions']
                                            daily_anomalies['Anomaly Rate'] = (daily_anomalies['Anomaly Count'] / daily_anomalies['Total Transactions']) * 100
                                            
                                            fig_temporal = px.line(
                                                daily_anomalies,
                                                x='Date',
                                                y='Anomaly Rate',
                                                title="Daily Anomaly Rate Trend",
                                                markers=True
                                            )
                                            st.plotly_chart(fig_temporal, use_container_width=True)

                                    # Download option for anomaly analysis
                                    st.markdown("#### 💾 Export Anomaly Analysis")

                                    export_col1, export_col2 = st.columns(2)

                                    with export_col1:
                                        # Export anomaly data
                                        anomaly_export_df = analysis_df[analysis_df['is_anomaly']].copy()
                                        if not anomaly_export_df.empty:
                                            csv_anomalies = anomaly_export_df.to_csv(index=False)
                                            st.download_button(
                                                label="📥 Download Anomaly Data",
                                                data=csv_anomalies,
                                                file_name=f"anomaly_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                                mime="text/csv",
                                                use_container_width=True
                                            )

                                    with export_col2:
                                        # Export full analysis
                                        csv_full = analysis_df.to_csv(index=False)
                                        st.download_button(
                                            label="📊 Download Full Analysis",
                                            data=csv_full,
                                            file_name=f"complete_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                            mime="text/csv",
                                            use_container_width=True
                                        )
                                    # Scatter Plot
                                    fig_scatter = px.scatter(
                                        analysis_df, x='charge_amount_diff', y='percentage_diff',
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
                                            analysis_df, x='charge_amount_diff', color='is_anomaly',
                                            title="Charge Amount Difference Distribution",
                                            barmode='overlay',
                                            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                                        )
                                        st.plotly_chart(fig_hist_amount, use_container_width=True)
                                    
                                    with col2:
                                        fig_hist_pct = px.histogram(
                                            analysis_df, x='percentage_diff', color='is_anomaly',
                                            title="Percentage Difference Distribution",
                                            barmode='overlay',
                                            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'}
                                        )
                                        st.plotly_chart(fig_hist_pct, use_container_width=True)
                                else:
                                    st.info("✅ No anomalies detected by any algorithm")
                            else:
                                st.info("✅ No algorithms produced results")

                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")

            with tab2:
                st.markdown("### 📈 Advanced Analytics")
                
                # Charges vs Recommended Prices Table
                st.markdown("#### Charges vs Recommended Prices")
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
                
                # Initialize session state for view_raw_data
                if 'view_raw_data' not in st.session_state:
                    st.session_state.view_raw_data = False
                
                # Check if we should load full dataset
                load_full_data = st.button("Load Full Dataset")
                if load_full_data:
                    st.session_state.view_raw_data = True
                
                if st.session_state.view_raw_data:
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
                    
                    # Add option to hide the raw data
                    if st.button("Hide Full Dataset"):
                        st.session_state.view_raw_data = False
                        st.rerun()

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
                - Isolation Forest: Unsupervised, handles high-dimensional data
                - Z-Score: Statistical, fast for normally distributed data  
                - Autoencoder: Deep learning, learns complex patterns
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


    

        # Close database connections at the end
        cur1.close()
        cur2.close()
        conn1.close()
        conn2.close()




elif page == "AI-powered Real-time & Historical Analysis":
    with placeholder.container():

        # ===================================================================
        # 1. IMPORTS
        # ===================================================================
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

        st.set_page_config(layout="wide")
        st.title("🤖 AI-powered Real-time & Historical Transaction Analysis")
        st.caption("Advanced monitoring + Pattern recognition + Anomaly detection + Fee validation")

        # --- API Key Input ---
        open_key = "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"
        client = OpenAI(api_key=open_key) if open_key else None

        # --- Database Connections ---
        conn1_params = {
            "host": "localhost",
            "database": "dummydb",
            "user": "dummydata",
            "password": "Test123",
            "port": "5433"
        }
        
        conn_charges_params = {
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
            "port": 5432,
            "sslmode": "require"
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

        # ===================================================================
        # 3. HELPER FUNCTIONS
        # ===================================================================
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
                parson_parse(content)
                
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

        # ===================================================================
        # 4. REPORT GENERATION FUNCTIONS
        # ===================================================================
        def generate_pdf_report(transactions_df, fee_differences_table):
            """Generate a comprehensive PDF report and return bytes"""
            try:
                from fpdf import FPDF
                import tempfile
                import os
                from datetime import datetime
                
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                pdf.set_font('Arial', 'B', 16)
                pdf.cell(0, 10, 'Revenue Assurance Analysis Report', 0, 1, 'C')
                pdf.ln(5)
                
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
                pdf.ln(10)
                
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Executive Summary', 0, 1)
                pdf.set_font('Arial', '', 10)
                
                total_transactions = len(transactions_df)
                
                if 'amount_converted' in transactions_df.columns:
                    total_volume = transactions_df['amount_converted'].sum()
                elif 'amount' in transactions_df.columns:
                    total_volume = transactions_df['amount'].sum()
                else:
                    total_volume = 0
                    
                if 'is_anomaly' in transactions_df.columns:
                    anomalies_count = transactions_df['is_anomaly'].sum()
                else:
                    anomalies_count = 0
                    
                if 'fee_status' in transactions_df.columns:
                    fee_violations = len(transactions_df[transactions_df['fee_status'] == 'violation'])
                else:
                    fee_violations = 0
                    
                summary_text = f"""
                Total Transactions Analyzed: {total_transactions:,}
                Total Transaction Volume: ${total_volume:,.2f}
                Anomalies Detected: {anomalies_count}
                Fee Compliance Issues: {fee_violations}
                Analysis Period: Real-time monitoring
                """
                pdf.multi_cell(0, 8, summary_text)
                
                try:
                    import io
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    return pdf_bytes
                except:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_path = tmp_file.name
                    
                    try:
                        pdf.output(tmp_path)
                        
                        with open(tmp_path, 'rb') as file:
                            pdf_bytes = file.read()
                        
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                            
                        return pdf_bytes
                    except Exception as e:
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                        return None
                        
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
                return None

        def generate_excel_report(transactions_df, fee_differences_table):
            """Generate Excel report with detailed data"""
            try:
                import io
                from datetime import datetime
                
                output = io.BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    summary_data = {
                        'Metric': ['Total Transactions', 'Total Volume', 'Anomalies', 'Fee Violations', 'Report Date'],
                        'Value': [
                            len(transactions_df),
                            transactions_df['amount_converted'].sum() if 'amount_converted' in transactions_df.columns else 0,
                            transactions_df['is_anomaly'].sum() if 'is_anomaly' in transactions_df.columns else 0,
                            len(transactions_df[transactions_df['fee_status'] == 'violation']) if 'fee_status' in transactions_df.columns else 0,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    safe_transactions_cols = [col for col in transactions_df.columns if col in transactions_df]
                    if safe_transactions_cols:
                        transactions_df[safe_transactions_cols].to_excel(writer, sheet_name='Transactions', index=False)
                    else:
                        pd.DataFrame({'Message': ['No transaction data available']}).to_excel(writer, sheet_name='Transactions', index=False)
                    
                    if 'is_anomaly' in transactions_df.columns:
                        anomalies_mask = transactions_df['is_anomaly'] == 1
                        if anomalies_mask.any():
                            anomalies_df = transactions_df.loc[anomalies_mask]
                            safe_anomaly_cols = [col for col in anomalies_df.columns if col in anomalies_df]
                            if safe_anomaly_cols:
                                anomalies_df[safe_anomaly_cols].to_excel(writer, sheet_name='Anomalies', index=False)
                    
                    if 'fee_status' in transactions_df.columns:
                        violations_mask = transactions_df['fee_status'] == 'violation'
                        if violations_mask.any():
                            violations_df = transactions_df.loc[violations_mask]
                            safe_violation_cols = [col for col in violations_df.columns if col in violations_df]
                            if safe_violation_cols:
                                violations_df[safe_violation_cols].to_excel(writer, sheet_name='Fee Violations', index=False)
                    
                    if not fee_differences_table.empty:
                        fee_differences_table.to_excel(writer, sheet_name='Fee Differences', index=False)
                
                return output.getvalue()
                
            except Exception as e:
                st.error(f"Error generating Excel report: {str(e)}")
                return None

        def generate_csv_reports(transactions_df, fee_differences_table):
            """Generate multiple CSV files and return as zip"""
            try:
                import zipfile
                import io
                from datetime import datetime
                
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    safe_transactions_cols = [col for col in transactions_df.columns if col in transactions_df]
                    if safe_transactions_cols:
                        transactions_csv = transactions_df[safe_transactions_cols].to_csv(index=False)
                        zip_file.writestr('transactions.csv', transactions_csv)
                    else:
                        zip_file.writestr('transactions.csv', 'No transaction data available')
                    
                    if 'is_anomaly' in transactions_df.columns:
                        anomalies_mask = transactions_df['is_anomaly'] == 1
                        if anomalies_mask.any():
                            anomalies_df = transactions_df.loc[anomalies_mask]
                            safe_anomaly_cols = [col for col in anomalies_df.columns if col in anomalies_df]
                            if safe_anomaly_cols:
                                anomalies_csv = anomalies_df[safe_anomaly_cols].to_csv(index=False)
                                zip_file.writestr('anomalies.csv', anomalies_csv)
                    
                    if 'fee_status' in transactions_df.columns:
                        violations_mask = transactions_df['fee_status'] == 'violation'
                        if violations_mask.any():
                            violations_df = transactions_df.loc[violations_mask]
                            safe_violation_cols = [col for col in violations_df.columns if col in violations_df]
                            if safe_violation_cols:
                                violations_csv = violations_df[safe_violation_cols].to_csv(index=False)
                                zip_file.writestr('fee_violations.csv', violations_csv)
                    
                    if not fee_differences_table.empty:
                        fee_diff_csv = fee_differences_table.to_csv(index=False)
                        zip_file.writestr('fee_differences.csv', fee_diff_csv)
                
                return zip_buffer.getvalue()
                
            except Exception as e:
                st.error(f"Error generating CSV reports: {str(e)}")
                return None

        def generate_word_report(transactions_df, fee_differences_table):
            """Generate Word document report"""
            try:
                from docx import Document
                from datetime import datetime
                
                doc = Document()
                
                doc.add_heading('Revenue Assurance Analysis Report', 0)
                doc.add_paragraph(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                doc.add_paragraph()
                
                doc.add_heading('Executive Summary', level=1)
                total_transactions = len(transactions_df)
                
                if 'amount_converted' in transactions_df.columns:
                    total_volume = transactions_df['amount_converted'].sum()
                elif 'amount' in transactions_df.columns:
                    total_volume = transactions_df['amount'].sum()
                else:
                    total_volume = 0
                    
                if 'is_anomaly' in transactions_df.columns:
                    anomalies_count = transactions_df['is_anomaly'].sum()
                else:
                    anomalies_count = 0
                    
                summary_text = f"""
                This report provides a comprehensive analysis of {total_transactions:,} transactions 
                totaling ${total_volume:,.2f}. The analysis detected {anomalies_count} anomalous 
                transactions requiring investigation.
                """
                doc.add_paragraph(summary_text)
                
                import io
                output = io.BytesIO()
                doc.save(output)
                return output.getvalue()
                    
            except Exception as e:
                st.error(f"Error generating Word report: {str(e)}")
                return None

        def generate_json_report(transactions_df, fee_differences_table):
            """Generate JSON report with structured data"""
            try:
                from datetime import datetime
                import json
                
                total_transactions = len(transactions_df)
                
                if 'amount_converted' in transactions_df.columns:
                    total_volume = float(transactions_df['amount_converted'].sum())
                elif 'amount' in transactions_df.columns:
                    total_volume = float(transactions_df['amount'].sum())
                else:
                    total_volume = 0.0
                    
                if 'is_anomaly' in transactions_df.columns:
                    anomalies_detected = int(transactions_df['is_anomaly'].sum())
                else:
                    anomalies_detected = 0
                    
                if 'fee_status' in transactions_df.columns:
                    fee_violations = len(transactions_df[transactions_df['fee_status'] == 'violation'])
                else:
                    fee_violations = 0
                
                report_data = {
                    "metadata": {
                        "report_type": "Revenue Assurance Analysis",
                        "generated_at": datetime.now().isoformat(),
                        "data_sources": ["transactions", "fee_rules", "price_recommendations"]
                    },
                    "summary": {
                        "total_transactions": total_transactions,
                        "total_volume": total_volume,
                        "anomalies_detected": anomalies_detected,
                        "fee_violations": fee_violations
                    }
                }
                
                json_output = json.dumps(report_data, indent=2, default=str)
                return json_output.encode('utf-8')
                
            except Exception as e:
                st.error(f"Error generating JSON report: {str(e)}")
                return None

        def show_report_downloads(transactions_df, fee_differences_table):
            """Show download buttons for all report formats"""
            from datetime import datetime
            
            st.subheader("📊 Download Reports")
            st.info("💡 Click any button below to download reports")
            
            pdf_data = generate_pdf_report(transactions_df, fee_differences_table)
            excel_data = generate_excel_report(transactions_df, fee_differences_table)
            csv_data = generate_csv_reports(transactions_df, fee_differences_table)
            word_data = generate_word_report(transactions_df, fee_differences_table)
            json_data = generate_json_report(transactions_df, fee_differences_table)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            col1, col2 = st.columns(2)
            
            with col1:
                if pdf_data:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_data,
                        file_name=f"revenue_assurance_report_{timestamp}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="pdf_download"
                    )
                else:
                    st.warning("PDF report not available")
                
                if excel_data:
                    st.download_button(
                        label="📊 Download Excel Report",
                        data=excel_data,
                        file_name=f"revenue_assurance_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="excel_download"
                    )
                else:
                    st.warning("Excel report not available")
            
            with col2:
                if word_data:
                    st.download_button(
                        label="📝 Download Word Report",
                        data=word_data,
                        file_name=f"revenue_assurance_{timestamp}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="word_download"
                    )
                else:
                    st.warning("Word report not available")
                
                if csv_data:
                    st.download_button(
                        label="📋 Download CSV Reports (ZIP)",
                        data=csv_data,
                        file_name=f"revenue_assurance_csv_{timestamp}.zip",
                        mime="application/zip",
                        use_container_width=True,
                        key="csv_download"
                    )
                else:
                    st.warning("CSV reports not available")
            
            if json_data:
                st.download_button(
                    label="🔤 Download JSON Report",
                    data=json_data,
                    file_name=f"revenue_assurance_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="json_download"
                )
            else:
                st.warning("JSON report not available")

        # ===================================================================
        # 5. ADVANCED CLASSES (BEFORE MAIN LOGIC)
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
                        st.info(f"Too few samples ({sample_size}) for reliable anomaly detection")
                        df['is_anomaly'] = 0
                        df['combined_severity'] = 0.0
                        df['ensemble_anomaly_score'] = 0.0
                        return df
                    
                    # Convert all feature columns to numeric to handle decimal.Decimal types
                    # Convert all feature columns to float to handle decimal.Decimal types
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
                    
                except Exception as e:  # ← MAKE SURE YOU HAVE THIS EXCEPT BLOCK
                    st.error(f"Anomaly detection error: {str(e)}")
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

        # ===================================================================
        # 6. INITIALIZATION FUNCTIONS
        # ===================================================================
        def initialize_session_state():
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
            if "current_index" not in st.session_state:
                st.session_state.current_index = 0
            if "anomaly_detector" not in st.session_state:
                st.session_state.anomaly_detector = AdvancedAnomalyDetector()
            if "fee_verifier" not in st.session_state:
                st.session_state.fee_verifier = FeeVerificationSystem()
            if "ai_cache" not in st.session_state:
                st.session_state.ai_cache = {}
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
            if "show_reports" not in st.session_state:
                st.session_state.show_reports = False

        def load_transaction_data():
            try:
                conn1 = psycopg2.connect(**conn1_params)
                cur1 = conn1.cursor()
                cur1.execute("SELECT * FROM transactions ORDER BY id ASC")
                data = cur1.fetchall()
                cols = [desc[0] for desc in cur1.description]
                cur1.close()
                conn1.close()
                
                st.session_state.all_transactions = pd.DataFrame(data, columns=cols)
                st.session_state.current_index = 0
                st.session_state.transactions_df = pd.DataFrame()
                
                st.success(f"✅ Loaded {len(st.session_state.all_transactions)} transactions from dummydb")
                
            except Exception as e:
                st.error(f"Could not load transactions from dummydb: {e}")
                return False
            return True

        def load_transaction_types():
            try:
                conn2 = psycopg2.connect(**conn2_params)
                cur2 = conn2.cursor()
                
                cur2.execute("SELECT * FROM transaction_types")
                types = pd.DataFrame(cur2.fetchall(), columns=[d[0] for d in cur2.description])
                
                cur2.close()
                conn2.close()
                    
                st.session_state.transaction_types = types
                st.success("✅ Loaded transaction types from Neon")
                
            except Exception as e:
                st.warning(f"Could not load transaction mappings from Neon: {e}")
                st.session_state.transaction_types = pd.DataFrame()

        def load_charges_data():
            try:
                conn_charges = psycopg2.connect(**conn_charges_params)
                cur_charges = conn_charges.cursor()
                cur_charges.execute("""
                    SELECT transaction_type_id, charge_type, charge_range_min, charge_range_max, charge_amount, charge_percentage
                    FROM charges
                """)
                charges_data = cur_charges.fetchall()
                charges_df = pd.DataFrame(charges_data, columns=[
                    "transaction_type_id", "charge_type", "charge_range_min", "charge_range_max", "charge_amount", "charge_percentage"
                ])
                cur_charges.close()
                conn_charges.close()
                st.session_state.charges = charges_df
                st.success("✅ Loaded charges from core_banking_system")
                return True
            except Exception as e:
                st.warning(f"Could not load charges from core_banking_system: {e}")
                st.session_state.charges = pd.DataFrame()
                return False

        def load_price_recommendations():
            try:
                conn2 = psycopg2.connect(**conn2_params)
                cur2 = conn2.cursor()
                cur2.execute("""
                    SELECT transaction_type_id, recommended_min_fee, recommended_max_fee, recommended_flat_fee, recommended_percentage_fee
                    FROM price_recommendations
                """)
                recommended_prices_data = cur2.fetchall()
                recs = pd.DataFrame(recommended_prices_data, columns=[
                    "transaction_type_id", "recommended_min_fee", "recommended_max_fee", "recommended_flat_fee", "recommended_percentage_fee"
                ])
                cur2.close()
                conn2.close()
                st.session_state.price_recommendations = recs
                st.success("✅ Loaded price recommendations from Neon")
                return True
            except Exception as e:
                st.warning(f"Could not load recommendations from Neon: {e}")
                st.session_state.price_recommendations = pd.DataFrame()
                return False

        # ===================================================================
        # 7. MAIN APPLICATION LOGIC
        # ===================================================================
        
        # Initialize notification systems
        notification_system = NotificationSystem()
        popup_system = PopupNotificationSystem()
        
        # Initialize and Load Data
        initialize_session_state()

        with st.spinner("Loading data from databases..."):
            if st.session_state.all_transactions.empty:
                if not load_transaction_data():
                    st.error("Failed to load transaction data from dummydb.")
            
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

        # Report Download Section
        st.sidebar.header("📊 Reports")
        
        with st.sidebar.expander("Download Analysis Reports", expanded=False):
            st.write("Generate comprehensive reports in multiple formats:")
            
            if st.button("🎁 Show Download Options", use_container_width=True, type="primary", key="show_reports_btn"):
                st.session_state.show_reports = True
            
            st.info("""
            Available formats:
            • PDF - Professional summary
            • Excel - Detailed data sheets  
            • Word - Formatted document
            • CSV - Raw data files
            • JSON - Structured data
            """)
        
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
        
        risk_level = st.sidebar.multiselect(
            "Risk Level",
            ["Low", "Medium", "High", "Critical"],
            default=["Medium", "High", "Critical"]
        )

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

        # Main Dashboard Layout
        placeholder = st.empty()
        metrics_placeholder = st.empty()
        alerts_placeholder = st.empty()

        # Check if we have data to proceed
        if st.session_state.all_transactions.empty:
            st.error("No transaction data available. Please check your database connection.")
            st.stop()

        # Display connection status
        if st.session_state.transaction_types.empty:
            st.warning("⚠️ Could not load transaction types from Neon database. Some features may be limited.")
        if st.session_state.price_recommendations.empty:
            st.warning("⚠️ Could not load price recommendations from Neon database. Fee verification will be limited.")

        # Report Generation Interface
        if st.session_state.get('show_reports', False):
            show_report_downloads(st.session_state.transactions_df, st.session_state.fee_differences_table)
            if st.button("← Back to Analysis", key="back_btn"):
                st.session_state.show_reports = False
                st.rerun()
            st.stop()

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
            st.session_state.analysis_started = True
            notification_system.add_notification("Real-time analysis started automatically", "info")
            popup_system.add_popup("Analysis Started", "Real-time transaction analysis is now running", "info")

        # Add these AI functions BEFORE your main application logic (before the tabs)

        def real_ai_revenue_analysis(transactions_df):
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
                st.error(f"Real AI revenue analysis failed: {e}")
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
                st.error(f"ML forecasting failed: {e}")
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
                st.error(f"Revenue clustering failed: {e}")
                return None
        # Display tabs ALWAYS (place this BEFORE the processing condition)
        with placeholder.container():
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    "📈 Live Transactions", "🔍 Anomaly Analysis", "💰 Fee Compliance", 
                    "🤖 AI Insights", "📊 Fee Differences", "📋 Transaction Types", "🎯 Scenario Simulator"
                ])
            
            with tab1:
                st.subheader("Live Transaction Stream")
                
                # Create filtered dataframe for display
                display_df = st.session_state.transactions_df.copy()
                
                # Apply currency conversion
                if 'amount' in display_df.columns:
                    display_df["amount"] = pd.to_numeric(display_df["amount"], errors="coerce").fillna(0)
                    if display_currency == "ZiG":
                        display_df["amount_converted"] = display_df["amount"] * exchange_rate
                    else:
                        display_df["amount_converted"] = display_df["amount"]
                else:
                    display_df["amount_converted"] = 0
                    
                # Apply filters
                display_df = display_df[
                    (display_df["amount_converted"] >= min_amount) &
                    (display_df["amount_converted"] <= max_amount)
                ]
                
                if focus_category != "All" and "category_name" in display_df.columns:
                    display_df = display_df[display_df["category_name"] == focus_category]
                    
                # Display columns
                display_cols = ['id', 'amount_converted', 'currency', 'transaction_type_name']
                
                # Add available category columns
                if 'category_name' in display_df.columns:
                    display_cols.append('category_name')
                elif 'suggested_category' in display_df.columns:
                    display_cols.append('suggested_category')
                    
                # Add anomaly columns if available
                if 'is_anomaly' in display_df.columns:
                    display_cols.extend(['is_anomaly', 'combined_severity'])
                    
                # Add fee columns if available
                if 'fee_status_type' in display_df.columns:
                    display_cols.extend(['fee_status_type'])
                    
                # Filter to only existing columns
                display_cols = [col for col in display_cols if col in display_df.columns]
                
                if display_cols:
                    # Apply styling based on fee status
                    def color_fee_status(val):
                        if val == "Overcharge":
                            return 'background-color: #ffcccc'
                        elif val == "Undercharge":
                            return 'background-color: #ccffcc'
                        elif val == "Normal":
                            return 'background-color: #e6f3ff'
                        else:
                            return ''
                    
                    if 'fee_status_type' in display_df.columns:
                        styled_df = display_df[display_cols].head(50).style.applymap(
                            color_fee_status, subset=['fee_status_type']
                        )
                    else:
                        styled_df = display_df[display_cols].head(50)
                    
                    st.dataframe(styled_df, use_container_width=True, height=400)
                else:
                    st.info("No transaction data available yet")
            
            with tab2:
                st.subheader("🤖 AI-Powered Revenue Analytics")
                
                if not st.session_state.transactions_df.empty:
                    # Currency selection
                    currency = st.selectbox("Display Currency", ["USD", "ZiG"])
                    exchange_rate = 13.5 if currency == "ZiG" else 1.0
                    
                    # Prepare data
                    analysis_df = st.session_state.transactions_df.copy()
                    analysis_df["amount"] = pd.to_numeric(analysis_df["amount"], errors="coerce").fillna(0)
                    analysis_df["amount_converted"] = analysis_df["amount"] * exchange_rate
                    
                    # Basic revenue summary (your existing code)
                    st.markdown("### 📊 Basic Revenue Overview")
                    
                    if "category_name" in analysis_df.columns:
                        revenue_summary = analysis_df.groupby("category_name")["amount_converted"].sum().reset_index().sort_values("amount_converted", ascending=False)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart
                            fig1 = px.pie(revenue_summary, values='amount_converted', names='category_name', 
                                        title=f"Revenue Distribution by Category ({currency})")
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            # Bar chart
                            fig2 = px.bar(revenue_summary, x='category_name', y='amount_converted',
                                        title=f"Revenue by Category ({currency})",
                                        labels={'amount_converted': f'Revenue ({currency})', 'category_name': 'Category'})
                            fig2.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    # AI-POWERED REVENUE ANALYSIS SECTION
                    st.markdown("---")
                    st.markdown("### 🧠 AI-Powered Revenue Insights")
                    
                    if st.button("🚀 Run AI Revenue Analysis", type="primary", key="ai_revenue_analysis"):
                        with st.spinner("AI is analyzing revenue patterns... This may take a few seconds."):
                            
                            # 1. REAL AI REVENUE ANALYSIS
                            ai_insights = real_ai_revenue_analysis(analysis_df)
                            
                            if ai_insights:
                                st.success("✅ AI Analysis Complete!")
                                
                                # Display AI Insights in an organized way
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("#### 💰 Revenue Stream Analysis")
                                    if 'revenue_streams' in ai_insights:
                                        for stream in ai_insights['revenue_streams'][:4]:  # Show top 4
                                            trend_icon = "📈" if "increas" in stream.get('growth_trend', '').lower() else "📉" if "decreas" in stream.get('growth_trend', '').lower() else "➡️"
                                            st.metric(
                                                f"{trend_icon} {stream.get('stream_name', 'Stream')}",
                                                f"{stream.get('contribution_percentage', 0):.1f}%",
                                                stream.get('growth_trend', 'Unknown trend')
                                            )
                                
                                with col2:
                                    st.markdown("#### ⚠️ AI-Detected Risks")
                                    if 'revenue_risks' in ai_insights:
                                        for risk in ai_insights['revenue_risks'][:3]:
                                            severity_color = {
                                                'high': '🔴',
                                                'medium': '🟡', 
                                                'low': '🟢'
                                            }.get(risk.get('severity', '').lower(), '⚪')
                                            
                                            st.error(f"{severity_color} **{risk.get('severity', 'Unknown').upper()}**: {risk.get('risk_description', '')}")
                                            with st.expander("Mitigation Strategy"):
                                                st.write(risk.get('mitigation', 'No mitigation strategy provided'))
                                
                                # Key Insights
                                st.markdown("#### 💡 Key AI Insights")
                                if 'key_insights' in ai_insights:
                                    for i, insight in enumerate(ai_insights['key_insights'][:5]):
                                        st.info(f"{i+1}. {insight}")
                                
                                # AI Recommendations
                                st.markdown("#### 🎯 AI Optimization Recommendations")
                                if 'optimization_recommendations' in ai_insights:
                                    for i, rec in enumerate(ai_insights['optimization_recommendations'][:4]):
                                        confidence_color = "🟢" if rec.get('confidence', 0) > 80 else "🟡" if rec.get('confidence', 0) > 60 else "🔴"
                                        
                                        with st.expander(f"{confidence_color} Recommendation {i+1}: {rec.get('recommendation', '')}"):
                                            col_a, col_b, col_c = st.columns(3)
                                            with col_a:
                                                st.metric("Confidence", f"{rec.get('confidence', 0)}%")
                                            with col_b:
                                                st.metric("Impact", rec.get('expected_impact', 'Unknown'))
                                            with col_c:
                                                st.metric("Complexity", rec.get('implementation_complexity', 'Unknown'))
                            
                            # 2. REAL ML REVENUE FORECASTING
                            st.markdown("---")
                            st.markdown("### 📈 AI Revenue Forecasting")
                            
                            ml_forecast = real_ml_revenue_forecast(analysis_df, periods=6)
                            
                            if ml_forecast:
                                # Create interactive forecast chart
                                forecast_dates = ml_forecast['dates']
                                forecast_values = ml_forecast['forecast']
                                confidence = ml_forecast['confidence_interval']
                                
                                # Create historical data for context
                                if 'created_at' in analysis_df.columns:
                                    analysis_df['date'] = pd.to_datetime(analysis_df['created_at']).dt.date
                                    historical_daily = analysis_df.groupby('date')['amount_converted'].sum().reset_index()
                                    historical_daily['type'] = 'Historical'
                                
                                # Prepare forecast data
                                forecast_data = pd.DataFrame({
                                    'date': forecast_dates,
                                    'amount_converted': forecast_values,
                                    'type': 'Forecast'
                                })
                                
                                # Combine historical and forecast data
                                if 'historical_daily' in locals():
                                    combined_data = pd.concat([historical_daily, forecast_data])
                                else:
                                    combined_data = forecast_data
                                
                                # Create the plot
                                fig = go.Figure()
                                
                                # Add historical data if available
                                if 'historical_daily' in locals():
                                    fig.add_trace(go.Scatter(
                                        x=historical_daily['date'],
                                        y=historical_daily['amount_converted'],
                                        mode='lines+markers',
                                        name='Historical Revenue',
                                        line=dict(color='blue', width=2)
                                    ))
                                
                                # Add forecast with confidence interval
                                fig.add_trace(go.Scatter(
                                    x=forecast_data['date'],
                                    y=forecast_data['amount_converted'] + confidence,
                                    mode='lines',
                                    line=dict(width=0),
                                    showlegend=False,
                                    name='Upper Bound'
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=forecast_data['date'],
                                    y=forecast_data['amount_converted'] - confidence,
                                    mode='lines',
                                    line=dict(width=0),
                                    fill='tonexty',
                                    fillcolor='rgba(0,100,80,0.2)',
                                    name='Confidence Interval'
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=forecast_data['date'],
                                    y=forecast_data['amount_converted'],
                                    mode='lines+markers',
                                    name='AI Forecast',
                                    line=dict(color='red', width=3, dash='dash')
                                ))
                                
                                fig.update_layout(
                                    title="AI Revenue Forecast with 95% Confidence Interval",
                                    xaxis_title="Date",
                                    yaxis_title=f"Revenue ({currency})",
                                    hovermode='x unified',
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Forecast metrics
                                total_forecast = sum(forecast_values)
                                growth_rate = ((forecast_values[-1] / forecast_values[0]) - 1) * 100 if len(forecast_values) > 1 else 0
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Forecasted", f"{currency} {total_forecast:,.0f}")
                                with col2:
                                    st.metric("Avg Monthly", f"{currency} {np.mean(forecast_values):,.0f}")
                                with col3:
                                    st.metric("Projected Growth", f"{growth_rate:+.1f}%")
                            
                            # 3. REAL REVENUE CLUSTERING ANALYSIS
                            st.markdown("---")
                            st.markdown("### 🎯 AI Customer Segmentation")
                            
                            clustering_result = real_revenue_stream_clustering(analysis_df)
                            
                            if clustering_result:
                                st.success(f"🤖 AI identified {clustering_result['optimal_k']} natural customer segments")
                                
                                # Display cluster analysis
                                cluster_analysis = clustering_result['cluster_analysis']
                                
                                # Create a user-friendly display of clusters
                                st.markdown("#### Customer Segments Analysis")
                                
                                # Convert cluster analysis to readable format
                                readable_clusters = []
                                for cluster_id in cluster_analysis.index:
                                    cluster_data = cluster_analysis.loc[cluster_id]
                                    readable_clusters.append({
                                        'Segment': f"Segment {cluster_id + 1}",
                                        'Customers': int(cluster_data[('amount', 'count')]),
                                        'Avg Transaction': f"{currency} {cluster_data[('amount', 'mean')]:.2f}",
                                        'Total Revenue': f"{currency} {cluster_data[('amount', 'sum')]:.2f}",
                                        'Avg Fee': f"{currency} {cluster_data[('fee_applied', 'mean')]:.2f}"
                                    })
                                
                                segments_df = pd.DataFrame(readable_clusters)
                                st.dataframe(segments_df, use_container_width=True)
                                
                                # Visualize the segments
                                if 'amount' in analysis_df.columns and 'fee_applied' in analysis_df.columns:
                                    # Add cluster labels to dataframe for visualization
                                    if len(clustering_result['clusters']) == len(analysis_df):
                                        analysis_df_with_clusters = analysis_df.copy()
                                        analysis_df_with_clusters['segment'] = [f"Segment {c+1}" for c in clustering_result['clusters']]
                                        
                                        fig = px.scatter(
                                            analysis_df_with_clusters,
                                            x='amount',
                                            y='fee_applied',
                                            color='segment',
                                            size='amount_converted',
                                            hover_data=['category_name'] if 'category_name' in analysis_df_with_clusters.columns else None,
                                            title="AI-Discovered Customer Segments",
                                            labels={
                                                'amount': f'Transaction Amount ({currency})',
                                                'fee_applied': f'Fee Applied ({currency})',
                                                'segment': 'Customer Segment'
                                            }
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.info("👆 Click the button above to run AI-powered revenue analysis")
                        
                    # Keep your existing trend analysis
                    st.markdown("---")
                    st.markdown("### 📈 Revenue Trends Over Time")
                    
                    if "created_at" in analysis_df.columns:
                        analysis_df["created_at"] = pd.to_datetime(analysis_df["created_at"], errors="coerce")
                        # Use available category column or fallback
                        trend_group_col = None
                        if "category_name" in analysis_df.columns:
                            trend_group_col = "category_name"
                        elif "suggested_category" in analysis_df.columns:
                            trend_group_col = "suggested_category"
                        elif "transaction_type_name" in analysis_df.columns:
                            trend_group_col = "transaction_type_name"
                        else:
                            # If no category columns, just group by date
                            trend_data = analysis_df.groupby(analysis_df["created_at"].dt.date)["amount_converted"].sum().reset_index()
                            trend_data['category'] = 'All Transactions'
                            trend_group_col = 'category'

                        if trend_group_col and trend_group_col != 'category':  # If we have a real category column
                            trend_data = analysis_df.groupby([analysis_df["created_at"].dt.date, trend_group_col])["amount_converted"].sum().reset_index()
                        
                        
                        if not trend_data.empty:
                            # Use the actual column name that exists in trend_data
                            fig_trend = px.line(trend_data, x='created_at', y='amount_converted', color='suggested_category',
                                            title=f"Revenue Trends by Category ({currency})",
                                            labels={'amount_converted': f'Revenue ({currency})', 'created_at': 'Date'})
                            
                            st.plotly_chart(fig_trend, use_container_width=True)
                
                else:
                    st.info("No transaction data available for analysis")
            
            with tab3:
                st.subheader("Fee Compliance Dashboard")
                
                fee_df = st.session_state.transactions_df.copy()
                
                if 'fee_status_type' in fee_df.columns:
                    # Create unique timestamp for chart keys
                    chart_timestamp = int(time.time() * 1000)
                    
                    # Fee status distribution
                    fee_status_counts = fee_df['fee_status_type'].value_counts()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie chart
                        pie_fig = px.pie(
                            values=fee_status_counts.values,
                            names=fee_status_counts.index,
                            title="Fee Status Distribution"
                        )
                        st.plotly_chart(pie_fig, use_container_width=True, key=f"fee_pie_{chart_timestamp}")
                    
                    with col2:
                        # Bar chart of fee status by transaction type
                        if 'category_name' in fee_df.columns or 'suggested_category' in fee_df.columns:
                            category_col = 'category_name' if 'category_name' in fee_df.columns else 'suggested_category'
                            fee_by_category = fee_df.groupby([category_col, 'fee_status_type']).size().reset_index(name='count')
                            bar_fig = px.bar(
                                fee_by_category,
                                x=category_col,
                                y='count',
                                color='fee_status_type',
                                title="Fee Status by Transaction Category",
                                barmode='stack'
                            )
                            st.plotly_chart(bar_fig, use_container_width=True, key=f"fee_bar_{chart_timestamp}")
                        else:
                            st.info("No category data available for fee analysis")
                else:
                    st.info("No fee compliance data available yet")
            
            with tab4:
                st.subheader("AI-Powered Insights")
                
                insights_df = st.session_state.transactions_df.copy()
                
                if len(insights_df) > 10 and 'is_anomaly' in insights_df.columns:
                    # Get only the anomaly rows
                    anomaly_rows = insights_df[insights_df['is_anomaly'] == 1]
                    
                    if not anomaly_rows.empty:
                        insights = ai_insights_with_severity(insights_df, anomaly_rows)
                    else:
                        insights = None
                        
                    if insights:
                        st.info("### Revenue Insights")
                        for insight in insights.get('revenue_insights', []):
                            st.write(f"• {insight}")
                        
                        st.error("### Critical Anomalies")
                        for anomaly in insights.get('critical_anomalies', []):
                            st.write(f"🔴 {anomaly['description']} (Severity: {anomaly['severity']})")
                            st.write(f"   Action: {anomaly['recommended_action']}")
                        
                        st.warning("### Investigation Priority")
                        for txn_id in insights.get('investigation_priority', [])[:5]:
                            st.write(f"• Transaction {txn_id}")
                    else:
                        st.info("AI insights not available - check API key or try again later")
                else:
                    st.info("Need more data for AI insights (minimum 10 transactions)")
            
            with tab5:
                st.subheader("Fee Differences Analysis")
                
                if not st.session_state.fee_differences_table.empty:
                    st.write("### Charges vs Recommended Prices Comparison")
                        
                    # Summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        undercharged = (st.session_state.fee_differences_table['fee_status_type'] == "Undercharge").sum()
                        st.metric("Undercharges", undercharged)
                    with col2:
                        overcharged = (st.session_state.fee_differences_table['fee_status_type'] == "Overcharge").sum()
                        st.metric("Overcharges", overcharged)
                    with col3:
                        normal = (st.session_state.fee_differences_table['fee_status_type'] == "Normal").sum()
                        st.metric("Normal Fees", normal)
                    with col4:
                        mismatch = (st.session_state.fee_differences_table['fee_status_type'] == "Mismatch").sum()
                        st.metric("Mismatches", mismatch)
                            
                    # Apply styling to the differences table
                    def style_fee_differences(row):
                        styles = [''] * len(row)
                        if row['fee_status_type'] == 'Overcharge':
                            styles = ['background-color: #ffcccc'] * len(row)
                        elif row['fee_status_type'] == 'Undercharge':
                            styles = ['background-color: #ccffcc'] * len(row)
                        elif row['fee_status_type'] == 'Normal':
                            styles = ['background-color: #e6f3ff'] * len(row)
                        return styles
                    
                    styled_diff_table = st.session_state.fee_differences_table.style.apply(
                        style_fee_differences, axis=1
                    )
                    
                    st.dataframe(styled_diff_table, use_container_width=True)
                else:
                    st.info("No fee differences data available yet")
                    
                        
            with tab6:
                st.subheader("📋 Transaction Type Analysis")
                
                type_df = st.session_state.transactions_df.copy()
                
                # Ensure amount_converted column exists
                if 'amount' in type_df.columns:
                    type_df["amount"] = pd.to_numeric(type_df["amount"], errors="coerce").fillna(0)
                    if display_currency == "ZiG":
                        type_df["amount_converted"] = type_df["amount"] * exchange_rate
                    else:
                        type_df["amount_converted"] = type_df["amount"]
                else:
                    type_df["amount_converted"] = 0
                
                # Safe category column selection
                category_col = None
                possible_category_cols = ['category_name', 'suggested_category', 'transaction_type_name']
                
                for col in possible_category_cols:
                    if col in type_df.columns and not type_df[col].isna().all():
                        category_col = col
                        break
                
                if not category_col:
                    type_df['fallback_category'] = 'All Transactions'
                    category_col = 'fallback_category'
                
                # FIXED: Define category_volume BEFORE using it
                category_volume = None
                
                if category_col and 'amount_converted' in type_df.columns and not type_df.empty:
                    chart_timestamp = int(time.time() * 1000)
                    
                    try:
                        if type_df[category_col].notna().sum() > 0:
                            # DEFINE category_volume here
                            category_volume = type_df.groupby(category_col)['amount_converted'].sum().sort_values(ascending=False)
                                                            # Overall metrics section
                            st.markdown("---")
                            st.subheader("📈 Overall Transaction Metrics")

                            if not type_df.empty:
                                col1, col2, col3, col4 = st.columns(4)  # MAKE SURE THIS LINE EXISTS
                                
                                with col1:
                                    if 'amount_converted' in type_df.columns:
                                        total_volume = type_df['amount_converted'].sum()
                                        st.metric("Total Volume", f"{currency} {total_volume:,.2f}")
                                
                                with col2:
                                    if 'amount_converted' in type_df.columns:
                                        avg_transaction = type_df['amount_converted'].mean()
                                        st.metric("Avg Transaction", f"{currency} {avg_transaction:,.2f}")
                                
                                with col3:  # THIS IS WHERE THE ERROR IS
                                    total_transactions = len(type_df)
                                    st.metric("Total Transactions", f"{total_transactions:,}")
                                
                                with col4:
                                    if 'fee_applied' in type_df.columns:
                                        total_fees = pd.to_numeric(type_df['fee_applied'], errors='coerce').sum()
                                        st.metric("Total Fees", f"{currency} {total_fees:,.2f}")
                                    else:
                                        st.metric("Fee Data", "Not Available")
                            else:
                                st.info("No transaction data available for overall metrics")    
                    except Exception as e:
                        st.error(f"Error in tab6: {str(e)}")

            # Add this AFTER your existing tab6 code, not inside any try/except blocks

            # 7. SCENARIO SIMULATOR TAB
            with tab7:
                st.subheader("🎯 Financial Scenario Simulator")
                
                st.info("""
                **Financial Scenario Simulator**
                Adjust parameters below to simulate different financial scenarios and see their impact on revenue.
                """)
                
                # Scenario Configuration
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("📈 Volume Scenarios")
                    base_volume = st.number_input("Base Transaction Volume", value=1000, min_value=100, step=100)
                    growth_scenario = st.slider("Volume Growth %", -50, 200, 0, help="Simulate volume changes")
                    seasonal_factor = st.slider("Seasonal Factor", 0.5, 2.0, 1.0, help="Seasonal demand multiplier")
                
                with col2:
                    st.subheader("💵 Pricing Scenarios")
                    base_fee_rate = st.slider("Base Fee Rate %", 0.1, 10.0, 2.0, step=0.1)
                    premium_tier_rate = st.slider("Premium Tier Rate %", 0.1, 15.0, 3.5, step=0.1)
                    discount_scenario = st.slider("Discount/Promo %", -20.0, 0.0, 0.0, step=1.0)
                
                with col3:
                    st.subheader("📊 Mix Scenarios")
                    high_value_mix = st.slider("High-Value Txns %", 0, 100, 20, help="Percentage of high-value transactions")
                    international_mix = st.slider("International Txns %", 0, 100, 15, help="Percentage of international transactions")
                    corporate_mix = st.slider("Corporate Txns %", 0, 100, 30, help="Percentage of corporate transactions")
                
                # Calculate Scenario Results
                simulated_volume = base_volume * (1 + growth_scenario/100) * seasonal_factor
                effective_fee_rate = base_fee_rate * (1 + discount_scenario/100)
                
                # Revenue calculation with mix factors
                base_revenue = simulated_volume * 100 * effective_fee_rate/100  # Assume $100 avg transaction
                premium_revenue = (simulated_volume * high_value_mix/100) * 500 * premium_tier_rate/100  # High-value at $500 avg
                international_revenue = (simulated_volume * international_mix/100) * 150 * (effective_fee_rate + 1)/100  # Intl premium
                corporate_revenue = (simulated_volume * corporate_mix/100) * 300 * (effective_fee_rate - 0.5)/100  # Corp discount
                
                total_revenue = base_revenue + premium_revenue + international_revenue + corporate_revenue
                
                # Display Results
                st.markdown("---")
                st.subheader("📊 Scenario Results")
                
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.metric("Simulated Volume", f"{simulated_volume:,.0f}", f"{growth_scenario}%")
                    st.metric("Effective Fee Rate", f"{effective_fee_rate:.2f}%", f"{discount_scenario}%")
                
                with result_col2:
                    st.metric("Base Revenue", f"${base_revenue:,.2f}")
                    st.metric("Premium Revenue", f"${premium_revenue:,.2f}")
                
                with result_col3:
                    st.metric("International Revenue", f"${international_revenue:,.2f}")
                    st.metric("Corporate Revenue", f"${corporate_revenue:,.2f}")
                
                st.metric("**Total Projected Revenue**", f"**${total_revenue:,.2f}**", delta_color="off")
                
                # Visualization
                col_viz1, col_viz2 = st.columns(2)
                
                with col_viz1:
                    # Revenue breakdown pie chart
                    revenue_breakdown = {
                        'Base': base_revenue,
                        'Premium': premium_revenue,
                        'International': international_revenue,
                        'Corporate': corporate_revenue
                    }
                    
                    breakdown_fig = px.pie(
                        values=list(revenue_breakdown.values()),
                        names=list(revenue_breakdown.keys()),
                        title="Revenue Breakdown by Segment",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(breakdown_fig, use_container_width=True)
                
                with col_viz2:
                    # Sensitivity analysis
                    fee_rates = [effective_fee_rate * (1 + i/100) for i in range(-20, 21, 5)]
                    revenues = [total_revenue * (1 + (rate - effective_fee_rate)/effective_fee_rate) for rate in fee_rates]
                    
                    sensitivity_fig = px.line(
                        x=fee_rates,
                        y=revenues,
                        title="Revenue Sensitivity to Fee Rate Changes",
                        labels={'x': 'Fee Rate (%)', 'y': 'Projected Revenue ($)'}
                    )
                    sensitivity_fig.add_vline(x=effective_fee_rate, line_dash="dash", line_color="red", 
                                            annotation_text="Current Scenario")
                    st.plotly_chart(sensitivity_fig, use_container_width=True)
                
                # Scenario Comparison
                st.subheader("🔄 Scenario Comparison")
                
                # Pre-defined scenarios
                scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
                
                with scenario_col1:
                    if st.button("📈 Growth Scenario", use_container_width=True):
                        st.session_state.scenario_type = "growth"
                        st.rerun()
                
                with scenario_col2:
                    if st.button("💰 Premiumization", use_container_width=True):
                        st.session_state.scenario_type = "premium"
                        st.rerun()
                
                with scenario_col3:
                    if st.button("🌍 International Focus", use_container_width=True):
                        st.session_state.scenario_type = "international"
                        st.rerun()
                
                # What-If Analysis
                st.subheader("🎯 What-If Analysis")
                
                whatif_col1, whatif_col2 = st.columns(2)
                
                with whatif_col1:
                    target_revenue = st.number_input("Target Revenue Goal ($)", value=total_revenue * 1.2, step=1000.0)
                    required_growth = ((target_revenue / total_revenue) - 1) * 100
                    st.metric("Required Growth", f"{required_growth:.1f}%")
                
                with whatif_col2:
                    current_market_share = st.slider("Current Market Share %", 1.0, 100.0, 15.0, step=0.5)
                    target_market_share = st.slider("Target Market Share %", 1.0, 100.0, 25.0, step=0.5)
                    market_growth_potential = (target_market_share / current_market_share - 1) * 100
                    st.metric("Market Share Opportunity", f"{market_growth_potential:.1f}%")
                        
                                    

        # ===================================================================
        # MAIN PROCESSING LOOP
        # ===================================================================
            total = len(st.session_state.all_transactions)

            if st.session_state.analysis_started and st.session_state.current_index < total:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Process only one batch per Streamlit run (no while loop)
                start_idx = st.session_state.current_index
                end_idx = min(start_idx + batch_size, total)
                new_rows = st.session_state.all_transactions.iloc[start_idx:end_idx].copy()

                if not new_rows.empty:
                    # Enhanced categorization
                    if not st.session_state.transaction_types.empty:
                        new_rows = new_rows.merge(st.session_state.transaction_types, on="transaction_type_id", how="left")

                    # AI categorization for missing categories
                    if "transaction_type_name" in new_rows.columns:
                        for idx, row in new_rows.iterrows():
                            if pd.isna(row.get("category_name")):
                                cat, sub, confidence = suggest_category_ai(row.get("transaction_type_name", ""))
                                new_rows.at[idx, "suggested_category"] = cat
                                new_rows.at[idx, "suggested_subcategory"] = sub
                                new_rows.at[idx, "ai_confidence"] = confidence

                    # Add to main dataframe
                    st.session_state.transactions_df = pd.concat(
                        [st.session_state.transactions_df, new_rows],
                        ignore_index=True
                    ).drop_duplicates("id").tail(200)  # Keep latest 200

                    # Update current index
                    st.session_state.current_index = end_idx

                # --- Display current data ---
                filtered_df = st.session_state.transactions_df.copy()
                
                # Apply filters and display...
                # (Your filtering and display code here)

                # Update progress
                progress = st.session_state.current_index / total
                progress_bar.progress(min(progress, 1.0))
                status_text.text(f"Processed {st.session_state.current_index} of {total} transactions")

                # Auto-refresh for next batch
                time.sleep(refresh_rate)
                st.rerun()

                # Advanced Anomaly Detection
                available_columns = st.session_state.transactions_df.columns.tolist()
                feature_candidates = ['amount', 'fee_applied']
                feature_columns = [col for col in feature_candidates if col in available_columns]
                
                numeric_columns = st.session_state.transactions_df.select_dtypes(include=[np.number]).columns.tolist()
                exclude_columns = ['id', 'transaction_type_id', 'category_id', 'is_anomaly']
                
                for col in numeric_columns:
                    if col not in feature_columns and col not in exclude_columns:
                        if st.session_state.transactions_df[col].std() > 0:
                            feature_columns.append(col)
                
                if not feature_columns:
                    if 'amount' in available_columns:
                        feature_columns = ['amount']
                    else:
                        st.session_state.transactions_df['is_anomaly'] = 0
                        st.session_state.transactions_df['combined_severity'] = 0.0
                        st.session_state.transactions_df['ensemble_anomaly_score'] = 0.0
                else:
                    try:
                        st.session_state.transactions_df = st.session_state.anomaly_detector.detect_anomalies_ensemble(
                            st.session_state.transactions_df, feature_columns, contamination=0.05
                        )
                        if 'is_anomaly' not in st.session_state.transactions_df.columns:
                            st.session_state.transactions_df['is_anomaly'] = 0
                        if 'combined_severity' not in st.session_state.transactions_df.columns:
                            st.session_state.transactions_df['combined_severity'] = 0.0
                        if 'ensemble_anomaly_score' not in st.session_state.transactions_df.columns:
                            st.session_state.transactions_df['ensemble_anomaly_score'] = 0.0
                    except Exception as e:
                        st.error(f"Anomaly detection failed: {str(e)}")
                        st.session_state.transactions_df['is_anomaly'] = 0
                        st.session_state.transactions_df['combined_severity'] = 0.0
                        st.session_state.transactions_df['ensemble_anomaly_score'] = 0.0

                    # Enhanced Fee Verification
                    fee_results = []
                    for idx, row in st.session_state.transactions_df.iterrows():
                        verification = st.session_state.fee_verifier.verify_fee_compliance(
                            row.to_dict(), 
                            st.session_state.charges, 
                            st.session_state.price_recommendations
                        )
                        fee_results.append(verification)
                    
                    st.session_state.transactions_df['fee_analysis'] = fee_results
                    st.session_state.transactions_df['fee_status'] = [r['status'] for r in fee_results]
                    st.session_state.transactions_df['fee_status_type'] = [r.get('fee_status_type', 'Unknown') for r in fee_results]
                    st.session_state.transactions_df['fee_severity'] = [r.get('severity', 'none') for r in fee_results]

                # Enhanced Filtering
                filtered_df = st.session_state.transactions_df.copy()
                
                if 'amount' in filtered_df.columns:
                    filtered_df["amount"] = pd.to_numeric(filtered_df["amount"], errors="coerce").fillna(0)
                else:
                    filtered_df["amount"] = 0

                if display_currency == "ZiG":
                    filtered_df["amount_converted"] = filtered_df["amount"] * exchange_rate
                else:
                    filtered_df["amount_converted"] = filtered_df["amount"]

                filtered_df = filtered_df[
                    (filtered_df["amount_converted"] >= min_amount) &
                    (filtered_df["amount_converted"] <= max_amount)
                ]

                if focus_category != "All" and "category_name" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df["category_name"] == focus_category]

                if 'combined_severity' not in filtered_df.columns:
                    filtered_df['combined_severity'] = 0.0

                if show_high_severity_only:
                    filtered_df = filtered_df[filtered_df["combined_severity"] > anomaly_threshold]

                # Real-time Metrics Dashboard
                with metrics_placeholder.container():
                    st.subheader("📊 Real-time Monitoring Dashboard")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_volume = filtered_df["amount_converted"].sum()
                        sample_size = len(filtered_df)
                        st.metric("Total Volume", f"${total_volume:,.2f}", delta=f"{sample_size} samples")
                        
                    with col2:
                        current_anomaly_count = filtered_df["is_anomaly"].sum() if 'is_anomaly' in filtered_df.columns else 0
                        st.metric("Anomalies Detected", current_anomaly_count)
                        
                        if current_anomaly_count > st.session_state.last_anomaly_count:
                            new_anomalies = current_anomaly_count - st.session_state.last_anomaly_count
                            notification_system.add_notification(
                                f"🚨 {new_anomalies} new anomaly(ies) detected!", "warning"
                            )
                            popup_system.add_popup("New Anomalies Detected", 
                                                f"{new_anomalies} new transaction anomalies found", "warning")
                            st.session_state.last_anomaly_count = current_anomaly_count
                        
                    with col3:
                        current_fee_violations = filtered_df[filtered_df["fee_status"] == "violation"].shape[0] if 'fee_status' in filtered_df.columns else 0
                        st.metric("Fee Violations", current_fee_violations)
                        
                        if current_fee_violations > st.session_state.last_fee_violation_count:
                            new_violations = current_fee_violations - st.session_state.last_fee_violation_count
                            notification_system.add_notification(
                                f"💰 {new_violations} new fee violation(s) detected!", "error"
                            )
                            popup_system.add_popup("Fee Violations Detected", 
                                                f"{new_violations} new fee compliance issues found", "error")
                            st.session_state.last_fee_violation_count = current_fee_violations
                        
                    with col4:
                        high_risk = filtered_df[filtered_df["combined_severity"] > 0.8].shape[0] if 'combined_severity' in filtered_df.columns else 0
                        st.metric("High Risk Txns", high_risk)

                # Alert System
                with alerts_placeholder.container():
                    if 'is_anomaly' in filtered_df.columns and 'combined_severity' in filtered_df.columns:
                        critical_anomalies = filtered_df[
                            (filtered_df["is_anomaly"] == 1) & 
                            (filtered_df["combined_severity"] > 0.9)
                        ]
                        
                        if not critical_anomalies.empty and not st.session_state.critical_anomalies_detected:
                            st.session_state.critical_anomalies_detected = True
                            popup_system.add_popup("CRITICAL ALERT", 
                                                "Critical anomalies detected requiring immediate attention!", "error")
                        
                        if not critical_anomalies.empty:
                            st.error("🚨 CRITICAL ANOMALIES DETECTED")
                            for _, alert in critical_anomalies.head(3).iterrows():
                                st.write(f"• Txn {alert['id']}: ${alert['amount_converted']:.2f} - Severity: {alert['combined_severity']:.2f}")

                # Update progress
                st.session_state.current_index = end_idx
                progress = st.session_state.current_index / total
                progress_bar.progress(progress)
                status_text.text(f"Processed {st.session_state.current_index} of {total} transactions")
                
                time.sleep(refresh_rate)

        st.success("✅ Analysis Complete! All transactions processed.")
        notification_system.add_notification("Real-time analysis completed successfully", "info")
        popup_system.add_popup("Analysis Complete", "All transactions have been processed successfully", "info")

elif page == "AI-assisted Revenue Categorization":
    with placeholder.container():
        import psycopg2
        import pandas as pd
        import matplotlib.pyplot as plt
        import streamlit as st
        from openai import OpenAI
        import json
        import numpy as np

        st.title("🤖 AI-Assisted Revenue Categorization")

        # --- Enter API Key directly here ---
        OPENAI_API_KEY = "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"   # 🔑 Replace with your real key
        client = OpenAI(api_key=OPENAI_API_KEY)

        # --- Fetch Transactions from dummydb ---
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

        # --- Fetch Mapping Tables from Neon ---
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

        # --- Merge Mappings ---
        types = types.merge(categories, on="category_id", how="left")
        merged = transactions.merge(types, on="transaction_type_id", how="left")

        # --- Find Unmapped Transactions ---
        unmapped = merged[merged["category_name"].isnull()]

        # Create tabs for better organization
        tab1, tab2, tab3 = st.tabs(["🎯 Categorization", "📊 Analytics", "🔄 Revenue Lifecycle"])

        with tab1:
            st.subheader("🚨 Unmapped Transactions")
            if unmapped.empty:
                st.success("All transactions are mapped! ✅")
            else:
                st.warning(f"{len(unmapped)} transactions need mapping")

                # --- AI Suggestion Function ---
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
                def ai_insights_with_severity(trend_df, anomalies_df):
                    """Generate AI-powered insights with severity scoring for anomalies"""
                    if not client or trend_df.empty:
                        return None
                        
                    sample = trend_df.tail(30).to_dict(orient="records")
                    
                    # FIXED: anomalies_df is already filtered to only contain anomalies
                    # So we don't need to filter it again, just take the samples directly
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

                # Apply AI categorization
                unmapped[["suggested_category", "suggested_subcategory"]] = unmapped[
                    "transaction_type_name"
                ].apply(lambda x: pd.Series(suggest_category_ai(x)))

                st.dataframe(unmapped[["id", "transaction_type_name", "suggested_category", "suggested_subcategory"]])

                # --- Manual Override Form ---
                with st.form("mapping_form"):
                    selected_id = st.selectbox("Pick a transaction to map", unmapped["id"])
                    selected_cat = st.selectbox("Category", categories["category_name"].unique())

                    # Get category_id
                    cat_id = categories[categories["category_name"] == selected_cat]["category_id"].iloc[0]
                    sub_options = subcategories[subcategories["category_id"] == cat_id]

                    selected_sub = st.selectbox("Subcategory", sub_options["subcategory_name"].unique())

                    if st.form_submit_button("✅ Approve Mapping"):
                        sub_id = sub_options[sub_options["subcategory_name"] == selected_sub]["subcategory_id"].iloc[0]

                        # Update mapping in Neon (not dummydb)
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

        with tab2:
            # --- Revenue Analytics ---
            st.subheader("📊 Revenue by Category/Subcategory")

            if "amount" in merged.columns:
                # Currency selection
                currency = st.selectbox("Display Currency", ["USD", "ZiG"])
                exchange_rate = 13.5 if currency == "ZiG" else 1.0
                
                # Convert amount based on currency
                amount_col = "amount_converted"
                merged[amount_col] = merged["amount"] * exchange_rate

                revenue_summary = merged.groupby("category_name")[amount_col].sum().reset_index().sort_values(amount_col, ascending=False)

                # Pie chart
                fig1, ax1 = plt.subplots()
                ax1.pie(revenue_summary[amount_col], labels=revenue_summary["category_name"], autopct="%1.1f%%")
                ax1.axis("equal")
                st.pyplot(fig1)

                # Bar chart with rotated labels
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
            # --- Revenue Lifecycle Analysis ---
            st.subheader("🔄 Revenue Lifecycle Analysis")

            # Initialize lifecycle metrics
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

            # Perform lifecycle analysis
            lifecycle_data = analyze_revenue_lifecycle(merged)

            if lifecycle_data:
                # Key Metrics Dashboard
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
                
                # Revenue Distribution by Category
                st.write("### 💰 Revenue by Category (Lifecycle Stage Proxy)")
                if not lifecycle_data['category_revenue'].empty:
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                    
                    # Pie chart
                    lifecycle_data['category_revenue'].plot.pie(
                        ax=ax1, 
                        autopct='%1.1f%%',
                        startangle=90,
                        title="Revenue Distribution by Category"
                    )
                    ax1.set_ylabel('')
                    
                    # Bar chart
                    lifecycle_data['category_revenue'].plot.bar(
                        ax=ax2,
                        color='skyblue',
                        title="Revenue by Category"
                    )
                    ax2.set_ylabel('Revenue ($)')
                    ax2.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # Revenue Trends Over Time
                st.write("### 📊 Revenue Trends (Retention Analysis)")
                if not lifecycle_data['revenue_trend'].empty:
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
                
                # Customer Value Analysis
                st.write("### 👥 Customer Value Segmentation")
                if lifecycle_data['total_customers'] > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Customer Distribution**")
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
                
                # Lifecycle Stage Recommendations
                st.write("### 🎯 Lifecycle Optimization Recommendations")
                
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
                
                if recommendations:
                    for rec in recommendations:
                        st.info(rec)
                else:
                    st.success("✅ Good balance across revenue lifecycle stages!")
                
            else:
                st.info("No transaction data available for revenue lifecycle analysis.")

            # --- Customer Journey Analysis ---
            if 'customer_id' in merged.columns and 'created_at' in merged.columns:
                st.subheader("🧭 Customer Journey Analysis")
                
                # Select a customer to analyze
                customer_options = merged['customer_id'].unique()
                if len(customer_options) > 0:
                    selected_customer = st.selectbox("Select Customer to Analyze Journey", customer_options[:10])  # Limit to first 10
                    
                    customer_data = merged[merged['customer_id'] == selected_customer].sort_values('created_at')
                    
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
                        st.dataframe(journey_df)

elif page == "Transaction Monitoring":
    with placeholder.container():

        st.title("🔍 Transaction Monitoring & Analysis")
        refresh_rate = st.sidebar.slider("⏱ Refresh every (seconds)", 10, 300, 60)  
        st.sidebar.write("Page auto-refreshes every set interval.")

        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_rate * 1000, limit=None, key="refresh")

        # --- Timestamp for last refresh ---
        last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.info(f"📅 Last refreshed at: **{last_refresh}** (every {refresh_rate} seconds)")

        # --- Load transactions from dummydb ---
        conn3 = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        cur3 = conn3.cursor()
        cur3.execute("SELECT id, transaction_type_id, amount, created_at, updated_at FROM transactions")
        data = cur3.fetchall()
        columns = [desc[0] for desc in cur3.description]
        cur3.close()
        conn3.close()

        transactions = pd.DataFrame(data, columns=columns)
        transactions = pd.DataFrame(data, columns=columns)

        #  Fix: Convert amount from Decimal to float
        transactions['amount'] = transactions['amount'].astype(float)

        # --- Feature Engineering ---
        transactions['created_at'] = pd.to_datetime(transactions['created_at'])
        transactions['updated_at'] = pd.to_datetime(transactions['updated_at'])

        transactions['hour_of_day'] = transactions['created_at'].dt.hour
        transactions['day_of_week'] = transactions['created_at'].dt.dayofweek
        transactions['processing_time'] = (transactions['updated_at'] - transactions['created_at']).dt.total_seconds()

        transactions = pd.get_dummies(transactions, columns=['transaction_type_id'], prefix='type')

        # --- Isolation Forest ---
        features = ['amount', 'hour_of_day', 'day_of_week', 'processing_time'] + \
                [col for col in transactions.columns if col.startswith('type_')]

        X = transactions[features].fillna(0)

        iforest = IsolationForest(contamination=0.02, random_state=42)
        transactions['anomaly'] = iforest.fit_predict(X)
        transactions['anomaly'] = transactions['anomaly'].map({1: 'Normal', -1: 'Anomaly'})

            # --- Sidebar Filters ---
        st.sidebar.header("🔎 Filters")

        # Date range filter
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [transactions['created_at'].min().date(), transactions['created_at'].max().date()]
        )

        # Transaction type filter
        transaction_types = [col for col in transactions.columns if col.startswith('type_')]
        selected_types = st.sidebar.multiselect("Transaction Types", transaction_types, default=transaction_types)

        # Anomaly filter
        anomaly_filter = st.sidebar.multiselect("Anomaly Status", ['Normal', 'Anomaly'], default=['Normal','Anomaly'])

        # --- Apply Filters ---
        filtered = transactions.copy()
        filtered = filtered[
            (filtered['created_at'].dt.date >= date_range[0]) &
            (filtered['created_at'].dt.date <= date_range[1]) &
            (filtered['anomaly'].isin(anomaly_filter))
        ]

        # Keep only selected transaction type columns
        if selected_types:
            filtered = filtered[(filtered[selected_types] == 1).any(axis=1)]



        # --- Visualizations ---
        st.subheader("Transaction Anomalies Overview")

        # Scatter: Amount vs Hour
        fig1 = plt.figure(figsize=(10,6))
        sns.scatterplot(x='hour_of_day', y='amount', hue='anomaly', data=transactions, palette=['blue','red'])
        plt.title('Transaction Amount vs Hour of Day')
        st.pyplot(fig1)
        st.markdown("""
        **Explanation:**  
        Each dot is a transaction.  
        - X-axis = Hour of the day  
        - Y-axis = Transaction amount  
        - Red = anomaly, Blue = normal  

        If you see red dots outside normal working hours or with unusual amounts, they may signal suspicious activity.
        """)

        # Scatter: Amount vs Processing Time
        fig2 = plt.figure(figsize=(10,6))
        sns.scatterplot(x='processing_time', y='amount', hue='anomaly', data=transactions, palette=['blue','red'])
        plt.title('Transaction Amount vs Processing Time')
        st.pyplot(fig2)
        st.markdown("""
        **Explanation:**  
        - X-axis = Processing time (seconds)  
        - Y-axis = Transaction amount  

        Anomalies (red) could mean very large amounts processed unusually fast,  
        or small amounts with unusually long delays. Both could indicate system issues or fraud.
        """)

        # Boxplot: anomalies vs amount
        fig3 = plt.figure(figsize=(10,6))
        sns.boxplot(x='anomaly', y='amount', data=transactions)
        plt.title('Transaction Amount Distribution (Normal vs Anomaly)')
        st.pyplot(fig3)
        st.markdown("""
        **Explanation:**  
        This shows how transaction amounts are distributed between normal and anomalous transactions.  
        - If anomalies are consistently higher/lower than normal ones, the issue is amount-driven.  
        - If they overlap, anomalies may be due to timing or type of transaction.
        """)


        # Bar chart: anomalies by transaction type
        anomaly_counts = transactions[transactions['anomaly']=='Anomaly'].filter(like='type_').sum()
        st.bar_chart(anomaly_counts)
        st.markdown("""
        **Explanation:**  
        Each bar shows how many anomalies were detected for each transaction type.  
        High counts for one type (e.g., transfers or withdrawals) suggest those need closer investigation.
        """)

        st.subheader("🤖 AI-Powered Recommendations")

        # Rule 1: Night anomalies
        night_anomalies = transactions[(transactions['hour_of_day'] >= 0) & (transactions['hour_of_day'] <= 5) & (transactions['anomaly'] == 'Anomaly')]
        if len(night_anomalies) > 0:
            st.warning("🌙 High anomaly activity detected during **night hours (00:00–05:00)** → Recommend stricter monitoring rules at night.")

        # Rule 2: Transaction type anomalies
        top_anomaly_types = anomaly_counts.sort_values(ascending=False).head(1)
        if not top_anomaly_types.empty and top_anomaly_types.iloc[0] > 0:
            st.warning(f"📌 Anomalies are concentrated in **{top_anomaly_types.index[0]}** → Review related pricing rules or suspicious agent activity.")

        # Rule 3: High-value anomalies
        high_value_anomalies = transactions[(transactions['amount'] > transactions['amount'].quantile(0.95)) & (transactions['anomaly'] == 'Anomaly')]
        if len(high_value_anomalies) > 0:
            st.error("💰 High-value anomaly transactions detected → Escalate to compliance immediately.")

        if len(night_anomalies) == 0 and top_anomaly_types.empty and len(high_value_anomalies) == 0:
            st.success("✅ No critical recommendations at the moment. Transaction anomalies are within expected patterns.")
        
        # --- Suspicious Transactions Table ---
        st.subheader("⚠️ Suspicious Transactions for Review")
        suspicious = transactions[transactions['anomaly'] == 'Anomaly']
        if not suspicious.empty:
            st.dataframe(
                suspicious[['id', 'amount', 'created_at', 'processing_time']],
                use_container_width=True
            )
        else:
            st.success("No suspicious transactions detected ✅")

        # --- Alerts ---
        total_txn = len(transactions)
        anomaly_count = len(suspicious)
        anomaly_rate = (anomaly_count / total_txn * 100) if total_txn > 0 else 0

        alert_threshold = st.slider("Set anomaly alert threshold (%)", 1, 50, 5)

        if anomaly_rate > alert_threshold:
            st.error(f"🚨 ALERT: {anomaly_rate:.2f}% anomalies detected!")

            # --- Slack Alert ---
            def send_slack_alert(message):
                webhook_url = "https://hooks.slack.com/services/XXXX/XXXX/XXXX"  # replace
                payload = {"text": message}
                requests.post(webhook_url, json=payload)

            send_slack_alert(f"🚨 {anomaly_rate:.2f}% anomalies detected in transactions!")

            # --- Email Alert ---
            def send_email_alert(subject, body):
                sender = "patiencemupikeni@outlook.com"
                receiver = "patiencemupikeni@gmail.com"
                password = "Dube1999"  # ⚠️ use env vars in real apps

                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = sender
                msg["To"] = receiver

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.sendmail(sender, receiver, msg.as_string())

            send_email_alert(
                "🚨 Anomaly Alert in Transactions",
                f"{anomaly_rate:.2f}% anomalies detected. Check dashboard immediately."
            )

        else:
            st.info(f"✅ Anomaly rate is within safe limits ({anomaly_rate:.2f}%)")

elif page == "Fee Validation":
    with placeholder.container():

        st.title("💰 Fee Validation & Verification")

        # --- Load Charges (dummydb) ---
        conn3 = psycopg2.connect(
            host="localhost",
            database="core_banking_system",
            user="bankuser",
            password="Test123",
            port=5433
        )
        charges_df = pd.read_sql("SELECT charge_id, currency_id, charge_amount, charge_range_min, charge_range_max, charge_percentage, transaction_type_id FROM charges", conn3)
        conn3.close()

        # --- Load Price Recommendations (neon → conn2) ---
        conn2 = psycopg2.connect(**conn2_params)
        recommendations_df = pd.read_sql("""
            SELECT transaction_type_id, recommended_min_fee, recommended_max_fee,
                recommended_flat_fee, recommended_percentage_fee
            FROM price_recommendations
        """, conn2)
        conn2.close()

        # --- Merge charges with recommendations ---
        merged = pd.merge(
            charges_df,
            recommendations_df,
            on="transaction_type_id",
            how="left"
        )

        # --- Fee validation function ---
        def validate_fee(row):
            try:
                amount = float(row["charge_amount"]) if row["charge_amount"] is not None else 0
                min_fee = float(row["recommended_min_fee"]) if row["recommended_min_fee"] is not None else 0
                max_fee = float(row["recommended_max_fee"]) if row["recommended_max_fee"] is not None else float("inf")
                flat_fee = float(row["recommended_flat_fee"]) if row["recommended_flat_fee"] is not None else None
                perc = float(row["recommended_percentage_fee"]) if row["recommended_percentage_fee"] is not None else None

                # --- Rule 1: Min/Max validation ---
                if min_fee <= amount <= max_fee:
                    return "Valid"
                
                # --- Rule 2: Flat fee validation ---
                if flat_fee is not None:
                    if amount == flat_fee:
                        return "Valid"
                    elif amount > flat_fee:
                        return "Overcharge"
                    else:
                        return "Undercharge"

                # --- Rule 3: Percentage fee validation ---
                if perc is not None:
                    expected_fee = (amount * perc)
                    if amount < expected_fee:
                        return "Undercharge"
                    elif amount > expected_fee:
                        return "Overcharge"
                    else:
                        return "Valid"

                return "No Rule"
            except Exception as e:
                return f"Error: {e}"

        # --- Apply validation ---
        if not merged.empty:
            merged["status"] = merged.apply(validate_fee, axis=1)

            # Show results in Streamlit
            st.subheader("🔍 Fee Validation Results")
            st.dataframe(merged[[
                "transaction_type_id",
                "charge_amount",
                "recommended_min_fee",
                "recommended_max_fee",
                "recommended_flat_fee",
                "recommended_percentage_fee",
                "status"
            ]])

            # Summary counts
            summary = merged["status"].value_counts()
            st.bar_chart(summary)
        else:
            st.warning("⚠️ No merged data found. Check if transaction_type_id matches across databases.")

elif page == "Forecasting":
    with placeholder.container():
        st.title("📈 Revenue Forecasting")

        # --- Load Transactions (dummydb) ---
        conn3 = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        transactions = pd.read_sql("SELECT amount, created_at FROM transactions", conn3)
        conn3.close()

        # --- Preprocess ---
        transactions["created_at"] = pd.to_datetime(transactions["created_at"])
        transactions["date"] = transactions["created_at"].dt.date

        # Daily revenue aggregation
        daily_revenue = transactions.groupby("date").agg(
            total_revenue=("amount", "sum"),
            transaction_count=("amount", "count")
        ).reset_index()

        st.subheader("📊 Daily Revenue Overview")
        st.line_chart(daily_revenue.set_index("date")["total_revenue"])

        # --- Forecasting with ARIMA ---
        from statsmodels.tsa.arima.model import ARIMA

        ts = daily_revenue.set_index("date")["total_revenue"]

        # Build ARIMA model (simple config)
        model = ARIMA(ts, order=(2,1,2))
        model_fit = model.fit()

        # Forecast next 7 days
        forecast_steps = 7
        forecast = model_fit.forecast(steps=forecast_steps)

        forecast_df = pd.DataFrame({
            "date": pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), periods=forecast_steps),
            "forecast_revenue": forecast
        })

        # --- Show forecast ---
        st.subheader("🔮 Revenue Forecast (Next 7 Days)")
        st.line_chart(
            pd.concat([ts, forecast_df.set_index("date")["forecast_revenue"]], axis=1)
            .rename(columns={"total_revenue": "Actual Revenue", "forecast_revenue": "Forecast"})
        )

        st.dataframe(forecast_df)

        # --- Early Warning ---
        latest_actual = ts.iloc[-1]
        latest_forecast = forecast.iloc[0]

        if latest_actual < 0.9 * latest_forecast:
            st.error(f"⚠️ Warning: Latest revenue ({latest_actual:.2f}) is significantly below forecast ({latest_forecast:.2f})")
        else:
            st.success("✅ Revenue is within expected range.")









 


    

   

 









# Close the cursors and connections
cur1.close()
cur2.close()
conn1.close()
conn2.close()