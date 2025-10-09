import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from utils.visualization import create_monitoring_charts

def show_monitoring_dashboard(filtered_df, full_df):
    """Display the main monitoring dashboard"""
    
    # Key Metrics
    show_key_metrics(filtered_df)
    
    # Visualizations
    st.subheader("📈 Transaction Anomalies Overview")
    
    # Create visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Amount vs Hour", 
        "Amount vs Processing Time", 
        "Amount Distribution", 
        "Anomaly Types"
    ])
    
    with tab1:
        show_amount_vs_hour_chart(full_df)
    
    with tab2:
        show_amount_vs_processing_chart(full_df)
    
    with tab3:
        show_amount_distribution_chart(full_df)
    
    with tab4:
        show_anomaly_types_chart(full_df)

def show_key_metrics(df):
    """Display key monitoring metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_txn = len(df)
        st.metric("Total Transactions", total_txn)
    
    with col2:
        if 'anomaly' in df.columns:
            anomaly_count = len(df[df['anomaly'] == 'Anomaly'])
            st.metric("Anomalies Detected", anomaly_count)
        else:
            st.metric("Anomalies Detected", 0)
    
    with col3:
        if 'amount' in df.columns:
            total_amount = df['amount'].sum()
            st.metric("Total Amount", f"${total_amount:,.2f}")
        else:
            st.metric("Total Amount", "$0")
    
    with col4:
        if 'anomaly' in df.columns and len(df) > 0:
            anomaly_rate = (len(df[df['anomaly'] == 'Anomaly']) / len(df)) * 100
            st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")
        else:
            st.metric("Anomaly Rate", "0%")

def show_amount_vs_hour_chart(df):
    """Show amount vs hour of day scatter plot"""
    if 'hour_of_day' in df.columns and 'amount' in df.columns and 'anomaly' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='hour_of_day', y='amount', hue='anomaly', data=df, palette=['blue','red'], ax=ax)
        ax.set_title('Transaction Amount vs Hour of Day')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Amount ($)')
        st.pyplot(fig)
        
        st.markdown("""
        **Explanation:**  
        Each dot is a transaction.  
        - X-axis = Hour of the day  
        - Y-axis = Transaction amount  
        - Red = anomaly, Blue = normal  

        If you see red dots outside normal working hours or with unusual amounts, they may signal suspicious activity.
        """)
    else:
        st.info("Required data not available for this chart")

def show_amount_vs_processing_chart(df):
    """Show amount vs processing time scatter plot"""
    if 'processing_time' in df.columns and 'amount' in df.columns and 'anomaly' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='processing_time', y='amount', hue='anomaly', data=df, palette=['blue','red'], ax=ax)
        ax.set_title('Transaction Amount vs Processing Time')
        ax.set_xlabel('Processing Time (seconds)')
        ax.set_ylabel('Amount ($)')
        st.pyplot(fig)
        
        st.markdown("""
        **Explanation:**  
        - X-axis = Processing time (seconds)  
        - Y-axis = Transaction amount  

        Anomalies (red) could mean very large amounts processed unusually fast,  
        or small amounts with unusually long delays. Both could indicate system issues or fraud.
        """)
    else:
        st.info("Required data not available for this chart")

def show_amount_distribution_chart(df):
    """Show boxplot of amount distribution by anomaly status"""
    if 'anomaly' in df.columns and 'amount' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='anomaly', y='amount', data=df, ax=ax)
        ax.set_title('Transaction Amount Distribution (Normal vs Anomaly)')
        ax.set_xlabel('Anomaly Status')
        ax.set_ylabel('Amount ($)')
        st.pyplot(fig)
        
        st.markdown("""
        **Explanation:**  
        This shows how transaction amounts are distributed between normal and anomalous transactions.  
        - If anomalies are consistently higher/lower than normal ones, the issue is amount-driven.  
        - If they overlap, anomalies may be due to timing or type of transaction.
        """)
    else:
        st.info("Required data not available for this chart")

def show_anomaly_types_chart(df):
    """Show bar chart of anomalies by transaction type"""
    if any(col.startswith('type_') for col in df.columns) and 'anomaly' in df.columns:
        anomaly_counts = df[df['anomaly']=='Anomaly'].filter(like='type_').sum()
        if not anomaly_counts.empty:
            st.bar_chart(anomaly_counts)
            
            st.markdown("""
            **Explanation:**  
            Each bar shows how many anomalies were detected for each transaction type.  
            High counts for one type (e.g., transfers or withdrawals) suggest those need closer investigation.
            """)
        else:
            st.info("No anomaly data available for transaction types")
    else:
        st.info("No transaction type data available")

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_monitoring_dashboard(filtered_df, full_df):
    """Display the main monitoring dashboard"""
    
    # Key Metrics
    show_key_metrics(filtered_df)
    
    # Visualizations
    st.subheader("📈 Transaction Anomalies Overview")
    
    # Create visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Amount vs Hour", 
        "Amount vs Processing Time", 
        "Amount Distribution", 
        "Anomaly Types"
    ])
    
    with tab1:
        show_amount_vs_hour_chart(full_df)
    
    with tab2:
        show_amount_vs_processing_chart(full_df)
    
    with tab3:
        show_amount_distribution_chart(full_df)
    
    with tab4:
        show_anomaly_types_chart(full_df)

def show_key_metrics(df):
    """Display key monitoring metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_txn = len(df)
        st.metric("Total Transactions", total_txn)
    
    with col2:
        if 'anomaly' in df.columns:
            anomaly_count = len(df[df['anomaly'] == 'Anomaly'])
            st.metric("Anomalies Detected", anomaly_count)
        else:
            st.metric("Anomalies Detected", 0)
    
    with col3:
        if 'amount' in df.columns:
            total_amount = df['amount'].sum()
            st.metric("Total Amount", f"${total_amount:,.2f}")
        else:
            st.metric("Total Amount", "$0")
    
    with col4:
        if 'anomaly' in df.columns and len(df) > 0:
            anomaly_rate = (len(df[df['anomaly'] == 'Anomaly']) / len(df)) * 100
            st.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")
        else:
            st.metric("Anomaly Rate", "0%")

