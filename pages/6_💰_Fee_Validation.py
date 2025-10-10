import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_transaction_data, get_charges_data, get_price_recommendations

st.set_page_config(page_title="Fee Validation", layout="wide")
st.title("Fee Validation & Compliance")

# Load data
try:
    transactions_df = get_transaction_data()
    charges_df = get_charges_data()
    recommendations_df = get_price_recommendations()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    transactions_df = pd.DataFrame()
    charges_df = pd.DataFrame()
    recommendations_df = pd.DataFrame()

def safe_convert_to_float(value):
    """Safely convert any value to float"""
    try:
        if value is None or pd.isna(value) or value == '':
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace('$', '').replace(',', '').strip()
            return float(cleaned) if cleaned else 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def verify_fee_compliance(transaction, charges_df, recommendations_df):
    """Simple fee compliance verification"""
    try:
        amount = safe_convert_to_float(transaction.get("amount", 0))
        fee_applied = safe_convert_to_float(transaction.get("fee_applied", 0))
        
        # Simple fee validation logic
        expected_fee = amount * 0.02  # 2% expected fee
        tolerance = 0.10  # 10% tolerance
        
        if fee_applied < expected_fee * (1 - tolerance):
            return {
                "status": "violation",
                "fee_status_type": "Undercharge",
                "actual_fee": fee_applied,
                "expected_fee": expected_fee,
                "difference": fee_applied - expected_fee
            }
        elif fee_applied > expected_fee * (1 + tolerance):
            return {
                "status": "violation", 
                "fee_status_type": "Overcharge",
                "actual_fee": fee_applied,
                "expected_fee": expected_fee,
                "difference": fee_applied - expected_fee
            }
        else:
            return {
                "status": "compliant",
                "fee_status_type": "Normal",
                "actual_fee": fee_applied,
                "expected_fee": expected_fee,
                "difference": fee_applied - expected_fee
            }
    except Exception as e:
        return {
            "status": "error",
            "fee_status_type": "Error",
            "actual_fee": 0,
            "expected_fee": 0,
            "difference": 0
        }

