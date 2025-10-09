import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_transaction_data, get_charges_data, get_price_recommendations
from utils.ai_analysis import FeeVerificationSystem

st.set_page_config(page_title="Fee Validation", layout="wide")
st.title("💰 Fee Validation & Compliance")

# Load data
transactions_df = get_transaction_data()
charges_df = get_charges_data()
recommendations_df = get_price_recommendations()


if not transactions_df.empty:
    # Initialize fee verification system
    fee_verifier = FeeVerificationSystem()
    
    # Verify fee compliance
    with st.spinner("Validating fee compliance..."):
        fee_results = []
        for _, row in transactions_df.iterrows():
            verification = fee_verifier.verify_fee_compliance(
                row.to_dict(), 
                charges_df, 
                recommendations_df
            )
            fee_results.append(verification)
        
        transactions_df['fee_analysis'] = fee_results
        transactions_df['fee_status'] = [r['status'] for r in fee_results]
        transactions_df['fee_status_type'] = [r.get('fee_status_type', 'Unknown') for r in fee_results]
    
    # Fee compliance summary
    status_counts = transactions_df['fee_status_type'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(transactions_df)
        st.metric("Total Transactions", total)
    
    with col2:
        compliant = status_counts.get('Normal', 0)
        st.metric("Compliant", compliant)
    
    with col3:
        undercharges = status_counts.get('Undercharge', 0)
        st.metric("Undercharges", undercharges)
    
    with col4:
        overcharges = status_counts.get('Overcharge', 0)
        st.metric("Overcharges", overcharges)
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, 
                     title="Fee Compliance Status")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Fee analysis by transaction type
        if 'transaction_type_name' in transactions_df.columns:
            fee_by_type = transactions_df.groupby(['transaction_type_name', 'fee_status_type']).size().reset_index(name='count')
            fig2 = px.bar(fee_by_type, x='transaction_type_name', y='count', color='fee_status_type',
                         title="Fee Status by Transaction Type", barmode='stack')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed fee analysis table
    st.subheader("Detailed Fee Analysis")
    display_cols = ['id', 'transaction_type_name', 'amount', 'fee_applied', 'fee_status_type']
    display_cols = [col for col in display_cols if col in transactions_df.columns]
    st.dataframe(transactions_df[display_cols], use_container_width=True)
else:
    st.info("No transaction data available")

import streamlit as st
import pandas as pd
from utils.database import get_charges_data, get_price_recommendations
from utils.fee_validation import validate_fee_compliance
from components.fee_dashboard import show_fee_dashboard
from components.fee_analysis import show_fee_analysis

st.set_page_config(page_title="Fee Validation", layout="wide")
st.title("💰 Fee Validation & Verification")

# Load data
with st.spinner("Loading fee data..."):
    charges_df = get_charges_data()
    recommendations_df = get_price_recommendations()

if charges_df.empty or recommendations_df.empty:
    st.error("Could not load fee data. Please check database connections.")
else:
    # Validate fees
    validation_results = validate_fee_compliance(charges_df, recommendations_df)
    
    # Show dashboard
    show_fee_dashboard(validation_results)
    
    # Show detailed analysis
    show_fee_analysis(validation_results)