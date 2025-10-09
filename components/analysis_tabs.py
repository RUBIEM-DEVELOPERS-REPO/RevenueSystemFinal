import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.visualization import create_revenue_charts

def show_analytics_tab(merged_df):
    st.subheader("📊 Revenue Analytics")
    
    if "amount" not in merged_df.columns:
        st.info("No amount data available for analytics")
        return
    
    # Currency selection
    currency = st.selectbox("Display Currency", ["USD", "ZiG"])
    exchange_rate = 13.5 if currency == "ZiG" else 1.0
    
    # Convert amount based on currency
    amount_col = "amount_converted"
    merged_df[amount_col] = merged_df["amount"] * exchange_rate
    
    # Revenue summary
    if "category_name" in merged_df.columns:
        revenue_summary = merged_df.groupby("category_name")[amount_col].sum().reset_index().sort_values(amount_col, ascending=False)
        
        # Create charts
        create_revenue_charts(revenue_summary, currency)
        
        # Show trend analysis if date data available
        if "created_at" in merged_df.columns:
            show_revenue_trends(merged_df, amount_col, currency)
    else:
        st.info("No category data available for revenue analysis")

def show_revenue_trends(merged_df, amount_col, currency):
    st.subheader("📈 Revenue Trends Over Time")
    
    merged_df["created_at"] = pd.to_datetime(merged_df["created_at"], errors="coerce")
    trend_data = merged_df.groupby([merged_df["created_at"].dt.date, "category_name"])[amount_col].sum().reset_index()
    
    if not trend_data.empty:
        # Create trend visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for cat in trend_data["category_name"].unique():
            sub_df = trend_data[trend_data["category_name"] == cat]
            ax.plot(sub_df["created_at"], sub_df[amount_col], marker="o", label=cat, linewidth=2)
        
        ax.legend()
        ax.set_ylabel(f"Revenue ({currency})")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)
        ax.set_title("Revenue Trends by Category")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Summary statistics
        show_trend_summary(trend_data, amount_col)

def show_trend_summary(trend_data, amount_col):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = trend_data[amount_col].sum()
        st.metric("Total Revenue Period", f"${total_revenue:,.2f}")
    
    with col2:
        avg_daily = trend_data.groupby('created_at')[amount_col].sum().mean()
        st.metric("Average Daily Revenue", f"${avg_daily:,.2f}")
    
    with col3:
        if len(trend_data['created_at'].unique()) > 1:
            growth = trend_data.groupby('created_at')[amount_col].sum().pct_change().mean() * 100
            st.metric("Avg Daily Growth", f"{growth:.1f}%")

    import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.ai_analysis import (
    real_ai_revenue_analysis, real_ml_revenue_forecast, 
    real_revenue_stream_clustering, ai_insights_with_severity
)

def show_analysis_tabs(controls, client):
    """Display the main analysis tabs"""
    
    with st.container():
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Live Transactions", "🔍 Anomaly Analysis", "💰 Fee Compliance", 
            "🤖 AI Insights", "📊 Fee Differences", "📋 Transaction Types", "🎯 Scenario Simulator"
        ])
        
        with tab1:
            show_live_transactions_tab(controls)
        
        with tab2:
            show_ai_revenue_analytics_tab(controls, client)
        
        with tab3:
            show_fee_compliance_tab()
        
        with tab4:
            show_ai_insights_tab(client)
        
        with tab5:
            show_fee_differences_tab()
        
        with tab6:
            show_transaction_types_tab(controls)
        
        with tab7:
            show_scenario_simulator_tab()

