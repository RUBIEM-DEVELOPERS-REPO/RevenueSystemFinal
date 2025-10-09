import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class TransactionMonitor:
    """Monitor and analyze transactions for anomalies"""
    
    def __init__(self, contamination=0.02):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
    
    def process_transactions(self, df):
        """Process raw transaction data and engineer features"""
        processed_df = df.copy()
        
        # Convert amount to float
        if 'amount' in processed_df.columns:
            processed_df['amount'] = processed_df['amount'].astype(float)
        
        # Convert timestamps
        if 'created_at' in processed_df.columns:
            processed_df['created_at'] = pd.to_datetime(processed_df['created_at'])
        if 'updated_at' in processed_df.columns:
            processed_df['updated_at'] = pd.to_datetime(processed_df['updated_at'])
        
        # Feature engineering
        processed_df = self._engineer_features(processed_df)
        
        return processed_df
    
    def _engineer_features(self, df):
        """Engineer features for anomaly detection"""
        # Time-based features
        if 'created_at' in df.columns:
            df['hour_of_day'] = df['created_at'].dt.hour
            df['day_of_week'] = df['created_at'].dt.dayofweek
            df['day_of_month'] = df['created_at'].dt.day
        
        # Processing time
        if 'created_at' in df.columns and 'updated_at' in df.columns:
            df['processing_time'] = (df['updated_at'] - df['created_at']).dt.total_seconds()
        else:
            df['processing_time'] = 0
        
        # Transaction type dummies
        if 'transaction_type_id' in df.columns:
            df = pd.get_dummies(df, columns=['transaction_type_id'], prefix='type')
        
        return df
    
    def detect_anomalies(self, df):
        """Detect anomalies using Isolation Forest"""
        # Select features for anomaly detection
        features = self._select_features(df)
        
        if len(features) == 0:
            df['anomaly'] = 'Normal'
            return df
        
        X = df[features].fillna(0)
        
        # Fit model and predict
        df['anomaly_score'] = self.model.fit_predict(X)
        df['anomaly'] = df['anomaly_score'].map({1: 'Normal', -1: 'Anomaly'})
        
        return df
    
    def _select_features(self, df):
        """Select features for anomaly detection"""
        base_features = ['amount', 'hour_of_day', 'day_of_week', 'processing_time']
        available_base = [f for f in base_features if f in df.columns]
        
        type_features = [col for col in df.columns if col.startswith('type_')]
        
        return available_base + type_features

class AlertSystem:
    """Alert system for notifying about anomalies"""
    
    def __init__(self, threshold=5):
        self.threshold = threshold  # Number of anomalies to trigger alert
    
    def check_alerts(self, df):
        """Check if alerts need to be triggered based on anomalies"""
        if 'anomaly' not in df.columns:
            return False, 0
        
        anomaly_count = (df['anomaly'] == 'Anomaly').sum()
        
        if anomaly_count >= self.threshold:
            return True, anomaly_count
        else:
            return False, anomaly_count     

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class TransactionMonitor:
    """Monitor and analyze transactions for anomalies"""
    
    def __init__(self, contamination=0.02):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
    
    def process_transactions(self, df):
        """Process raw transaction data and engineer features"""
        processed_df = df.copy()
        
        # Convert amount to float
        if 'amount' in processed_df.columns:
            processed_df['amount'] = processed_df['amount'].astype(float)
        
        # Convert timestamps
        if 'created_at' in processed_df.columns:
            processed_df['created_at'] = pd.to_datetime(processed_df['created_at'])
        if 'updated_at' in processed_df.columns:
            processed_df['updated_at'] = pd.to_datetime(processed_df['updated_at'])
        
        # Feature engineering
        processed_df = self._engineer_features(processed_df)
        
        return processed_df
    
    def _engineer_features(self, df):
        """Engineer features for anomaly detection"""
        # Time-based features
        if 'created_at' in df.columns:
            df['hour_of_day'] = df['created_at'].dt.hour
            df['day_of_week'] = df['created_at'].dt.dayofweek
            df['day_of_month'] = df['created_at'].dt.day
        
        # Processing time
        if 'created_at' in df.columns and 'updated_at' in df.columns:
            df['processing_time'] = (df['updated_at'] - df['created_at']).dt.total_seconds()
        else:
            df['processing_time'] = 0
        
        # Transaction type dummies
        if 'transaction_type_id' in df.columns:
            df = pd.get_dummies(df, columns=['transaction_type_id'], prefix='type')
        
        return df
    
    def detect_anomalies(self, df):
        """Detect anomalies using Isolation Forest"""
        # Select features for anomaly detection
        features = self._select_features(df)
        
        if len(features) == 0:
            df['anomaly'] = 'Normal'
            return df
        
        X = df[features].fillna(0)
        
        # Fit model and predict
        df['anomaly_score'] = self.model.fit_predict(X)
        df['anomaly'] = df['anomaly_score'].map({1: 'Normal', -1: 'Anomaly'})
        
        return df
    
    def _select_features(self, df):
        """Select features for anomaly detection"""
        base_features = ['amount', 'hour_of_day', 'day_of_week', 'processing_time']
        available_base = [f for f in base_features if f in df.columns]
        
        type_features = [col for col in df.columns if col.startswith('type_')]
        
        return available_base + type_features