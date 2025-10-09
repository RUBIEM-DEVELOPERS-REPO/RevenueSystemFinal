import psycopg2
import pandas as pd
import streamlit as st

import psycopg2
import pandas as pd
import streamlit as st

def get_transaction_data(limit=None):
    """
    Retrieve transaction data from the database
    """
    try:
        conn = get_db_connection()
        
        # Base query
        query = """
        SELECT 
            t.transaction_id,
            t.transaction_date,
            t.amount,
            t.description,
            t.status,
            t.customer_id,
            t.transaction_type_id,
            tt.type_name,
            tt.category_id,
            c.category_name
        FROM transactions t
        LEFT JOIN transaction_types tt ON t.transaction_type_id = tt.transaction_type_id
        LEFT JOIN categories c ON tt.category_id = c.category_id
        ORDER BY t.transaction_date DESC
        """
        
        # Execute with or without limit
        if limit is not None:
            query += " LIMIT %s"
            transactions_df = pd.read_sql(query, conn, params=(limit,))
        else:
            transactions_df = pd.read_sql(query, conn)
            
        conn.close()
        return transactions_df
        
    except Exception as e:
        print(f"Error fetching transaction data: {e}")
        return pd.DataFrame()

def get_mapping_data():
    """Fetch mapping tables from Neon"""
    try:
        conn = psycopg2.connect(
            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_7AlUWE8wkigH",
            port=5432
        )
        
        # Fetch categories
        categories = pd.read_sql("SELECT * FROM transaction_categories", conn)
        subcategories = pd.read_sql("SELECT * FROM transaction_subcategories", conn)
        types = pd.read_sql("SELECT * FROM transaction_types", conn)
        
        conn.close()
        
        # Merge categories with types
        types = types.merge(categories, on="category_id", how="left")
        return categories, subcategories, types
        
    except Exception as e:
        st.error(f"Error fetching mapping data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def update_transaction_mapping(transaction_id, category_id, subcategory_id):
    """Update transaction mapping in Neon database"""
    try:
        conn = psycopg2.connect(
            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_7AlUWE8wkigH",
            port=5432
        )
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE transaction_types 
            SET category_id = %s, subcategory_id = %s
            WHERE transaction_type_id = (
                SELECT transaction_type_id FROM transactions WHERE id = %s
            )
        """, (category_id, subcategory_id, transaction_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error updating mapping: {e}")
        return False

# Database connection functions
def get_db_connections():
    # Your database connection parameters
    pass

def get_transaction_data():
    # Your transaction data loading logic
    pass

def get_charges_data():
    # Your charges data loading logic
    pass

def get_price_recommendations():
    # Your price recommendations loading logic
    pass
def get_transaction_data():
    """Fetch transaction data for monitoring"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        query = """
        SELECT id, transaction_type_id, amount, created_at, updated_at 
        FROM transactions 
        ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def get_charges_data():
    """Fetch charges data from core_banking_system"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="core_banking_system",
            user="bankuser",
            password="Test123",
            port=5433
        )
        query = """
        SELECT charge_id, currency_id, charge_amount, charge_range_min, 
               charge_range_max, charge_percentage, transaction_type_id 
        FROM charges
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading charges data: {e}")
        return pd.DataFrame()

def get_price_recommendations():
    """Fetch price recommendations from Neon"""
    try:
        conn = psycopg2.connect(**conn2_params)
        query = """
        SELECT transaction_type_id, recommended_min_fee, recommended_max_fee,
               recommended_flat_fee, recommended_percentage_fee
        FROM price_recommendations
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading price recommendations: {e}")
        return pd.DataFrame()


import psycopg2
import pandas as pd

# Add your database connection parameters
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

def get_transaction_data():
    """Fetch transactions from dummydb"""
    try:
        conn = psycopg2.connect(**conn1_params)
        query = "SELECT * FROM transactions ORDER BY id ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading transaction data: {e}")
        return pd.DataFrame()

def get_transaction_types():
    """Fetch transaction types from Neon"""
    try:
        conn = psycopg2.connect(**conn2_params)
        query = "SELECT * FROM transaction_types"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading transaction types: {e}")
        return pd.DataFrame()

def get_charges_data():
    """Fetch charges from core_banking_system"""
    try:
        conn = psycopg2.connect(**conn_charges_params)
        query = """
        SELECT transaction_type_id, charge_type, charge_range_min, charge_range_max, charge_amount, charge_percentage
        FROM charges
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading charges data: {e}")
        return pd.DataFrame()

def get_price_recommendations():
    """Fetch price recommendations from Neon"""
    try:
        conn = psycopg2.connect(**conn2_params)
        query = """
        SELECT transaction_type_id, recommended_min_fee, recommended_max_fee, recommended_flat_fee, recommended_percentage_fee
        FROM price_recommendations
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading price recommendations: {e}")
        return pd.DataFrame()

import psycopg2
import pandas as pd

def get_transaction_monitoring_data():
    """Fetch transaction data for monitoring"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        query = """
        SELECT id, transaction_type_id, amount, created_at, updated_at 
        FROM transactions 
        ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def get_alerts_data(limit=1000):
    """
    Retrieve alerts data from the database for monitoring
    """
    try:
        conn = get_db_connection()
        query = """
        SELECT 
            alert_id,
            transaction_id,
            alert_type,
            severity,
            description,
            created_date,
            status,
            rule_triggered
        FROM alerts 
        ORDER BY created_date DESC 
        LIMIT %s
        """
        alerts_df = pd.read_sql(query, conn, params=(limit,))
        conn.close()
        return alerts_df
    except Exception as e:
        print(f"Error fetching alerts data: {e}")
        return pd.DataFrame()

# Alternative if you don't have an alerts table yet, create a mock function:
def get_alerts_data(limit=1000):
    """
    Mock alerts data for demonstration
    """
    try:
        # Try to get real data first
        conn = get_db_connection()
        query = "SELECT * FROM alerts LIMIT %s"
        alerts_df = pd.read_sql(query, conn, params=(limit,))
        conn.close()
        return alerts_df
    except:
        # Return mock data if table doesn't exist
        import random
        from datetime import datetime, timedelta
        
        alert_types = ['high_amount', 'suspicious_pattern', 'duplicate_transaction', 'unusual_time']
        severities = ['low', 'medium', 'high', 'critical']
        statuses = ['pending', 'investigating', 'resolved', 'false_positive']
        
        mock_alerts = []
        for i in range(min(limit, 50)):  # Max 50 mock alerts
            mock_alerts.append({
                'alert_id': i + 1,
                'transaction_id': random.randint(1000, 5000),
                'alert_type': random.choice(alert_types),
                'severity': random.choice(severities),
                'description': f"Alert for {random.choice(alert_types).replace('_', ' ')}",
                'created_date': datetime.now() - timedelta(hours=random.randint(0, 72)),
                'status': random.choice(statuses),
                'rule_triggered': f"rule_{random.randint(1, 10)}"
            })
        
        return pd.DataFrame(mock_alerts)

def apply_transaction_type_filter(df, selected_types):
    """Filter transactions by selected transaction types"""
    if not selected_types or df.empty:
        return df
    return df[df['transaction_type_id'].isin(selected_types)]

def calculate_lifecycle_metrics(merged_df):
    """Calculate customer lifecycle metrics"""
    lifecycle_data = {}
    
    if merged_df.empty:
        lifecycle_data['total_customers'] = 0
        lifecycle_data['high_value_customers'] = 0
        lifecycle_data['avg_daily_transactions'] = 0
        lifecycle_data['revenue_trend'] = pd.Series()
        lifecycle_data['total_revenue'] = 0
        lifecycle_data['total_transactions'] = 0
        return lifecycle_data
    
    # Total revenue and transactions
    total_revenue = merged_df['amount'].sum() if 'amount' in merged_df.columns else 0
    total_transactions = len(merged_df)
    
    # Customer metrics
    if 'customer_id' in merged_df.columns:
        customer_metrics = merged_df.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count']
        })
        customer_metrics.columns = ['_'.join(col).strip() for col in customer_metrics.columns.values]

        lifecycle_data['total_customers'] = len(customer_metrics)
        lifecycle_data['high_value_customers'] = (customer_metrics['amount_sum'] > customer_metrics['amount_sum'].quantile(0.8)).sum()
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