def show_live_transactions_tab(controls):
    """Display live transactions tab"""
    st.subheader("Live Transaction Stream")
    
    # Create filtered dataframe for display
    display_df = st.session_state.transactions_df.copy()
    
    # Apply currency conversion
    if 'amount' in display_df.columns:
        display_df["amount"] = pd.to_numeric(display_df["amount"], errors="coerce").fillna(0)
        if controls['display_currency'] == "ZiG":
            display_df["amount_converted"] = display_df["amount"] * controls['exchange_rate']
        else:
            display_df["amount_converted"] = display_df["amount"]
    else:
        display_df["amount_converted"] = 0
        
    # Apply filters
    display_df = display_df[
        (display_df["amount_converted"] >= controls['min_amount']) &
        (display_df["amount_converted"] <= controls['max_amount'])
    ]
    
    if controls['focus_category'] != "All" and "category_name" in display_df.columns:
        display_df = display_df[display_df["category_name"] == controls['focus_category']]
        
    # Display columns
    display_cols = ['id', 'amount_converted', 'currency', 'transaction_type_name']
    
    # Add available category columns
    if 'category_name' in display_df.columns:
        display_cols.append('category_name')
    elif 'suggested_category' in display_df.columns:
        display_cols.append('suggested_category')
        
    # Add anomaly columns if available
    if 'is_anomaly' in display_df.columns:
        display_cols.extend(['is_anomaly', 'combined_severity'])
        
    # Add fee columns if available
    if 'fee_status_type' in display_df.columns:
        display_cols.extend(['fee_status_type'])
        
    # Filter to only existing columns
    display_cols = [col for col in display_cols if col in display_df.columns]
    
    if display_cols:
        # Apply styling based on fee status
        def color_fee_status(val):
            if val == "Overcharge":
                return 'background-color: #ffcccc'
            elif val == "Undercharge":
                return 'background-color: #ccffcc'
            elif val == "Normal":
                return 'background-color: #e6f3ff'
            else:
                return ''
        
        if 'fee_status_type' in display_df.columns:
            styled_df = display_df[display_cols].head(50).style.applymap(
                color_fee_status, subset=['fee_status_type']
            )
        else:
            styled_df = display_df[display_cols].head(50)
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("No transaction data available yet")

# Add the other tab functions here (show_ai_revenue_analytics_tab, show_fee_compliance_tab, etc.)
# These would contain the code from your original tabs
def show_ai_revenue_analytics_tab(controls, client):
    """Display AI Revenue Analytics tab"""
    st.subheader("AI-Powered Revenue Analytics")
    
    if st.button("Run AI Revenue Analysis"):
        with st.spinner("Analyzing revenue data..."):
            ai_results = real_ai_revenue_analysis(st.session_state.transactions_df, client)
            if ai_results:
                st.success("AI Revenue Analysis Complete")
                st.write(ai_results)
            else:
                st.error("AI analysis failed or returned no results")

def show_fee_compliance_tab():  
    """Display Fee Compliance tab"""
    st.subheader("Fee Compliance Analysis")
    st.info("Fee compliance analysis functionality is under development.")

def show_ai_insights_tab(client):
    """Display AI Insights tab"""
    st.subheader("AI-Generated Business Insights")
    
    if st.button("Generate AI Insights"):
        with st.spinner("Generating AI insights..."):

            insights = ai_insights_with_severity(st.session_state.transactions_df, client)
            if insights:
                st.success("AI Insights Generated")
                for insight in insights:
                    severity_color = "🔴" if insight['severity'] == 'high' else "🟡" if insight['severity'] == 'medium' else "🟢"
                    st.write(f"{severity_color} **{insight['severity'].upper()}**: {insight['message']}")
            else:
                st.error("No insights generated")

def show_fee_differences_tab():
    """Display Fee Differences tab"""
    st.subheader("Fee Differences Analysis")
    st.info("Fee differences analysis functionality is under development.")

def show_transaction_types_tab(controls):

    """Display Transaction Types tab"""
    st.subheader("Transaction Types Overview")
    st.info("Transaction types overview functionality is under development.")
    # Placeholder for transaction types analysis

def show_scenario_simulator_tab():
    """Display Scenario Simulator tab"""
    st.subheader("Scenario Simulator")
    st.info("Scenario simulator functionality is under development.")
    # Placeholder for scenario simulation analysis

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def show_analytics_tab(merged_df):
    """Display revenue analytics tab"""
    
    st.subheader("📊 Revenue by Category/Subcategory")
    
    if "amount" not in merged_df.columns:
        st.info("No amount data available for analytics")
        return
    
    # Currency selection
    currency = st.selectbox("Display Currency", ["USD", "ZiG"])
    exchange_rate = 13.5 if currency == "ZiG" else 1.0
    
    # Convert amount based on currency
    amount_col = "amount_converted"
    merged_df[amount_col] = merged_df["amount"] * exchange_rate
    
    # Revenue summary
    if "category_name" in merged_df.columns:
        revenue_summary = merged_df.groupby("category_name")[amount_col].sum().reset_index().sort_values(amount_col, ascending=False)
        
        # Create charts
        create_revenue_charts(revenue_summary, currency)
        
        # Show trend analysis if date data available
        if "created_at" in merged_df.columns:
            show_revenue_trends(merged_df, amount_col, currency)
    else:
        st.info("No category data available for revenue analysis")

