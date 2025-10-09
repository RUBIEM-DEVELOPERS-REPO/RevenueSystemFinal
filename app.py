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

# Set page config at the very top
st.set_page_config(
    page_title="Revenue Assurance Dashboard",
   
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
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
    
    .algorithm-card {
        background: #fff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        min-height: 160px;
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
    
    .download-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 2rem;
        border: 2px dashed #dee2e6;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # DASHBOARD HEADER
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

    # Define functions
    def generate_sample_data():
        """Generate sample revenue data for demonstration"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        n_days = len(dates)
        
        random.seed(42)
        
        revenue = []
        current = 100000
        
        for i in range(n_days):
            growth = random.uniform(80, 120)
            current += growth
            seasonal = 3000 * math.sin(2 * math.pi * i / 365)
            current += seasonal
            revenue.append(current)
        
        anomaly = [False] * n_days
        anomaly_indices = random.sample(range(n_days), 12)
        
        for idx in anomaly_indices:
            revenue[idx] = revenue[idx] * random.uniform(0.3, 0.6)
            anomaly[idx] = True
        
        return pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'anomaly': anomaly
        })

    def generate_analysis_data():
        """Generate sample transaction data for anomaly detection"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'transaction_id': range(1, n_samples + 1),
            'charge_amount': np.random.normal(100, 30, n_samples),
            'recommended_min_fee': np.random.normal(80, 20, n_samples),
            'recommended_max_fee': np.random.normal(120, 25, n_samples),
            'recommended_percentage_fee': np.random.normal(5, 2, n_samples),
            'recommended_flat_fee': np.random.normal(10, 5, n_samples),
            'transaction_type_id': np.random.choice(['TYPE_A', 'TYPE_B', 'TYPE_C', 'TYPE_D'], n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create some anomalies
        anomaly_indices = np.random.choice(n_samples, 50, replace=False)
        df.loc[anomaly_indices, 'charge_amount'] *= np.random.uniform(1.5, 3.0, 50)
        
        # Calculate differences
        df['charge_amount_diff'] = df['charge_amount'] - df[['recommended_min_fee', 'recommended_max_fee']].mean(axis=1)
        df['percentage_diff'] = (df['charge_amount_diff'] / df[['recommended_min_fee', 'recommended_max_fee']].mean(axis=1)) * 100
        
        return df

    def detect_rule_based_anomalies(df):
        """Detect anomalies based on business rules"""
        anomalies = []
        
        for idx, row in df.iterrows():
            reasons = []
            severity = "low"
            
            # Rule 1: Charge outside recommended range
            if (row['charge_amount'] < row['recommended_min_fee'] or 
                row['charge_amount'] > row['recommended_max_fee']):
                reasons.append(f"Charge ${row['charge_amount']:.2f} outside range [${row['recommended_min_fee']:.2f}, ${row['recommended_max_fee']:.2f}]")
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

    # Initialize session state
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False
    if 'view_raw_data' not in st.session_state:
        st.session_state.view_raw_data = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    # Load sample data
    df = generate_sample_data()
    merged_df = generate_analysis_data()

    

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

    # Revenue Trend Chart
    st.markdown("## 📊 Revenue Analytics")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    fig_revenue = go.Figure()
    normal_data = df[~df['anomaly']]
    fig_revenue.add_trace(go.Scatter(
        x=normal_data['date'],
        y=normal_data['revenue'],
        mode='lines',
        name='Normal Revenue',
        line=dict(color='#667eea', width=3)
    ))

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

    # ANOMALY DETECTION SECTION
    st.markdown("## 🎯 Advanced Anomaly Detection")
    
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
    if st.session_state.run_analysis or st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
        with st.spinner("🤖 Running multi-algorithm anomaly detection..."):
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

                # Store results in session state
                st.session_state.analysis_results = {
                    'algorithm_results': algorithm_results,
                    'analysis_df': analysis_df,
                    'valid_results': {k: v for k, v in algorithm_results.items() if v['count'] > 0} if algorithm_results else {}
                }

                # Display Results
                if algorithm_results:
                    valid_results = st.session_state.analysis_results['valid_results']
                    
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

                        # Mark anomalies in the analysis dataframe
                        analysis_df['is_anomaly'] = False
                        for result in valid_results.values():
                            if not result['anomalies'].empty:
                                analysis_df.loc[result['anomalies'].index, 'is_anomaly'] = True

                        # Scatter Plot
                        st.markdown("#### 📈 Anomaly Visualization")
                        fig_scatter = px.scatter(
                            analysis_df, x='charge_amount_diff', y='percentage_diff',
                            color='is_anomaly', 
                            title="Charge Amount vs Percentage Differences",
                            color_discrete_map={True: '#FF6B6B', False: '#4ECDC4'},
                            hover_data=['transaction_type_id'],
                            size_max=10
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)

                        # DOWNLOAD SECTION
                        st.markdown("---")
                        st.markdown("## 💾 Export Analysis Results")
                        st.markdown('<div class="download-section">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Export anomaly data
                            anomaly_export_df = analysis_df[analysis_df['is_anomaly']].copy()
                            if not anomaly_export_df.empty:
                                csv_anomalies = anomaly_export_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Anomaly Data",
                                    data=csv_anomalies,
                                    file_name=f"anomaly_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv",
                                    use_container_width=True,
                                    help="Download only the transactions flagged as anomalies"
                                )
                            else:
                                st.info("No anomalies to export")

                        with col2:
                            # Export full analysis
                            csv_full = analysis_df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download Full Analysis",
                                data=csv_full,
                                file_name=f"complete_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                mime="text/csv",
                                use_container_width=True,
                                help="Download the complete dataset with anomaly flags"
                            )

                        with col3:
                            # Export algorithm results summary
                            summary_data = []
                            for algo_name, result in valid_results.items():
                                summary_data.append({
                                    'Algorithm': algo_name,
                                    'Anomalies_Detected': result['count'],
                                    'Success_Rate': f"{(result['count'] / total_records * 100):.1f}%"
                                })
                            
                            summary_df = pd.DataFrame(summary_data)
                            csv_summary = summary_df.to_csv(index=False)
                            st.download_button(
                                label="📈 Download Summary Report",
                                data=csv_summary,
                                file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                mime="text/csv",
                                use_container_width=True,
                                help="Download algorithm performance summary"
                            )

                        st.markdown('</div>', unsafe_allow_html=True)

                    else:
                        st.info("✅ No anomalies detected by any algorithm")
                else:
                    st.info("✅ No algorithms produced results")

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")

    # DATA EXPLORER SECTION
    st.markdown("---")
    st.markdown("## 📋 Data Explorer")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("Explore the complete dataset used for analysis")
    
    with col2:
        if st.button("📖 Toggle Data View", use_container_width=True):
            st.session_state.view_raw_data = not st.session_state.view_raw_data
            st.rerun()

    if st.session_state.view_raw_data:
        st.markdown("#### Complete Dataset")
        st.dataframe(merged_df, use_container_width=True, height=400)
        
        # Data Export Options
        st.markdown("#### 📤 Export Raw Data")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            csv_raw = merged_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Raw CSV",
                data=csv_raw,
                file_name=f"raw_transaction_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col2:
            # Create a basic statistics report
            stats_report = f"""
Revenue Assurance Data Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Dataset Overview:
- Total Records: {len(merged_df):,}
- Total Transaction Amount: ${merged_df['charge_amount'].sum():,.2f}
- Average Transaction: ${merged_df['charge_amount'].mean():.2f}
- Unique Transaction Types: {merged_df['transaction_type_id'].nunique()}

Statistical Summary:
{merged_df[['charge_amount', 'charge_amount_diff', 'percentage_diff']].describe().to_string()}
            """
            st.download_button(
                label="📄 Download Stats Report",
                data=stats_report,
                file_name=f"data_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Quick Navigation Section
    st.markdown("---")
    st.markdown("## 🚀 Quick Navigation")
    st.info("Use the sidebar to navigate between different features and analysis tools.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 AI Analysis**")
        st.write("Real-time AI-powered revenue analysis and insights")
        
    with col2:
        st.markdown("**📊 Categorization**")
        st.write("AI-assisted revenue categorization and mapping")
        
    with col3:
        st.markdown("**🔍 Monitoring**")
        st.write("Real-time transaction monitoring and alerts")

    # System Status
    st.markdown("## 🟢 System Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.success("**All Systems Operational**")
    
    with status_col2:
        st.info("**Last Updated**")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with status_col3:
        st.warning("**Need Help?**")
        st.write("Check the documentation or contact support")

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

if __name__ == "__main__":
    main()