import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime
import random
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config at the very top
st.set_page_config(
    page_title="Revenue Assurance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TWO NEON DATABASE CONNECTIONS ---
# Database 1: Main database (transactions, charges, transaction_types)
NEON_DB_MAIN = {
    "host": "ep-frosty-dawn-ad0cnbjn-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_XCO6HPNfw7El",
    "port": 5432
}

# Database 2: Price recommendations database
NEON_DB_PRICE = {
    "host": "ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_7AlUWE8wkigH",
    "port": 5432
}

def get_neon_connection(db_config):
    """Create and return a connection to specified Neon database"""
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def load_charges_and_recommendations():
    """Load charges and price recommendations and perform calculations"""
    try:
        # Load charges from main database
        conn_main = get_neon_connection(NEON_DB_MAIN)
        if not conn_main:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        cur1 = conn_main.cursor()
        cur1.execute("""
            SELECT transaction_type_id, charge_type, charge_range_min, charge_range_max, charge_amount, charge_percentage
            FROM charges
        """)
        charges_data = cur1.fetchall()
        cur1.close()
        conn_main.close()

        # Load price recommendations from price database
        conn_price = get_neon_connection(NEON_DB_PRICE)
        if not conn_price:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        cur2 = conn_price.cursor()
        cur2.execute("""
            SELECT transaction_type_id, recommended_min_fee, recommended_max_fee, recommended_flat_fee, recommended_percentage_fee
            FROM price_recommendations
        """)
        recommended_prices_data = cur2.fetchall()
        cur2.close()
        conn_price.close()

        # Create DataFrames
        charges_df = pd.DataFrame(charges_data, columns=[
            "transaction_type_id", "charge_type", "charge_range_min", "charge_range_max", "charge_amount", "charge_percentage"
        ])
        
        recommended_prices_df = pd.DataFrame(recommended_prices_data, columns=[
            "transaction_type_id", "recommended_min_fee", "recommended_max_fee", "recommended_flat_fee", "recommended_percentage_fee"
        ])

        # Merge DataFrames based on transaction type
        merged_df = pd.merge(charges_df, recommended_prices_df, on="transaction_type_id", how='inner')

        # Remove duplicate records
        merged_df = merged_df.drop_duplicates()

        # Convert to numeric types to ensure proper calculations
        numeric_columns = [
            'charge_range_min', 'charge_range_max', 'charge_amount', 'charge_percentage',
            'recommended_min_fee', 'recommended_max_fee', 'recommended_flat_fee', 'recommended_percentage_fee'
        ]
        
        for col in numeric_columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0)

        # Calculate differences with proper validation
        merged_df['min_fee_diff'] = merged_df['charge_range_min'] - merged_df['recommended_min_fee']
        merged_df['max_fee_diff'] = merged_df['charge_range_max'] - merged_df['recommended_max_fee']
        merged_df['charge_amount_diff'] = merged_df['charge_amount'] - merged_df['recommended_flat_fee']
        merged_df['percentage_diff'] = merged_df['charge_percentage'] - merged_df['recommended_percentage_fee']

        # Calculate percentage differences
        merged_df['min_fee_percentage_diff'] = np.where(
            merged_df['recommended_min_fee'] != 0,
            (merged_df['min_fee_diff'] / merged_df['recommended_min_fee']) * 100,
            0
        )
        
        merged_df['max_fee_percentage_diff'] = np.where(
            merged_df['recommended_max_fee'] != 0,
            (merged_df['max_fee_diff'] / merged_df['recommended_max_fee']) * 100,
            0
        )

        # Create a comprehensive differences table
        differences_table = merged_df[[
            "transaction_type_id", "charge_type",
            "charge_range_min", "recommended_min_fee", "min_fee_diff", "min_fee_percentage_diff",
            "charge_range_max", "recommended_max_fee", "max_fee_diff", "max_fee_percentage_diff",
            "charge_amount", "recommended_flat_fee", "charge_amount_diff",
            "charge_percentage", "recommended_percentage_fee", "percentage_diff"
        ]]

        return charges_df, recommended_prices_df, differences_table

    except Exception as e:
        st.error(f"❌ Error loading charges and recommendations: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def detect_anomalies_iforest(differences_table):
    """Detect anomalies using Isolation Forest"""
    try:
        # Prepare features for anomaly detection
        features = differences_table[['charge_amount_diff', 'percentage_diff']].copy()
        
        # Handle infinite values and NaN
        features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Apply Isolation Forest
        iforest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_predictions = iforest.fit_predict(features_scaled)
        
        differences_table = differences_table.copy()
        differences_table['anomaly'] = anomaly_predictions
        anomalies = differences_table[differences_table['anomaly'] == -1]
        
        return differences_table, anomalies

    except Exception as e:
        st.error(f"❌ Isolation Forest failed: {e}")
        return differences_table, pd.DataFrame()

def detect_anomalies_zscore(differences_table):
    """Detect anomalies using Z-Score method"""
    try:
        # Prepare features
        features = differences_table[['charge_amount_diff', 'percentage_diff']].copy()
        
        # Convert to numeric and handle errors
        features['charge_amount_diff'] = pd.to_numeric(features['charge_amount_diff'], errors='coerce').fillna(0)
        features['percentage_diff'] = pd.to_numeric(features['percentage_diff'], errors='coerce').fillna(0)

        # Calculate Z-scores with proper NaN handling
        z_scores = np.abs(stats.zscore(features, nan_policy='omit'))
        z_scores = np.nan_to_num(z_scores, nan=0)
        
        # Detect anomalies (Z-score > 3)
        anomaly_mask = (z_scores > 3).any(axis=1)
        anomalies = differences_table[anomaly_mask]
        
        differences_table = differences_table.copy()
        differences_table['anomaly'] = anomaly_mask.astype(str)
        
        return differences_table, anomalies

    except Exception as e:
        st.error(f"❌ Z-Score detection failed: {e}")
        return differences_table, pd.DataFrame()

def detect_anomalies_autoencoder(differences_table):
    """Detect anomalies using Autoencoder (simplified PCA approach)"""
    try:
        # Prepare features
        features = differences_table[['charge_amount_diff', 'percentage_diff']].copy()
        
        # Handle infinite values and NaN
        features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Use PCA for dimensionality reduction (simplified autoencoder)
        pca = PCA(n_components=1)
        transformed = pca.fit_transform(features_scaled)
        reconstructed = pca.inverse_transform(transformed)
        
        # Calculate reconstruction error
        reconstruction_error = np.mean((features_scaled - reconstructed) ** 2, axis=1)
        
        # Detect anomalies based on reconstruction error
        threshold = np.percentile(reconstruction_error, 95)  # Top 5% as anomalies
        anomaly_mask = reconstruction_error > threshold
        
        anomalies = differences_table[anomaly_mask]
        differences_table = differences_table.copy()
        differences_table['anomaly'] = anomaly_mask.astype(int)
        
        return differences_table, anomalies

    except Exception as e:
        st.error(f"❌ Autoencoder detection failed: {e}")
        return differences_table, pd.DataFrame()

def detect_rule_based_anomalies(differences_table):
    """Detect anomalies based on business rules"""
    try:
        anomalies = []
        
        for idx, row in differences_table.iterrows():
            reasons = []
            severity = "low"
            
            # Rule 1: Significant min fee difference (> 20%)
            if abs(row['min_fee_percentage_diff']) > 20:
                reasons.append(f"Min fee difference: {row['min_fee_percentage_diff']:.1f}%")
                severity = "high" if abs(row['min_fee_percentage_diff']) > 50 else "medium"
            
            # Rule 2: Significant max fee difference (> 20%)
            if abs(row['max_fee_percentage_diff']) > 20:
                reasons.append(f"Max fee difference: {row['max_fee_percentage_diff']:.1f}%")
                severity = "high" if abs(row['max_fee_percentage_diff']) > 50 else "medium"
            
            # Rule 3: Large absolute charge amount difference
            if abs(row['charge_amount_diff']) > 100:
                reasons.append(f"Charge amount difference: ${row['charge_amount_diff']:.2f}")
                severity = "high" if abs(row['charge_amount_diff']) > 500 else "medium"
            
            # Rule 4: Large percentage difference
            if abs(row['percentage_diff']) > 10:
                reasons.append(f"Percentage difference: {row['percentage_diff']:.1f}%")
                severity = "high" if abs(row['percentage_diff']) > 25 else "medium"
            
            if reasons:
                anomalies.append({
                    'transaction_type_id': row['transaction_type_id'],
                    'charge_type': row['charge_type'],
                    'reasons': reasons,
                    'severity': severity,
                    'min_fee_percentage_diff': row['min_fee_percentage_diff'],
                    'max_fee_percentage_diff': row['max_fee_percentage_diff'],
                    'charge_amount_diff': row['charge_amount_diff'],
                    'percentage_diff': row['percentage_diff']
                })
        
        return pd.DataFrame(anomalies) if anomalies else pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ Rule-based detection failed: {e}")
        return pd.DataFrame()

def main():
    # Simple CSS for spaced tabs only
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        margin: 0 8px;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .quick-action-btn {
        width: 100%;
        margin: 5px 0;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        background: #e3f2fd;
        border-color: #2196f3;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== SIDEBAR =====
    with st.sidebar:
        st.title(" Quick Access")
        st.markdown("---")
        
        # Database Status
        st.subheader("Database Status")
        col1, col2 = st.columns(2)
        with col1:
            main_conn = get_neon_connection(NEON_DB_MAIN)
            if main_conn:
                st.success("Main DB ✅")
                main_conn.close()
            else:
                st.error("Main DB ❌")
        with col2:
            price_conn = get_neon_connection(NEON_DB_PRICE)
            if price_conn:
                st.success("Price DB ✅")
                price_conn.close()
            else:
                st.error("Price DB ❌")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("Quick Actions")
        
        if st.button("🔄 Refresh All Data", use_container_width=True):
            if 'data_loaded' in st.session_state:
                st.session_state.data_loaded = False
            st.rerun()
        
        if st.button("Run Full Analysis", use_container_width=True):
            st.session_state.run_full_analysis = True
            st.rerun()
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.session_state.generate_report = True
            st.rerun()
        
        st.markdown("---")
        
        
        
        # System Information
        st.subheader("ℹ️ System Info")
        st.write(f"**Last Updated:**")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if 'differences_table' in st.session_state:
            data = st.session_state.differences_table
            if not data.empty:
                st.write(f"**Records:** {len(data):,}")
                st.write(f"**Transaction Types:** {data['transaction_type_id'].nunique()}")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh data", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (minutes)", 1, 60, 5)
        
        st.markdown("---")
        
        # Help & Support
        st.subheader("❓ Help")
        if st.button("View Documentation", use_container_width=True):
            st.info("Documentation would open here")
        if st.button("Contact Support", use_container_width=True):
            st.info("Support contact form would appear here")

    # ===== MAIN CONTENT =====
    # Main dashboard header
    st.title("Revenue Assurance Dashboard")
    st.markdown("### AI-Powered Fee Validation and Anomaly Detection Platform")
    
    # Load data once at the beginning
    if 'data_loaded' not in st.session_state:
        with st.spinner("🔄 Loading data from databases..."):
            charges_df, recommended_prices_df, differences_table = load_charges_and_recommendations()
            st.session_state.charges_df = charges_df
            st.session_state.recommended_prices_df = recommended_prices_df
            st.session_state.differences_table = differences_table
            st.session_state.data_loaded = True
    
    # Access data from session state
    charges_df = st.session_state.charges_df
    recommended_prices_df = st.session_state.recommended_prices_df
    differences_table = st.session_state.differences_table
    
    # Create tabs with spaced titles
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "   📊 Dashboard Overview   ", 
        "   🔍 Anomaly Detection   ", 
        "   📈 Data Analysis   ", 
        "   📊 Visualizations   ", 
        "   💾 Export Data   "
    ])
    
    with tab1:
        st.header("📊 Dashboard Overview")
        
        if not differences_table.empty:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", len(differences_table))
            
            with col2:
                avg_charge_diff = differences_table['charge_amount_diff'].mean()
                st.metric("Avg Charge Diff", f"${avg_charge_diff:.2f}")
            
            with col3:
                avg_percentage_diff = differences_table['percentage_diff'].mean()
                st.metric("Avg % Diff", f"{avg_percentage_diff:.1f}%")
            
            with col4:
                high_diff_count = len(differences_table[differences_table['min_fee_percentage_diff'].abs() > 20])
                st.metric("High Variance Records", high_diff_count)
            

            # Recent data preview
            st.subheader("📋 Recent Data Preview")
            st.dataframe(differences_table.head(10), use_container_width=True)
            
        else:
            st.warning("⚠️ No data available. Please check your database connections.")
            if st.button("🔄 Retry Loading Data", key="retry_main"):
                st.session_state.data_loaded = False
                st.rerun()

        # Quick stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Data Summary")
            st.info(f"**Charges Loaded:** {len(charges_df)}")
            st.info(f"**Recommendations Loaded:** {len(recommended_prices_df)}")
            st.info(f"**Merged Records:** {len(differences_table)}")
            st.info(f"**Transaction Types:** {differences_table['transaction_type_id'].nunique()}")
            
            
            
            
    
    with tab2:
        st.header("🔍 Anomaly Detection")
        
        if differences_table.empty:
            st.warning("No data available for analysis")
        else:
            # Check if full analysis was triggered from sidebar
            if st.session_state.get('run_full_analysis', False):
                st.success("🚀 Running full analysis with all algorithms...")
                # Reset the flag
                st.session_state.run_full_analysis = False
                # Set all algorithms to run
                use_iforest = True
                use_zscore = True
                use_autoencoder = True
                use_rule_based = True
            else:
                # Algorithm selection
                st.subheader("Select Detection Algorithms")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    use_iforest = st.checkbox("🌲 Isolation Forest", value=True)
                with col2:
                    use_zscore = st.checkbox("📊 Z-Score", value=True)
                with col3:
                    use_autoencoder = st.checkbox("🧠 Autoencoder", value=False)
                with col4:
                    use_rule_based = st.checkbox("📏 Rule-Based", value=True)
            
            if st.button("🚀 Run Anomaly Detection", type="primary", use_container_width=True) or st.session_state.get('run_full_analysis', False):
                all_anomalies = {}
                
                # Run selected algorithms
                if use_iforest:
                    with st.spinner("Running Isolation Forest..."):
                        merged_iforest, anomalies_iforest = detect_anomalies_iforest(differences_table.copy())
                        all_anomalies['Isolation Forest'] = anomalies_iforest
                
                if use_zscore:
                    with st.spinner("Running Z-Score Detection..."):
                        merged_zscore, anomalies_zscore = detect_anomalies_zscore(differences_table.copy())
                        all_anomalies['Z-Score'] = anomalies_zscore
                
                if use_autoencoder:
                    with st.spinner("Running Autoencoder..."):
                        merged_autoencoder, anomalies_autoencoder = detect_anomalies_autoencoder(differences_table.copy())
                        all_anomalies['Autoencoder'] = anomalies_autoencoder
                
                if use_rule_based:
                    with st.spinner("Running Rule-Based Detection..."):
                        anomalies_rule_based = detect_rule_based_anomalies(differences_table)
                        all_anomalies['Rule-Based'] = anomalies_rule_based
                
                # Display summary
                st.subheader("📊 Detection Summary")
                summary_data = []
                for algo_name, anomalies in all_anomalies.items():
                    if not anomalies.empty:
                        summary_data.append({
                            'Algorithm': algo_name,
                            'Anomalies Found': len(anomalies),
                            'Detection Rate': f"{(len(anomalies) / len(differences_table) * 100):.1f}%"
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # Show detailed rule-based anomalies
                    if 'Rule-Based' in all_anomalies and not all_anomalies['Rule-Based'].empty:
                        st.subheader("📋 Rule-Based Anomaly Details")
                        st.dataframe(all_anomalies['Rule-Based'], use_container_width=True)
                        
                        # Visualize rule-based anomalies - FIXED: Use absolute values for size
                        st.subheader("📈 Rule-Based Anomaly Visualization")
                        anomalies_df = all_anomalies['Rule-Based'].copy()
                        # Use absolute values for size to avoid negative values
                        anomalies_df['size_value'] = np.abs(anomalies_df['charge_amount_diff'])
                        
                        fig = px.scatter(anomalies_df,
                                       x='charge_amount_diff', 
                                       y='percentage_diff',
                                       color='severity',
                                       size='size_value',  # Use absolute values
                                       hover_data=['transaction_type_id', 'charge_type'],
                                       title='Rule-Based Anomalies by Severity',
                                       color_discrete_map={
                                           'high': '#ff4444',
                                           'medium': '#ffaa00', 
                                           'low': '#44ff44'
                                       })
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("✅ No anomalies detected by any algorithm")
    
    with tab3:
        st.header("📈 Data Analysis")
        
        if differences_table.empty:
            st.warning("No data available for analysis")
        else:
            st.subheader("Differences Analysis")
            st.dataframe(differences_table, use_container_width=True, height=400)
            
            # Statistical summary
            st.subheader("Statistical Summary")
            st.dataframe(differences_table.describe(), use_container_width=True)
            
            # Correlation analysis
            st.subheader("Correlation Analysis")
            numeric_columns = differences_table.select_dtypes(include=[np.number]).columns
            correlation_matrix = differences_table[numeric_columns].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
            plt.title('Correlation Matrix')
            st.pyplot(fig)
            
            # Top differences
            st.subheader("🔝 Top Differences")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Largest Charge Amount Differences:**")
                top_charge_diff = differences_table.nlargest(5, 'charge_amount_diff')[['transaction_type_id', 'charge_amount_diff']]
                st.dataframe(top_charge_diff, use_container_width=True)
            
            with col2:
                st.write("**Largest Percentage Differences:**")
                top_percentage_diff = differences_table.nlargest(5, 'percentage_diff')[['transaction_type_id', 'percentage_diff']]
                st.dataframe(top_percentage_diff, use_container_width=True)
    
    with tab4:
        st.header("📊 Visualizations")
        
        if differences_table.empty:
            st.warning("No data available for visualization")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Charge Amount Differences")
                fig1 = px.histogram(differences_table, x='charge_amount_diff', 
                                   title='Distribution of Charge Amount Differences',
                                   nbins=50)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("Percentage Differences")
                fig2 = px.histogram(differences_table, x='percentage_diff',
                                   title='Distribution of Percentage Differences',
                                   nbins=50)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Scatter plot
            st.subheader("Charge Amount vs Percentage Differences")
            fig3 = px.scatter(differences_table, x='charge_amount_diff', y='percentage_diff',
                             color='transaction_type_id',
                             title='Charge Amount Differences vs Percentage Differences',
                             hover_data=['charge_type'])
            st.plotly_chart(fig3, use_container_width=True)
            
            # Box plots
            st.subheader("Distribution by Transaction Type")
            col1, col2 = st.columns(2)
            
            with col1:
                fig4 = px.box(differences_table, x='transaction_type_id', y='charge_amount_diff',
                             title='Charge Amount Differences by Transaction Type')
                st.plotly_chart(fig4, use_container_width=True)
            
            with col2:
                fig5 = px.box(differences_table, x='transaction_type_id', y='percentage_diff',
                             title='Percentage Differences by Transaction Type')
                st.plotly_chart(fig5, use_container_width=True)
    
    with tab5:
        st.header("💾 Export Data")
        
        if differences_table.empty:
            st.warning("No data available for export")
        else:
            # Check if report generation was triggered from sidebar
            if st.session_state.get('generate_report', False):
                st.success("📄 Generating comprehensive report...")
                # Reset the flag
                st.session_state.generate_report = False
            
            st.subheader("Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export differences table
                csv_diff = differences_table.to_csv(index=False)
                st.download_button(
                    label="📥 Download Differences CSV",
                    data=csv_diff,
                    file_name=f"fee_differences_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Export charges data
                if not charges_df.empty:
                    csv_charges = charges_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Charges CSV",
                        data=csv_charges,
                        file_name=f"charges_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                # Export recommendations data
                if not recommended_prices_df.empty:
                    csv_recs = recommended_prices_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Recommendations CSV",
                        data=csv_recs,
                        file_name=f"price_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Export summary report
            st.subheader("Summary Report")
            if st.button("📄 Generate Summary Report", use_container_width=True) or st.session_state.get('generate_report', False):
                summary_report = f"""
Revenue Assurance Dashboard - Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATA OVERVIEW:
- Total Charges Records: {len(charges_df)}
- Total Recommendations: {len(recommended_prices_df)}
- Merged Analysis Records: {len(differences_table)}
- Unique Transaction Types: {differences_table['transaction_type_id'].nunique()}

KEY METRICS:
- Average Charge Amount Difference: ${differences_table['charge_amount_diff'].mean():.2f}
- Average Percentage Difference: {differences_table['percentage_diff'].mean():.1f}%
- Maximum Charge Difference: ${differences_table['charge_amount_diff'].max():.2f}
- Minimum Charge Difference: ${differences_table['charge_amount_diff'].min():.2f}

STATISTICAL SUMMARY:
{differences_table[['charge_amount_diff', 'percentage_diff']].describe().to_string()}

DATABASE CONNECTIONS:
- Main Database: {'✅ Connected' if get_neon_connection(NEON_DB_MAIN) else '❌ Failed'}
- Price Database: {'✅ Connected' if get_neon_connection(NEON_DB_PRICE) else '❌ Failed'}
                """
                
                st.download_button(
                    label="📥 Download Summary Report",
                    data=summary_report,
                    file_name=f"revenue_assurance_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()