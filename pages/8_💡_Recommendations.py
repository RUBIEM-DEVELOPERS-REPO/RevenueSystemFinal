import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_transaction_data
from utils.ai_analysis import real_ai_revenue_analysis

st.set_page_config(page_title="Recommendations", layout="wide")
st.title("💡 AI-Powered Recommendations")

# Load data
transactions_df = get_transaction_data()

if not transactions_df.empty:
    st.subheader("🤖 AI Business Insights")
    
    if st.button("Generate AI Recommendations", type="primary"):
        with st.spinner("AI is analyzing your data for insights..."):
            ai_insights = real_ai_revenue_analysis(transactions_df)
            
            if ai_insights:
                st.success("✅ AI Analysis Complete!")
                
                # Revenue Streams
                if 'revenue_streams' in ai_insights:
                    st.subheader("💰 Revenue Stream Analysis")
                    for stream in ai_insights['revenue_streams']:
                        with st.expander(f"{stream.get('stream_name', 'Stream')} - {stream.get('contribution_percentage', 0):.1f}%"):
                            st.write(f"**Growth Trend:** {stream.get('growth_trend', 'Unknown')}")
                            st.write(f"**Optimization Opportunity:** {stream.get('optimization_opportunity', 'None identified')}")
                
                # Key Insights
                if 'key_insights' in ai_insights:
                    st.subheader("💡 Key Insights")
                    for i, insight in enumerate(ai_insights['key_insights'], 1):
                        st.info(f"{i}. {insight}")
                
                # Revenue Risks
                if 'revenue_risks' in ai_insights:
                    st.subheader("⚠️ Revenue Risks")
                    for risk in ai_insights['revenue_risks']:
                        severity_color = {
                            'high': '🔴',
                            'medium': '🟡', 
                            'low': '🟢'
                        }.get(risk.get('severity', '').lower(), '⚪')
                        
                        st.error(f"{severity_color} **{risk.get('severity', 'Unknown').upper()}**: {risk.get('risk_description', '')}")
                        st.write(f"**Mitigation:** {risk.get('mitigation', 'No strategy provided')}")
                
                # Optimization Recommendations
                if 'optimization_recommendations' in ai_insights:
                    st.subheader("🎯 Optimization Recommendations")
                    for i, rec in enumerate(ai_insights['optimization_recommendations'], 1):
                        confidence_color = "🟢" if rec.get('confidence', 0) > 80 else "🟡" if rec.get('confidence', 0) > 60 else "🔴"
                        
                        with st.expander(f"{confidence_color} Recommendation {i}: {rec.get('recommendation', '')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Confidence", f"{rec.get('confidence', 0)}%")
                            with col2:
                                st.metric("Expected Impact", rec.get('expected_impact', 'Unknown'))
                            with col3:
                                st.metric("Implementation", rec.get('implementation_complexity', 'Unknown'))
            else:
                st.error("Unable to generate AI insights. Please check your API key or try again.")
    
    # Manual recommendations based on data analysis
    st.subheader("📊 Data-Driven Suggestions")
    
    if 'amount' in transactions_df.columns:
        # Fee optimization opportunities
        if 'fee_applied' in transactions_df.columns:
            avg_fee_rate = (transactions_df['fee_applied'].sum() / transactions_df['amount'].sum()) * 100
            st.metric("Average Fee Rate", f"{avg_fee_rate:.2f}%")
            
            if avg_fee_rate < 1.5:
                st.warning("💡 Consider reviewing fee structure - current rates may be below industry average")
            elif avg_fee_rate > 3.0:
                st.warning("💡 High fee rates detected - monitor for potential customer impact")
        
        # Transaction volume insights
        if 'created_at' in transactions_df.columns:
            transactions_df['hour'] = pd.to_datetime(transactions_df['created_at']).dt.hour
            peak_hours = transactions_df['hour'].value_counts().head(3)
            st.write("**Peak Transaction Hours:**", ", ".join([f"{h}:00" for h in peak_hours.index]))
            
            if len(peak_hours) > 0:
                st.info("💡 Consider scaling resources during peak hours for better performance")
else:
    st.info("No transaction data available for analysis")