import streamlit as st
import pandas as pd

def show_anomaly_analysis(transactions_df, alert_system):
    """Display anomaly analysis and recommendations"""
    
    # AI-Powered Recommendations
    st.subheader("🤖 AI-Powered Recommendations")
    show_ai_recommendations(transactions_df)
    
    # Suspicious Transactions Table
    st.subheader("⚠️ Suspicious Transactions for Review")
    show_suspicious_transactions(transactions_df)
    
    # Alert System
    st.subheader("🚨 Alert System")
    setup_alerts(transactions_df, alert_system)

def show_ai_recommendations(df):
    """Generate and display AI-powered recommendations"""
    recommendations = []
    
    # Rule 1: Night anomalies
    if 'hour_of_day' in df.columns and 'anomaly' in df.columns:
        night_anomalies = df[(df['hour_of_day'] >= 0) & (df['hour_of_day'] <= 5) & (df['anomaly'] == 'Anomaly')]
        if len(night_anomalies) > 0:
            recommendations.append({
                "type": "warning",
                "message": "🌙 High anomaly activity detected during **night hours (00:00–05:00)** → Recommend stricter monitoring rules at night.",
                "count": len(night_anomalies)
            })
    
    # Rule 2: Transaction type anomalies
    if any(col.startswith('type_') for col in df.columns) and 'anomaly' in df.columns:
        anomaly_counts = df[df['anomaly']=='Anomaly'].filter(like='type_').sum()
        if not anomaly_counts.empty:
            top_anomaly_types = anomaly_counts.sort_values(ascending=False).head(1)
            if not top_anomaly_types.empty and top_anomaly_types.iloc[0] > 0:
                recommendations.append({
                    "type": "warning",
                    "message": f"📌 Anomalies are concentrated in **{top_anomaly_types.index[0]}** → Review related pricing rules or suspicious agent activity.",
                    "count": int(top_anomaly_types.iloc[0])
                })
    
    # Rule 3: High-value anomalies
    if 'amount' in df.columns and 'anomaly' in df.columns:
        high_value_threshold = df['amount'].quantile(0.95) if len(df) > 0 else 0
        high_value_anomalies = df[(df['amount'] > high_value_threshold) & (df['anomaly'] == 'Anomaly')]
        if len(high_value_anomalies) > 0:
            recommendations.append({
                "type": "error",
                "message": "💰 High-value anomaly transactions detected → Escalate to compliance immediately.",
                "count": len(high_value_anomalies)
            })
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            if rec["type"] == "error":
                st.error(f"{rec['message']} (Count: {rec['count']})")
            elif rec["type"] == "warning":
                st.warning(f"{rec['message']} (Count: {rec['count']})")
    else:
        st.success("✅ No critical recommendations at the moment. Transaction anomalies are within expected patterns.")

def show_suspicious_transactions(df):
    """Display table of suspicious transactions"""
    if 'anomaly' in df.columns:
        suspicious = df[df['anomaly'] == 'Anomaly']
        if not suspicious.empty:
            # Select relevant columns for display
            display_cols = ['id', 'amount', 'created_at']
            if 'processing_time' in suspicious.columns:
                display_cols.append('processing_time')
            if 'hour_of_day' in suspicious.columns:
                display_cols.append('hour_of_day')
            
            display_cols = [col for col in display_cols if col in suspicious.columns]
            
            st.dataframe(
                suspicious[display_cols],
                use_container_width=True
            )
            
            # Export option
            if st.button("📥 Export Suspicious Transactions"):
                csv = suspicious[display_cols].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="suspicious_transactions.csv",
                    mime="text/csv"
                )
        else:
            st.success("No suspicious transactions detected ✅")

def setup_alerts(df, alert_system):
    """Setup and manage alert system"""
    if 'anomaly' in df.columns and len(df) > 0:
        total_txn = len(df)
        anomaly_count = len(df[df['anomaly'] == 'Anomaly'])
        anomaly_rate = (anomaly_count / total_txn * 100) if total_txn > 0 else 0
        
        alert_threshold = st.slider("Set anomaly alert threshold (%)", 1, 50, 5)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Anomaly Rate", f"{anomaly_rate:.2f}%")
        
        with col2:
            st.metric("Alert Threshold", f"{alert_threshold}%")
        
        if anomaly_rate > alert_threshold:
            st.error(f"🚨 ALERT: {anomaly_rate:.2f}% anomalies detected!")
            
            # Send alerts
            if st.button("Send Alerts Now"):
                send_alerts(anomaly_rate, alert_system)
        else:
            st.info(f"✅ Anomaly rate is within safe limits ({anomaly_rate:.2f}%)")

def send_alerts(anomaly_rate, alert_system):
    """Send alerts via various channels"""
    with st.spinner("Sending alerts..."):
        try:
            # Send Slack alert
            alert_system.send_slack_alert(f"🚨 {anomaly_rate:.2f}% anomalies detected in transactions!")
            
            # Send email alert
            alert_system.send_email_alert(
                "🚨 Anomaly Alert in Transactions",
                f"{anomaly_rate:.2f}% anomalies detected. Check dashboard immediately."
            )
            
            st.success("✅ Alerts sent successfully!")
            
        except Exception as e:
            st.error(f"Failed to send alerts: {str(e)}")

import streamlit as st
import pandas as pd
from utils.database import get_transaction_data
from utils.alerts import AlertSystem