def show_amount_vs_hour_chart(df):
    """Show amount vs hour of day scatter plot"""
    if 'hour_of_day' in df.columns and 'amount' in df.columns and 'anomaly' in df.columns:
        # Use Plotly for better interactivity
        fig = px.scatter(
            df, 
            x='hour_of_day', 
            y='amount', 
            color='anomaly',
            color_discrete_map={'Normal': 'blue', 'Anomaly': 'red'},
            title='Transaction Amount vs Hour of Day',
            labels={'hour_of_day': 'Hour of Day', 'amount': 'Amount ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Explanation:**  
        Each dot is a transaction.  
        - X-axis = Hour of the day  
        - Y-axis = Transaction amount  
        - Red = anomaly, Blue = normal  

        If you see red dots outside normal working hours or with unusual amounts, they may signal suspicious activity.
        """)
    else:
        st.info("Required data not available for this chart")

def show_amount_vs_processing_chart(df):
    """Show amount vs processing time scatter plot"""
    if 'processing_time' in df.columns and 'amount' in df.columns and 'anomaly' in df.columns:
        fig = px.scatter(
            df, 
            x='processing_time', 
            y='amount', 
            color='anomaly',
            color_discrete_map={'Normal': 'blue', 'Anomaly': 'red'},
            title='Transaction Amount vs Processing Time',
            labels={'processing_time': 'Processing Time (seconds)', 'amount': 'Amount ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Explanation:**  
        - X-axis = Processing time (seconds)  
        - Y-axis = Transaction amount  

        Anomalies (red) could mean very large amounts processed unusually fast,  
        or small amounts with unusually long delays. Both could indicate system issues or fraud.
        """)
    else:
        st.info("Required data not available for this chart")

def show_amount_distribution_chart(df):
    """Show boxplot of amount distribution by anomaly status"""
    if 'anomaly' in df.columns and 'amount' in df.columns:
        fig = px.box(
            df, 
            x='anomaly', 
            y='amount',
            title='Transaction Amount Distribution (Normal vs Anomaly)',
            labels={'anomaly': 'Anomaly Status', 'amount': 'Amount ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Explanation:**  
        This shows how transaction amounts are distributed between normal and anomalous transactions.  
        - If anomalies are consistently higher/lower than normal ones, the issue is amount-driven.  
        - If they overlap, anomalies may be due to timing or type of transaction.
        """)
    else:
        st.info("Required data not available for this chart")

def show_anomaly_types_chart(df):
    """Show bar chart of anomalies by transaction type"""
    if any(col.startswith('type_') for col in df.columns) and 'anomaly' in df.columns:
        anomaly_counts = df[df['anomaly']=='Anomaly'].filter(like='type_').sum()
        if not anomaly_counts.empty:
            # Convert to proper format for Plotly
            anomaly_data = pd.DataFrame({
                'Transaction Type': anomaly_counts.index,
                'Anomaly Count': anomaly_counts.values
            })
            
            fig = px.bar(
                anomaly_data,
                x='Transaction Type',
                y='Anomaly Count',
                title='Anomalies by Transaction Type',
                labels={'Anomaly Count': 'Number of Anomalies'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Explanation:**  
            Each bar shows how many anomalies were detected for each transaction type.  
            High counts for one type (e.g., transfers or withdrawals) suggest those need closer investigation.
            """)
        else:
            st.info("No anomaly data available for transaction types")
    else:
        st.info("No transaction type data available")