import streamlit as st
import pandas as pd
import plotly.express as px

def show_fee_dashboard(validation_results):
    """Display fee validation dashboard"""
    
    st.subheader("🔍 Fee Validation Results")
    
    # Summary metrics
    show_fee_metrics(validation_results)
    
    # Validation results table
    show_validation_table(validation_results)
    
    # Summary chart
    show_validation_chart(validation_results)

def show_fee_metrics(validation_results):
    """Display key fee validation metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_charges = len(validation_results)
        st.metric("Total Charges", total_charges)
    
    with col2:
        valid_count = len(validation_results[validation_results['status'] == 'Valid'])
        st.metric("Valid Fees", valid_count)
    
    with col3:
        overcharge_count = len(validation_results[validation_results['status'] == 'Overcharge'])
        st.metric("Overcharges", overcharge_count)
    
    with col4:
        undercharge_count = len(validation_results[validation_results['status'] == 'Undercharge'])
        st.metric("Undercharges", undercharge_count)

def show_validation_table(validation_results):
    """Display detailed validation results table"""
    
    # Select columns for display
    display_columns = [
        "transaction_type_id", "charge_amount", "recommended_min_fee",
        "recommended_max_fee", "recommended_flat_fee", 
        "recommended_percentage_fee", "status"
    ]
    
    # Filter to only existing columns
    display_columns = [col for col in display_columns if col in validation_results.columns]
    
    # Apply styling based on status
    def color_status(val):
        if val == "Valid":
            return 'color: green; font-weight: bold'
        elif val == "Overcharge":
            return 'color: red; font-weight: bold'
        elif val == "Undercharge":
            return 'color: orange; font-weight: bold'
        else:
            return 'color: gray'
    
    styled_df = validation_results[display_columns].style.applymap(
        color_status, subset=['status']
    )
    
    st.dataframe(styled_df, use_container_width=True)

def show_validation_chart(validation_results):
    """Display validation summary chart"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        status_counts = validation_results['status'].value_counts()
        fig_bar = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="Fee Validation Summary",
            labels={'x': 'Validation Status', 'y': 'Count'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Fee Distribution by Status"
        )
        st.plotly_chart(fig_pie, use_container_width=True)