def create_revenue_charts(revenue_summary, currency):
    """Create revenue distribution charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart using Plotly
        fig_pie = px.pie(
            revenue_summary, 
            values=amount_col, 
            names='category_name', 
            title=f"Revenue Distribution by Category ({currency})"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart using Plotly
        fig_bar = px.bar(
            revenue_summary, 
            x='category_name', 
            y=amount_col,
            title=f"Revenue by Category ({currency})",
            labels={amount_col: f'Revenue ({currency})', 'category_name': 'Category'}
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

def show_revenue_trends(merged_df, amount_col, currency):
    """Display revenue trends over time"""
    
    st.subheader("📈 Revenue Trends Over Time")
    
    merged_df["created_at"] = pd.to_datetime(merged_df["created_at"], errors="coerce")
    trend_data = merged_df.groupby([merged_df["created_at"].dt.date, "category_name"])[amount_col].sum().reset_index()
    
    if not trend_data.empty:
        # Create interactive trend chart
        fig_trend = px.line(
            trend_data, 
            x='created_at', 
            y=amount_col, 
            color='category_name',
            title=f"Revenue Trends by Category ({currency})",
            labels={amount_col: f'Revenue ({currency})', 'created_at': 'Date'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Summary statistics
        show_trend_summary(trend_data, amount_col)

def show_trend_summary(trend_data, amount_col):
    """Display trend summary statistics"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = trend_data[amount_col].sum()
        st.metric("Total Revenue Period", f"${total_revenue:,.2f}")
    
    with col2:
        avg_daily = trend_data.groupby('created_at')[amount_col].sum().mean()
        st.metric("Average Daily Revenue", f"${avg_daily:,.2f}")
    
    with col3:
        if len(trend_data['created_at'].unique()) > 1:
            growth = trend_data.groupby('created_at')[amount_col].sum().pct_change().mean() * 100
            st.metric("Avg Daily Growth", f"{growth:.1f}%")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.ai_analysis import (
    real_ai_revenue_analysis, real_ml_revenue_forecast, 
    real_revenue_stream_clustering, ai_insights_with_severity
)

def show_analysis_tabs(controls, client):
    """Display the main analysis tabs"""
    
    with st.container():
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Live Transactions", "🔍 Anomaly Analysis", "💰 Fee Compliance", 
            "🤖 AI Insights", "📊 Fee Differences", "📋 Transaction Types", "🎯 Scenario Simulator"
        ])
        
        with tab1:
            show_live_transactions_tab(controls)
        
        with tab2:
            show_ai_revenue_analytics_tab(controls, client)
        
        with tab3:
            show_fee_compliance_tab()
        
        with tab4:
            show_ai_insights_tab(client)
        
        with tab5:
            show_fee_differences_tab()
        
        with tab6:
            show_transaction_types_tab(controls)
        
        with tab7:
            show_scenario_simulator_tab()

def show_live_transactions_tab(controls):
    """Display live transactions tab"""
    st.subheader("Live Transaction Stream")
    
    # Create filtered dataframe for display
    display_df = st.session_state.transactions_df.copy()
    
    # Apply currency conversion
    if 'amount' in display_df.columns:
        display_df["amount"] = pd.to_numeric(display_df["amount"], errors="coerce").fillna(0)
        if controls['display_currency'] == "ZiG":
            display_df["amount_converted"] = display_df["amount"] * controls['exchange_rate']
        else:
            display_df["amount_converted"] = display_df["amount"]
    else:
        display_df["amount_converted"] = 0
        
    # Apply filters
    display_df = display_df[
        (display_df["amount_converted"] >= controls['min_amount']) &
        (display_df["amount_converted"] <= controls['max_amount'])
    ]
    
    if controls['focus_category'] != "All" and "category_name" in display_df.columns:
        display_df = display_df[display_df["category_name"] == controls['focus_category']]
        
    # Display columns
    display_cols = ['id', 'amount_converted', 'currency', 'transaction_type_name']
    
    # Add available category columns
    if 'category_name' in display_df.columns:
        display_cols.append('category_name')
    elif 'suggested_category' in display_df.columns:
        display_cols.append('suggested_category')
        
    # Add anomaly columns if available
    if 'is_anomaly' in display_df.columns:
        display_cols.extend(['is_anomaly', 'combined_severity'])
        
    # Add fee columns if available
    if 'fee_status_type' in display_df.columns:
        display_cols.extend(['fee_status_type'])
        
    # Filter to only existing columns
    display_cols = [col for col in display_cols if col in display_df.columns]
    
    if display_cols:
        # Apply styling based on fee status
        def color_fee_status(val):
            if val == "Overcharge":
                return 'background-color: #ffcccc'
            elif val == "Undercharge":
                return 'background-color: #ccffcc'
            elif val == "Normal":
                return 'background-color: #e6f3ff'
            else:
                return ''
        
        if 'fee_status_type' in display_df.columns:
            styled_df = display_df[display_cols].head(50).style.applymap(
                color_fee_status, subset=['fee_status_type']
            )
        else:
            styled_df = display_df[display_cols].head(50)
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("No transaction data available yet")