if not transactions_df.empty:
    # Verify fee compliance
    with st.spinner("Validating fee compliance..."):
        fee_results = []
        for _, row in transactions_df.iterrows():
            verification = verify_fee_compliance(row.to_dict(), charges_df, recommendations_df)
            fee_results.append(verification)
        
        # Add fee analysis columns safely
        for i, result in enumerate(fee_results):
            transactions_df.at[transactions_df.index[i], 'fee_status'] = result.get('status', 'unknown')
            transactions_df.at[transactions_df.index[i], 'fee_status_type'] = result.get('fee_status_type', 'Unknown')
            transactions_df.at[transactions_df.index[i], 'actual_fee'] = result.get('actual_fee', 0)
            transactions_df.at[transactions_df.index[i], 'expected_fee'] = result.get('expected_fee', 0)
            transactions_df.at[transactions_df.index[i], 'fee_difference'] = result.get('difference', 0)
    
    # Ensure fee_status_type exists and count safely
    if 'fee_status_type' in transactions_df.columns:
        status_counts = transactions_df['fee_status_type'].value_counts()
    else:
        status_counts = pd.Series()
    
    # Fee compliance summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(transactions_df)
        st.metric("Total Transactions", total)
    
    with col2:
        compliant = status_counts.get('Normal', 0)
        st.metric("Compliant", compliant, delta=f"{(compliant/total*100):.1f}%" if total > 0 else "0%")
    
    with col3:
        undercharges = status_counts.get('Undercharge', 0)
        st.metric("Undercharges", undercharges, delta=f"{(undercharges/total*100):.1f}%" if total > 0 else "0%")
    
    with col4:
        overcharges = status_counts.get('Overcharge', 0)
        st.metric("Overcharges", overcharges, delta=f"{(overcharges/total*100):.1f}%" if total > 0 else "0%")
    
    # Visualization
    if not status_counts.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.pie(
                values=status_counts.values, 
                names=status_counts.index, 
                title="Fee Compliance Status",
                color_discrete_map={
                    'Normal': '#00ff00',
                    'Undercharge': '#ffff00', 
                    'Overcharge': '#ff0000',
                    'Error': '#808080'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Fee analysis by transaction type
            if 'transaction_type_name' in transactions_df.columns:
                fee_by_type = transactions_df.groupby(['transaction_type_name', 'fee_status_type']).size().reset_index(name='count')
                if not fee_by_type.empty:
                    fig2 = px.bar(
                        fee_by_type, 
                        x='transaction_type_name', 
                        y='count', 
                        color='fee_status_type',
                        title="Fee Status by Transaction Type", 
                        barmode='stack',
                        color_discrete_map={
                            'Normal': '#00ff00',
                            'Undercharge': '#ffff00',
                            'Overcharge': '#ff0000',
                            'Error': '#808080'
                        }
                    )
                    fig2.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No fee data available by transaction type")
            else:
                # Amount distribution by fee status
                if 'amount' in transactions_df.columns:
                    transactions_df['amount_numeric'] = pd.to_numeric(transactions_df['amount'], errors='coerce')
                    valid_amounts = transactions_df[transactions_df['amount_numeric'].notna()]
                    if not valid_amounts.empty:
                        fig3 = px.box(
                            valid_amounts,
                            x='fee_status_type',
                            y='amount_numeric',
                            title="Transaction Amount Distribution by Fee Status",
                            color='fee_status_type'
                        )
                        st.plotly_chart(fig3, use_container_width=True)
    
    # Fee difference analysis
    st.subheader(" Fee Difference Analysis")
    
    if 'fee_difference' in transactions_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Fee difference distribution
            fig4 = px.histogram(
                transactions_df,
                x='fee_difference',
                color='fee_status_type',
                title="Distribution of Fee Differences",
                nbins=20,
                color_discrete_map={
                    'Normal': '#00ff00',
                    'Undercharge': '#ffff00',
                    'Overcharge': '#ff0000'
                }
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # Fee difference by amount
            if 'amount' in transactions_df.columns:
                transactions_df['amount_numeric'] = pd.to_numeric(transactions_df['amount'], errors='coerce')
                valid_data = transactions_df[transactions_df['amount_numeric'].notna() & transactions_df['fee_difference'].notna()]
                if not valid_data.empty:
                    fig5 = px.scatter(
                        valid_data,
                        x='amount_numeric',
                        y='fee_difference',
                        color='fee_status_type',
                        title="Fee Difference vs Transaction Amount",
                        hover_data=['transaction_type_name'] if 'transaction_type_name' in transactions_df.columns else None,
                        color_discrete_map={
                            'Normal': '#00ff00',
                            'Undercharge': '#ffff00',
                            'Overcharge': '#ff0000'
                        }
                    )
                    st.plotly_chart(fig5, use_container_width=True)
    
    # Detailed fee analysis table
    st.subheader("Detailed Fee Analysis")
    
    # Build display columns safely
    display_cols = ['id']
    if 'transaction_type_name' in transactions_df.columns:
        display_cols.append('transaction_type_name')
    if 'amount' in transactions_df.columns:
        display_cols.append('amount')
    if 'fee_applied' in transactions_df.columns:
        display_cols.append('fee_applied')
    display_cols.extend(['fee_status_type', 'actual_fee', 'expected_fee', 'fee_difference'])
    
    # Only include columns that actually exist
    display_cols = [col for col in display_cols if col in transactions_df.columns]
    
    if display_cols:
        # Format numeric columns for display
        display_df = transactions_df[display_cols].copy()
        
        # Safely format numeric columns
        numeric_cols = ['amount', 'fee_applied', 'actual_fee', 'expected_fee', 'fee_difference']
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download option
        csv = transactions_df[display_cols].to_csv(index=False)
        st.download_button(
            label="📥 Download Fee Analysis as CSV",
            data=csv,
            file_name="fee_validation_analysis.csv",
            mime="text/csv"
        )
    else:
        st.warning("No columns available for display")
    
else:
    st.info(" No transaction data available. Please check your database connection.")

# Show charges and recommendations info
with st.expander(" Fee Structure Information"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Charges")
        if not charges_df.empty:
            st.dataframe(charges_df, use_container_width=True)
        else:
            st.info("No charges data available")
    
    with col2:
        st.subheader("Price Recommendations")
        if not recommendations_df.empty:
            st.dataframe(recommendations_df, use_container_width=True)
        else:
            st.info("No price recommendations available")