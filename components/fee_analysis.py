import streamlit as st
import pandas as pd
import numpy as np

def show_fee_analysis(validation_results):
    """Display detailed fee analysis"""
    
    st.subheader("📊 Detailed Fee Analysis")
    
    # Create analysis tabs
    tab1, tab2, tab3 = st.tabs(["💰 Compliance Issues", "📈 Trend Analysis", "🎯 Recommendations"])
    
    with tab1:
        show_compliance_issues(validation_results)
    
    with tab2:
        show_trend_analysis(validation_results)
    
    with tab3:
        show_recommendations(validation_results)

def show_compliance_issues(validation_results):
    """Display compliance issues in detail"""
    
    # Show overcharges
    overcharges = validation_results[validation_results['status'] == 'Overcharge']
    if not overcharges.empty:
        st.error("🚨 Overcharges Detected")
        st.dataframe(overcharges, use_container_width=True)
        
        # Calculate total overcharge amount
        if 'charge_amount' in overcharges.columns and 'recommended_max_fee' in overcharges.columns:
            total_overcharge = (overcharges['charge_amount'] - overcharges['recommended_max_fee']).sum()
            st.metric("Total Overcharge Amount", f"${total_overcharge:,.2f}")
    
    # Show undercharges
    undercharges = validation_results[validation_results['status'] == 'Undercharge']
    if not undercharges.empty:
        st.warning("⚠️ Undercharges Detected")
        st.dataframe(undercharges, use_container_width=True)
        
        # Calculate revenue loss
        if 'charge_amount' in undercharges.columns and 'recommended_min_fee' in undercharges.columns:
            revenue_loss = (undercharges['recommended_min_fee'] - undercharges['charge_amount']).sum()
            st.metric("Potential Revenue Loss", f"${revenue_loss:,.2f}")

def show_trend_analysis(validation_results):
    """Analyze fee validation trends"""
    
    if 'transaction_type_id' in validation_results.columns:
        # Analysis by transaction type
        type_analysis = validation_results.groupby('transaction_type_id').agg({
            'status': ['count', lambda x: (x == 'Valid').sum()],
            'charge_amount': 'mean'
        }).round(2)
        
        type_analysis.columns = ['total_charges', 'valid_charges', 'avg_charge_amount']
        type_analysis['compliance_rate'] = (type_analysis['valid_charges'] / type_analysis['total_charges'] * 100).round(1)
        
        st.write("**Compliance Rate by Transaction Type**")
        st.dataframe(type_analysis, use_container_width=True)
        
        # Highlight low compliance types
        low_compliance = type_analysis[type_analysis['compliance_rate'] < 80]
        if not low_compliance.empty:
            st.warning(f"⚠️ {len(low_compliance)} transaction types have compliance rate below 80%")

def show_recommendations(validation_results):
    """Generate fee validation recommendations"""
    
    recommendations = []
    
    # Check overall compliance rate
    total_charges = len(validation_results)
    valid_charges = len(validation_results[validation_results['status'] == 'Valid'])
    compliance_rate = (valid_charges / total_charges * 100) if total_charges > 0 else 0
    
    if compliance_rate < 90:
        recommendations.append(f"📊 **Overall Compliance**: Current compliance rate is {compliance_rate:.1f}%. Aim for 95%+")
    
    # Check for systematic issues
    overcharge_rate = len(validation_results[validation_results['status'] == 'Overcharge']) / total_charges * 100
    if overcharge_rate > 5:
        recommendations.append(f"🔴 **Overcharge Issue**: {overcharge_rate:.1f}% of charges are overcharges. Review pricing rules.")
    
    undercharge_rate = len(validation_results[validation_results['status'] == 'Undercharge']) / total_charges * 100
    if undercharge_rate > 5:
        recommendations.append(f"🟡 **Undercharge Issue**: {undercharge_rate:.1f}% of charges are undercharges. Potential revenue loss.")
    
    # Transaction type specific recommendations
    if 'transaction_type_id' in validation_results.columns:
        type_compliance = validation_results.groupby('transaction_type_id')['status'].apply(
            lambda x: (x == 'Valid').sum() / len(x) * 100
        )
        
        low_compliance_types = type_compliance[type_compliance < 80]
        for ttype, rate in low_compliance_types.items():
            recommendations.append(f"🎯 **Transaction Type {ttype}**: Low compliance rate ({rate:.1f}%). Needs review.")
    
    # Display recommendations
    if recommendations:
        st.info("### 🎯 Optimization Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.success("✅ Excellent fee compliance! No major issues detected.")