def show_ai_revenue_analytics_tab(controls, client):
    """Display AI-powered revenue analytics tab"""
    st.subheader("🤖 AI-Powered Revenue Analytics")
    
    if not st.session_state.transactions_df.empty:
        # Currency selection
        currency = st.selectbox("Display Currency", ["USD", "ZiG"], key="revenue_currency")
        exchange_rate = 13.5 if currency == "ZiG" else 1.0
        
        # Prepare data
        analysis_df = st.session_state.transactions_df.copy()
        analysis_df["amount"] = pd.to_numeric(analysis_df["amount"], errors="coerce").fillna(0)
        analysis_df["amount_converted"] = analysis_df["amount"] * exchange_rate
        
        # Basic revenue summary
        st.markdown("### 📊 Basic Revenue Overview")
        
        if "category_name" in analysis_df.columns:
            revenue_summary = analysis_df.groupby("category_name")["amount_converted"].sum().reset_index().sort_values("amount_converted", ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig1 = px.pie(revenue_summary, values='amount_converted', names='category_name', 
                            title=f"Revenue Distribution by Category ({currency})")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Bar chart
                fig2 = px.bar(revenue_summary, x='category_name', y='amount_converted',
                            title=f"Revenue by Category ({currency})",
                            labels={'amount_converted': f'Revenue ({currency})', 'category_name': 'Category'})
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
        
        # AI-POWERED REVENUE ANALYSIS SECTION
        st.markdown("---")
        st.markdown("### 🧠 AI-Powered Revenue Insights")
        
        if st.button("🚀 Run AI Revenue Analysis", type="primary", key="ai_revenue_analysis"):
            with st.spinner("AI is analyzing revenue patterns... This may take a few seconds."):
                
                # 1. REAL AI REVENUE ANALYSIS
                ai_insights = real_ai_revenue_analysis(analysis_df, client)
                
                if ai_insights:
                    st.success("✅ AI Analysis Complete!")
                    
                    # Display AI Insights in an organized way
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💰 Revenue Stream Analysis")
                        if 'revenue_streams' in ai_insights:
                            for stream in ai_insights['revenue_streams'][:4]:  # Show top 4
                                trend_icon = "📈" if "increas" in stream.get('growth_trend', '').lower() else "📉" if "decreas" in stream.get('growth_trend', '').lower() else "➡️"
                                st.metric(
                                    f"{trend_icon} {stream.get('stream_name', 'Stream')}",
                                    f"{stream.get('contribution_percentage', 0):.1f}%",
                                    stream.get('growth_trend', 'Unknown trend')
                                )
                    
                    with col2:
                        st.markdown("#### ⚠️ AI-Detected Risks")
                        if 'revenue_risks' in ai_insights:
                            for risk in ai_insights['revenue_risks'][:3]:
                                severity_color = {
                                    'high': '🔴',
                                    'medium': '🟡', 
                                    'low': '🟢'
                                }.get(risk.get('severity', '').lower(), '⚪')
                                
                                st.error(f"{severity_color} **{risk.get('severity', 'Unknown').upper()}**: {risk.get('risk_description', '')}")
                                with st.expander("Mitigation Strategy"):
                                    st.write(risk.get('mitigation', 'No mitigation strategy provided'))
                    
                    # Key Insights
                    st.markdown("#### 💡 Key AI Insights")
                    if 'key_insights' in ai_insights:
                        for i, insight in enumerate(ai_insights['key_insights'][:5]):
                            st.info(f"{i+1}. {insight}")
                    
                    # AI Recommendations
                    st.markdown("#### 🎯 AI Optimization Recommendations")
                    if 'optimization_recommendations' in ai_insights:
                        for i, rec in enumerate(ai_insights['optimization_recommendations'][:4]):
                            confidence_color = "🟢" if rec.get('confidence', 0) > 80 else "🟡" if rec.get('confidence', 0) > 60 else "🔴"
                            
                            with st.expander(f"{confidence_color} Recommendation {i+1}: {rec.get('recommendation', '')}"):
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Confidence", f"{rec.get('confidence', 0)}%")
                                with col_b:
                                    st.metric("Impact", rec.get('expected_impact', 'Unknown'))
                                with col_c:
                                    st.metric("Complexity", rec.get('implementation_complexity', 'Unknown'))
                
                # 2. REAL ML REVENUE FORECASTING
                st.markdown("---")
                st.markdown("### 📈 AI Revenue Forecasting")
                
                ml_forecast = real_ml_revenue_forecast(analysis_df, periods=6)
                
                if ml_forecast:
                    # Create interactive forecast chart
                    forecast_dates = ml_forecast['dates']
                    forecast_values = ml_forecast['forecast']
                    confidence = ml_forecast['confidence_interval']
                    
                    # Create historical data for context
                    if 'created_at' in analysis_df.columns:
                        analysis_df['date'] = pd.to_datetime(analysis_df['created_at']).dt.date
                        historical_daily = analysis_df.groupby('date')['amount_converted'].sum().reset_index()
                        historical_daily['type'] = 'Historical'
                    
                    # Prepare forecast data
                    forecast_data = pd.DataFrame({
                        'date': forecast_dates,
                        'amount_converted': forecast_values,
                        'type': 'Forecast'
                    })
                    
                    # Combine historical and forecast data
                    if 'historical_daily' in locals():
                        combined_data = pd.concat([historical_daily, forecast_data])
                    else:
                        combined_data = forecast_data
                    
                    # Create the plot
                    fig = go.Figure()
                    
                    # Add historical data if available
                    if 'historical_daily' in locals():
                        fig.add_trace(go.Scatter(
                            x=historical_daily['date'],
                            y=historical_daily['amount_converted'],
                            mode='lines+markers',
                            name='Historical Revenue',
                            line=dict(color='blue', width=2)
                        ))
                    
                    # Add forecast with confidence interval
                    fig.add_trace(go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['amount_converted'] + confidence,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        name='Upper Bound'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['amount_converted'] - confidence,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(0,100,80,0.2)',
                        name='Confidence Interval'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=forecast_data['date'],
                        y=forecast_data['amount_converted'],
                        mode='lines+markers',
                        name='AI Forecast',
                        line=dict(color='red', width=3, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title="AI Revenue Forecast with 95% Confidence Interval",
                        xaxis_title="Date",
                        yaxis_title=f"Revenue ({currency})",
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Forecast metrics
                    total_forecast = sum(forecast_values)
                    growth_rate = ((forecast_values[-1] / forecast_values[0]) - 1) * 100 if len(forecast_values) > 1 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Forecasted", f"{currency} {total_forecast:,.0f}")
                    with col2:
                        st.metric("Avg Monthly", f"{currency} {np.mean(forecast_values):,.0f}")
                    with col3:
                        st.metric("Projected Growth", f"{growth_rate:+.1f}%")
                
                # 3. REAL REVENUE CLUSTERING ANALYSIS
                st.markdown("---")
                st.markdown("### 🎯 AI Customer Segmentation")
                
                clustering_result = real_revenue_stream_clustering(analysis_df)
                
                if clustering_result:
                    st.success(f"🤖 AI identified {clustering_result['optimal_k']} natural customer segments")
                    
                    # Display cluster analysis
                    cluster_analysis = clustering_result['cluster_analysis']
                    
                    # Create a user-friendly display of clusters
                    st.markdown("#### Customer Segments Analysis")
                    
                    # Convert cluster analysis to readable format
                    readable_clusters = []
                    for cluster_id in cluster_analysis.index:
                        cluster_data = cluster_analysis.loc[cluster_id]
                        readable_clusters.append({
                            'Segment': f"Segment {cluster_id + 1}",
                            'Customers': int(cluster_data[('amount', 'count')]),
                            'Avg Transaction': f"{currency} {cluster_data[('amount', 'mean')]:.2f}",
                            'Total Revenue': f"{currency} {cluster_data[('amount', 'sum')]:.2f}",
                            'Avg Fee': f"{currency} {cluster_data[('fee_applied', 'mean')]:.2f}"
                        })
                    
                    segments_df = pd.DataFrame(readable_clusters)
                    st.dataframe(segments_df, use_container_width=True)
                    
                    # Visualize the segments
                    if 'amount' in analysis_df.columns and 'fee_applied' in analysis_df.columns:
                        # Add cluster labels to dataframe for visualization
                        if len(clustering_result['clusters']) == len(analysis_df):
                            analysis_df_with_clusters = analysis_df.copy()
                            analysis_df_with_clusters['segment'] = [f"Segment {c+1}" for c in clustering_result['clusters']]
                            
                            fig = px.scatter(
                                analysis_df_with_clusters,
                                x='amount',
                                y='fee_applied',
                                color='segment',
                                size='amount_converted',
                                hover_data=['category_name'] if 'category_name' in analysis_df_with_clusters.columns else None,
                                title="AI-Discovered Customer Segments",
                                labels={
                                    'amount': f'Transaction Amount ({currency})',
                                    'fee_applied': f'Fee Applied ({currency})',
                                    'segment': 'Customer Segment'
                                }
                            )
                            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👆 Click the button above to run AI-powered revenue analysis")
            
        # Keep your existing trend analysis
        st.markdown("---")
        st.markdown("### 📈 Revenue Trends Over Time")
        
        if "created_at" in analysis_df.columns:
            analysis_df["created_at"] = pd.to_datetime(analysis_df["created_at"], errors="coerce")
            # Use available category column or fallback
            trend_group_col = None
            if "category_name" in analysis_df.columns:
                trend_group_col = "category_name"
            elif "suggested_category" in analysis_df.columns:
                trend_group_col = "suggested_category"
            elif "transaction_type_name" in analysis_df.columns:
                trend_group_col = "transaction_type_name"
            else:
                # If no category columns, just group by date
                trend_data = analysis_df.groupby(analysis_df["created_at"].dt.date)["amount_converted"].sum().reset_index()
                trend_data['category'] = 'All Transactions'
                trend_group_col = 'category'

            if trend_group_col and trend_group_col != 'category':  # If we have a real category column
                trend_data = analysis_df.groupby([analysis_df["created_at"].dt.date, trend_group_col])["amount_converted"].sum().reset_index()
            
            
            if not trend_data.empty:
                # Use the actual column name that exists in trend_data
                fig_trend = px.line(trend_data, x='created_at', y='amount_converted', color=trend_group_col,
                                title=f"Revenue Trends by Category ({currency})",
                                labels={'amount_converted': f'Revenue ({currency})', 'created_at': 'Date'})
                
                st.plotly_chart(fig_trend, use_container_width=True)
    
    else:
        st.info("No transaction data available for analysis")

def show_fee_compliance_tab():
    """Display fee compliance dashboard"""
    st.subheader("Fee Compliance Dashboard")
    
    fee_df = st.session_state.transactions_df.copy()
    
    if 'fee_status_type' in fee_df.columns:
        # Create unique timestamp for chart keys
        import time
        chart_timestamp = int(time.time() * 1000)
        
        # Fee status distribution
        fee_status_counts = fee_df['fee_status_type'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            pie_fig = px.pie(
                values=fee_status_counts.values,
                names=fee_status_counts.index,
                title="Fee Status Distribution"
            )
            st.plotly_chart(pie_fig, use_container_width=True, key=f"fee_pie_{chart_timestamp}")
        
        with col2:
            # Bar chart of fee status by transaction type
            if 'category_name' in fee_df.columns or 'suggested_category' in fee_df.columns:
                category_col = 'category_name' if 'category_name' in fee_df.columns else 'suggested_category'
                fee_by_category = fee_df.groupby([category_col, 'fee_status_type']).size().reset_index(name='count')
                bar_fig = px.bar(
                    fee_by_category,
                    x=category_col,
                    y='count',
                    color='fee_status_type',
                    title="Fee Status by Transaction Category",
                    barmode='stack'
                )
                st.plotly_chart(bar_fig, use_container_width=True, key=f"fee_bar_{chart_timestamp}")
            else:
                st.info("No category data available for fee analysis")
    else:
        st.info("No fee compliance data available yet")

def show_ai_insights_tab(client):
    """Display AI-powered insights tab"""
    st.subheader("AI-Powered Insights")
    
    insights_df = st.session_state.transactions_df.copy()
    
    if len(insights_df) > 10 and 'is_anomaly' in insights_df.columns:
        # Get only the anomaly rows
        anomaly_rows = insights_df[insights_df['is_anomaly'] == 1]
        
        if not anomaly_rows.empty:
            insights = ai_insights_with_severity(insights_df, anomaly_rows, client)
        else:
            insights = None
            
        if insights:
            st.info("### Revenue Insights")
            for insight in insights.get('revenue_insights', []):
                st.write(f"• {insight}")
            
            st.error("### Critical Anomalies")
            for anomaly in insights.get('critical_anomalies', []):
                st.write(f"🔴 {anomaly['description']} (Severity: {anomaly['severity']})")
                st.write(f"   Action: {anomaly['recommended_action']}")
            
            st.warning("### Investigation Priority")
            for txn_id in insights.get('investigation_priority', [])[:5]:
                st.write(f"• Transaction {txn_id}")
        else:
            st.info("AI insights not available - check API key or try again later")
    else:
        st.info("Need more data for AI insights (minimum 10 transactions)")

def show_fee_differences_tab():
    """Display fee differences analysis tab"""
    st.subheader("Fee Differences Analysis")
    
    if not st.session_state.fee_differences_table.empty:
        st.write("### Charges vs Recommended Prices Comparison")
            
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            undercharged = (st.session_state.fee_differences_table['fee_status_type'] == "Undercharge").sum()
            st.metric("Undercharges", undercharged)
        with col2:
            overcharged = (st.session_state.fee_differences_table['fee_status_type'] == "Overcharge").sum()
            st.metric("Overcharges", overcharged)
        with col3:
            normal = (st.session_state.fee_differences_table['fee_status_type'] == "Normal").sum()
            st.metric("Normal Fees", normal)
        with col4:
            mismatch = (st.session_state.fee_differences_table['fee_status_type'] == "Mismatch").sum()
            st.metric("Mismatches", mismatch)
                
        # Apply styling to the differences table
        def style_fee_differences(row):
            styles = [''] * len(row)
            if row['fee_status_type'] == 'Overcharge':
                styles = ['background-color: #ffcccc'] * len(row)
            elif row['fee_status_type'] == 'Undercharge':
                styles = ['background-color: #ccffcc'] * len(row)
            elif row['fee_status_type'] == 'Normal':
                styles = ['background-color: #e6f3ff'] * len(row)
            return styles
        
        styled_diff_table = st.session_state.fee_differences_table.style.apply(
            style_fee_differences, axis=1
        )
        
        st.dataframe(styled_diff_table, use_container_width=True)
    else:
        st.info("No fee differences data available yet")

def show_transaction_types_tab(controls):
    """Display transaction type analysis tab"""
    st.subheader("📋 Transaction Type Analysis")
    
    type_df = st.session_state.transactions_df.copy()
    
    # Ensure amount_converted column exists
    if 'amount' in type_df.columns:
        type_df["amount"] = pd.to_numeric(type_df["amount"], errors="coerce").fillna(0)
        if controls['display_currency'] == "ZiG":
            type_df["amount_converted"] = type_df["amount"] * controls['exchange_rate']
        else:
            type_df["amount_converted"] = type_df["amount"]
    else:
        type_df["amount_converted"] = 0
    
    # Safe category column selection
    category_col = None
    possible_category_cols = ['category_name', 'suggested_category', 'transaction_type_name']
    
    for col in possible_category_cols:
        if col in type_df.columns and not type_df[col].isna().all():
            category_col = col
            break
    
    if not category_col:
        type_df['fallback_category'] = 'All Transactions'
        category_col = 'fallback_category'
    
    if category_col and 'amount_converted' in type_df.columns and not type_df.empty:
        try:
            if type_df[category_col].notna().sum() > 0:
                category_volume = type_df.groupby(category_col)['amount_converted'].sum().sort_values(ascending=False)
                
                # Overall metrics section
                st.markdown("---")
                st.subheader("📈 Overall Transaction Metrics")

                if not type_df.empty:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if 'amount_converted' in type_df.columns:
                            total_volume = type_df['amount_converted'].sum()
                            st.metric("Total Volume", f"{controls['display_currency']} {total_volume:,.2f}")
                    
                    with col2:
                        if 'amount_converted' in type_df.columns:
                            avg_transaction = type_df['amount_converted'].mean()
                            st.metric("Avg Transaction", f"{controls['display_currency']} {avg_transaction:,.2f}")
                    
                    with col3:
                        total_transactions = len(type_df)
                        st.metric("Total Transactions", f"{total_transactions:,}")
                    
                    with col4:
                        if 'fee_applied' in type_df.columns:
                            total_fees = pd.to_numeric(type_df['fee_applied'], errors='coerce').sum()
                            st.metric("Total Fees", f"{controls['display_currency']} {total_fees:,.2f}")
                        else:
                            st.metric("Fee Data", "Not Available")
                else:
                    st.info("No transaction data available for overall metrics")
                    
                # Show category distribution
                st.markdown("### Category Distribution")
                fig = px.bar(
                    x=category_volume.index,
                    y=category_volume.values,
                    title=f"Revenue by {category_col.replace('_', ' ').title()}",
                    labels={'x': category_col.replace('_', ' ').title(), 'y': f'Revenue ({controls["display_currency"]})'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error in transaction types tab: {str(e)}")

def show_scenario_simulator_tab():
    """Display financial scenario simulator tab"""
    st.subheader("🎯 Financial Scenario Simulator")
    
    st.info("""
    **Financial Scenario Simulator**
    Adjust parameters below to simulate different financial scenarios and see their impact on revenue.
    """)
    
    # Scenario Configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📈 Volume Scenarios")
        base_volume = st.number_input("Base Transaction Volume", value=1000, min_value=100, step=100)
        growth_scenario = st.slider("Volume Growth %", -50, 200, 0, help="Simulate volume changes")
        seasonal_factor = st.slider("Seasonal Factor", 0.5, 2.0, 1.0, help="Seasonal demand multiplier")
    
    with col2:
        st.subheader("💵 Pricing Scenarios")
        base_fee_rate = st.slider("Base Fee Rate %", 0.1, 10.0, 2.0, step=0.1)
        premium_tier_rate = st.slider("Premium Tier Rate %", 0.1, 15.0, 3.5, step=0.1)
        discount_scenario = st.slider("Discount/Promo %", -20.0, 0.0, 0.0, step=1.0)
    
    with col3:
        st.subheader("📊 Mix Scenarios")
        high_value_mix = st.slider("High-Value Txns %", 0, 100, 20, help="Percentage of high-value transactions")
        international_mix = st.slider("International Txns %", 0, 100, 15, help="Percentage of international transactions")
        corporate_mix = st.slider("Corporate Txns %", 0, 100, 30, help="Percentage of corporate transactions")
    
    # Calculate Scenario Results
    simulated_volume = base_volume * (1 + growth_scenario/100) * seasonal_factor
    effective_fee_rate = base_fee_rate * (1 + discount_scenario/100)
    
    # Revenue calculation with mix factors
    base_revenue = simulated_volume * 100 * effective_fee_rate/100  # Assume $100 avg transaction
    premium_revenue = (simulated_volume * high_value_mix/100) * 500 * premium_tier_rate/100  # High-value at $500 avg
    international_revenue = (simulated_volume * international_mix/100) * 150 * (effective_fee_rate + 1)/100  # Intl premium
    corporate_revenue = (simulated_volume * corporate_mix/100) * 300 * (effective_fee_rate - 0.5)/100  # Corp discount
    
    total_revenue = base_revenue + premium_revenue + international_revenue + corporate_revenue
    
    # Display Results
    st.markdown("---")
    st.subheader("📊 Scenario Results")
    
    result_col1, result_col2, result_col3 = st.columns(3)
    
    with result_col1:
        st.metric("Simulated Volume", f"{simulated_volume:,.0f}", f"{growth_scenario}%")
        st.metric("Effective Fee Rate", f"{effective_fee_rate:.2f}%", f"{discount_scenario}%")
    
    with result_col2:
        st.metric("Base Revenue", f"${base_revenue:,.2f}")
        st.metric("Premium Revenue", f"${premium_revenue:,.2f}")
    
    with result_col3:
        st.metric("International Revenue", f"${international_revenue:,.2f}")
        st.metric("Corporate Revenue", f"${corporate_revenue:,.2f}")
    
    st.metric("**Total Projected Revenue**", f"**${total_revenue:,.2f}**", delta_color="off")
    
    # Visualization
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        # Revenue breakdown pie chart
        revenue_breakdown = {
            'Base': base_revenue,
            'Premium': premium_revenue,
            'International': international_revenue,
            'Corporate': corporate_revenue
        }
        
        breakdown_fig = px.pie(
            values=list(revenue_breakdown.values()),
            names=list(revenue_breakdown.keys()),
            title="Revenue Breakdown by Segment",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(breakdown_fig, use_container_width=True)
    
    with col_viz2:
        # Sensitivity analysis
        fee_rates = [effective_fee_rate * (1 + i/100) for i in range(-20, 21, 5)]
        revenues = [total_revenue * (1 + (rate - effective_fee_rate)/effective_fee_rate) for rate in fee_rates]
        
        sensitivity_fig = px.line(
            x=fee_rates,
            y=revenues,
            title="Revenue Sensitivity to Fee Rate Changes",
            labels={'x': 'Fee Rate (%)', 'y': 'Projected Revenue ($)'}
        )
        sensitivity_fig.add_vline(x=effective_fee_rate, line_dash="dash", line_color="red", 
                                annotation_text="Current Scenario")
        st.plotly_chart(sensitivity_fig, use_container_width=True)