import streamlit as st
import pandas as pd
import numpy as np
import requests
import smtplib
from email.mime.text import MIMEText

def show_anomaly_analysis(transactions_df, alert_system):
    """Display anomaly analysis and recommendations"""
    
    # AI-Powered Recommendations
    st.subheader("🤖 AI-Powered Recommendations")
    show_ai_recommendations(transactions_df)
    
    # Suspicious Transactions Table
    st.subheader("⚠️ Suspicious Transactions for Review")
    show_suspicious_transactions(transactions_df)
    
    # Alert System
    st.subheader("🚨 Alert System")
    setup_alerts(transactions_df, alert_system)

def show_ai_recommendations(df):
    """Generate and display AI-powered recommendations"""
    recommendations = []
    
    # Rule 1: Night anomalies
    if 'hour_of_day' in df.columns and 'anomaly' in df.columns:
        night_anomalies = df[(df['hour_of_day'] >= 0) & (df['hour_of_day'] <= 5) & (df['anomaly'] == 'Anomaly')]
        if len(night_anomalies) > 0:
            recommendations.append({
                "type": "warning",
                "message": "🌙 High anomaly activity detected during **night hours (00:00–05:00)** → Recommend stricter monitoring rules at night.",
                "count": len(night_anomalies)
            })
    
    # Rule 2: Transaction type anomalies
    if any(col.startswith('type_') for col in df.columns) and 'anomaly' in df.columns:
        anomaly_counts = df[df['anomaly']=='Anomaly'].filter(like='type_').sum()
        if not anomaly_counts.empty:
            top_anomaly_types = anomaly_counts.sort_values(ascending=False).head(1)
            if not top_anomaly_types.empty and top_anomaly_types.iloc[0] > 0:
                recommendations.append({
                    "type": "warning",
                    "message": f"📌 Anomalies are concentrated in **{top_anomaly_types.index[0]}** → Review related pricing rules or suspicious agent activity.",
                    "count": int(top_anomaly_types.iloc[0])
                })
    
    # Rule 3: High-value anomalies
    if 'amount' in df.columns and 'anomaly' in df.columns:
        high_value_threshold = df['amount'].quantile(0.95) if len(df) > 0 else 0
        high_value_anomalies = df[(df['amount'] > high_value_threshold) & (df['anomaly'] == 'Anomaly')]
        if len(high_value_anomalies) > 0:
            recommendations.append({
                "type": "error",
                "message": "💰 High-value anomaly transactions detected → Escalate to compliance immediately.",
                "count": len(high_value_anomalies)
            })
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            if rec["type"] == "error":
                st.error(f"{rec['message']} (Count: {rec['count']})")
            elif rec["type"] == "warning":
                st.warning(f"{rec['message']} (Count: {rec['count']})")
    else:
        st.success("✅ No critical recommendations at the moment. Transaction anomalies are within expected patterns.")

def show_suspicious_transactions(df):
    """Display table of suspicious transactions"""
    if 'anomaly' in df.columns:
        suspicious = df[df['anomaly'] == 'Anomaly']
        if not suspicious.empty:
            # Select relevant columns for display
            display_cols = ['id', 'amount', 'created_at']
            if 'processing_time' in suspicious.columns:
                display_cols.append('processing_time')
            if 'hour_of_day' in suspicious.columns:
                display_cols.append('hour_of_day')
            
            display_cols = [col for col in display_cols if col in suspicious.columns]
            
            st.dataframe(
                suspicious[display_cols],
                use_container_width=True
            )
            
            # Export option
            if st.button("📥 Export Suspicious Transactions"):
                csv = suspicious[display_cols].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="suspicious_transactions.csv",
                    mime="text/csv"
                )
        else:
            st.success("No suspicious transactions detected ✅")

def setup_alerts(df, alert_system):
    """Setup and manage alert system"""
    if 'anomaly' in df.columns and len(df) > 0:
        total_txn = len(df)
        anomaly_count = len(df[df['anomaly'] == 'Anomaly'])
        anomaly_rate = (anomaly_count / total_txn * 100) if total_txn > 0 else 0
        
        alert_threshold = st.slider("Set anomaly alert threshold (%)", 1, 50, 5)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Current Anomaly Rate", f"{anomaly_rate:.2f}%")
        
        with col2:
            st.metric("Alert Threshold", f"{alert_threshold}%")
        
        if anomaly_rate > alert_threshold:
            st.error(f"🚨 ALERT: {anomaly_rate:.2f}% anomalies detected!")
            
            # Send alerts
            if st.button("Send Alerts Now"):
                send_alerts(anomaly_rate, alert_system)
        else:
            st.info(f"✅ Anomaly rate is within safe limits ({anomaly_rate:.2f}%)")

def send_alerts(anomaly_rate, alert_system):
    """Send alerts via various channels"""
    with st.spinner("Sending alerts..."):
        try:
            # Send Slack alert
            alert_system.send_slack_alert(f"🚨 {anomaly_rate:.2f}% anomalies detected in transactions!")
            
            # Send email alert
            alert_system.send_email_alert(
                "🚨 Anomaly Alert in Transactions",
                f"{anomaly_rate:.2f}% anomalies detected. Check dashboard immediately."
            )
            
            st.success("✅ Alerts sent successfully!")
            
        except Exception as e:
            st.error(f"Failed to send alerts: {str(e)}")