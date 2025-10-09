import streamlit as st
import pandas as pd

def show_sidebar_filters(transactions_df):
    """Display sidebar filters for transaction monitoring"""
    st.sidebar.header("🔎 Filters")
    
    # Date range filter
    if not transactions_df.empty and 'created_at' in transactions_df.columns:
        min_date = transactions_df['created_at'].min().date()
        max_date = transactions_df['created_at'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = [pd.Timestamp.now().date() - pd.Timedelta(days=7), pd.Timestamp.now().date()]
        st.sidebar.date_input("Select Date Range", date_range)

    # Transaction type filter
    transaction_types = [col for col in transactions_df.columns if col.startswith('type_')]
    selected_types = st.sidebar.multiselect(
        "Transaction Types", 
        transaction_types, 
        default=transaction_types[:3] if transaction_types else []
    )

    # Anomaly filter
    anomaly_filter = st.sidebar.multiselect(
        "Anomaly Status", 
        ['Normal', 'Anomaly'], 
        default=['Normal', 'Anomaly']
    )

    # Amount range filter
    if 'amount' in transactions_df.columns:
        min_amount = float(transactions_df['amount'].min())
        max_amount = float(transactions_df['amount'].max())
        
        amount_range = st.sidebar.slider(
            "Amount Range",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount)
        )
    else:
        amount_range = (0, 10000)

    # Apply filters
    filtered_df = apply_filters(transactions_df, date_range, selected_types, anomaly_filter, amount_range)
    
    # Show filter summary
    show_filter_summary(filtered_df, transactions_df)
    
    return filtered_df

def apply_filters(df, date_range, selected_types, anomaly_filter, amount_range):
    """Apply all filters to the dataframe"""
    filtered = df.copy()
    
    # Date range filter
    if len(date_range) == 2 and 'created_at' in filtered.columns:
        filtered = filtered[
            (filtered['created_at'].dt.date >= date_range[0]) &
            (filtered['created_at'].dt.date <= date_range[1])
        ]
    
    # Anomaly filter
    if 'anomaly' in filtered.columns:
        filtered = filtered[filtered['anomaly'].isin(anomaly_filter)]
    
    # Amount range filter
    if 'amount' in filtered.columns:
        filtered = filtered[
            (filtered['amount'] >= amount_range[0]) &
            (filtered['amount'] <= amount_range[1])
        ]
    
    # Transaction type filter
    if selected_types:
        filtered = filtered[(filtered[selected_types] == 1).any(axis=1)]
    
    return filtered

def show_filter_summary(filtered_df, original_df):
    """Show summary of applied filters"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Filter Summary")
    
    total_original = len(original_df)
    total_filtered = len(filtered_df)
    
    st.sidebar.metric("Total Transactions", total_filtered, f"of {total_original}")
    
    if 'anomaly' in filtered_df.columns:
        anomalies = len(filtered_df[filtered_df['anomaly'] == 'Anomaly'])
        st.sidebar.metric("Anomalies", anomalies)
    
    if 'amount' in filtered_df.columns:
        total_amount = filtered_df['amount'].sum()
        st.sidebar.metric("Total Amount", f"${total_amount:,.2f}")

    import streamlit as st
import pandas as pd

def show_sidebar_filters(transactions_df):
    """Display sidebar filters for transaction monitoring"""
    
    st.sidebar.header("🔎 Filters")
    
    # Date range filter
    if not transactions_df.empty and 'created_at' in transactions_df.columns:
        min_date = transactions_df['created_at'].min().date()
        max_date = transactions_df['created_at'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = [pd.Timestamp.now().date() - pd.Timedelta(days=7), pd.Timestamp.now().date()]
        st.sidebar.date_input("Select Date Range", date_range)

    # Transaction type filter
    transaction_types = [col for col in transactions_df.columns if col.startswith('type_')]
    selected_types = st.sidebar.multiselect(
        "Transaction Types", 
        transaction_types, 
        default=transaction_types[:3] if transaction_types else []
    )

    # Anomaly filter
    anomaly_filter = st.sidebar.multiselect(
        "Anomaly Status", 
        ['Normal', 'Anomaly'], 
        default=['Normal', 'Anomaly']
    )

    # Amount range filter
    if 'amount' in transactions_df.columns:
        min_amount = float(transactions_df['amount'].min())
        max_amount = float(transactions_df['amount'].max())
        
        amount_range = st.sidebar.slider(
            "Amount Range",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount)
        )
    else:
        amount_range = (0, 10000)

    # Apply filters
    filtered_df = apply_filters(transactions_df, date_range, selected_types, anomaly_filter, amount_range)
    
    # Show filter summary
    show_filter_summary(filtered_df, transactions_df)
    
    return filtered_df

def apply_filters(df, date_range, selected_types, anomaly_filter, amount_range):
    """Apply all filters to the dataframe"""
    filtered = df.copy()
    
    # Date range filter
    if len(date_range) == 2 and 'created_at' in filtered.columns:
        filtered = filtered[
            (filtered['created_at'].dt.date >= date_range[0]) &
            (filtered['created_at'].dt.date <= date_range[1])
        ]
    
    # Anomaly filter
    if 'anomaly' in filtered.columns:
        filtered = filtered[filtered['anomaly'].isin(anomaly_filter)]
    
    # Amount range filter
    if 'amount' in filtered.columns:
        filtered = filtered[
            (filtered['amount'] >= amount_range[0]) &
            (filtered['amount'] <= amount_range[1])
        ]
    
    # Transaction type filter
    if selected_types:
        filtered = filtered[(filtered[selected_types] == 1).any(axis=1)]
    
    return filtered

def show_filter_summary(filtered_df, original_df):
    """Show summary of applied filters"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Filter Summary")
    
    total_original = len(original_df)
    total_filtered = len(filtered_df)
    
    st.sidebar.metric("Total Transactions", total_filtered, f"of {total_original}")
    
    if 'anomaly' in filtered_df.columns:
        anomalies = len(filtered_df[filtered_df['anomaly'] == 'Anomaly'])
        st.sidebar.metric("Anomalies", anomalies)
    
    if 'amount' in filtered_df.columns:
        total_amount = filtered_df['amount'].sum()
        st.sidebar.metric("Total Amount", f"${total_amount:,.2f}")