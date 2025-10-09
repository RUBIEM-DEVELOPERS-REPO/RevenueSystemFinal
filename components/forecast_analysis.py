import streamlit as st
import pandas as pd
import numpy as np

def show_forecast_analysis(forecast_results):
    """Display detailed forecast analysis"""
    
    st.subheader("🔮 Forecast Analysis & Insights")
    
    # Create analysis tabs
    tab1, tab2, tab3 = st.tabs(["📈 Forecast Details", "⚠️ Early Warnings", "🎯 Business Insights"])
    
    with tab1:
        show_forecast_details(forecast_results)
    
    with tab2:
        show_early_warnings(forecast_results)
    
    with tab3:
        show_business_insights(forecast_results)

def show_forecast_details(forecast_results):
    """Display detailed forecast data"""
    
    if 'forecast_data' in forecast_results:
        forecast_df = forecast_results['forecast_data']
        
        st.write("### 📅 Detailed Forecast Data")
        st.dataframe(forecast_df, use_container_width=True)
        
        # Forecast statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_forecast = forecast_df['forecast_revenue'].min()
            st.metric("Minimum Forecast", f"${min_forecast:,.2f}")
        
        with col2:
            max_forecast = forecast_df['forecast_revenue'].max()
            st.metric("Maximum Forecast", f"${max_forecast:,.2f}")
        
        with col3:
            avg_forecast = forecast_df['forecast_revenue'].mean()
            st.metric("Average Forecast", f"${avg_forecast:,.2f}")
        
        # Export option
        if st.button("📥 Export Forecast Data"):
            csv = forecast_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="revenue_forecast.csv",
                mime="text/csv"
            )

def show_early_warnings(forecast_results):
    """Display early warning system"""
    
    if 'historical_data' in forecast_results and 'forecast_data' in forecast_results:
        historical_df = forecast_results['historical_data']
        forecast_df = forecast_results['forecast_data']
        
        # Get latest actual and first forecast
        latest_actual = historical_df['total_revenue'].iloc[-1]
        first_forecast = forecast_df['forecast_revenue'].iloc[0]
        
        # Calculate deviation
        deviation = ((latest_actual - first_forecast) / first_forecast * 100) if first_forecast > 0 else 0
        
        st.write("### ⚠️ Performance Alert System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Latest Actual Revenue", f"${latest_actual:,.2f}")
        
        with col2:
            st.metric("Expected Revenue", f"${first_forecast:,.2f}")
        
        with col3:
            st.metric("Deviation", f"{deviation:+.1f}%")
        
        # Alert logic
        if deviation < -10:
            st.error(f"🚨 CRITICAL: Revenue is {abs(deviation):.1f}% below forecast! Immediate action required.")
        elif deviation < -5:
            st.warning(f"⚠️ WARNING: Revenue is {abs(deviation):.1f}% below forecast. Monitor closely.")
        elif deviation > 10:
            st.success(f"📈 EXCELLENT: Revenue is {deviation:.1f}% above forecast!")
        elif deviation > 5:
            st.info(f"👍 GOOD: Revenue is {deviation:.1f}% above forecast.")
        else:
            st.success("✅ Revenue is within expected range.")
        
        # Trend analysis
        show_trend_analysis(historical_df, forecast_df)

def show_trend_analysis(historical_df, forecast_df):
    """Analyze revenue trends"""
    
    st.write("### 📊 Trend Analysis")
    
    # Historical trend
    historical_trend = historical_df['total_revenue'].pct_change().mean() * 100
    
    # Forecast trend
    forecast_trend = forecast_df['forecast_revenue'].pct_change().mean() * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Historical Growth Trend", f"{historical_trend:+.1f}%")
    
    with col2:
        st.metric("Forecast Growth Trend", f"{forecast_trend:+.1f}%")
    
    # Trend comparison
    if forecast_trend < historical_trend * 0.5:
        st.warning("📉 Forecast shows significant growth slowdown")
    elif forecast_trend > historical_trend * 1.5:
        st.success("📈 Forecast shows accelerated growth")

def show_business_insights(forecast_results):
    """Generate business insights from forecasts"""
    
    insights = []
    
    if 'historical_data' in forecast_results and 'forecast_data' in forecast_results:
        historical_df = forecast_results['historical_data']
        forecast_df = forecast_results['forecast_data']
        
        # Insight 1: Growth momentum
        hist_avg = historical_df['total_revenue'].mean()
        forecast_avg = forecast_df['forecast_revenue'].mean()
        growth = ((forecast_avg - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
        
        if growth > 10:
            insights.append("🚀 **Strong Growth Momentum**: Forecast indicates significant revenue growth ahead")
        elif growth > 0:
            insights.append("📈 **Steady Growth**: Moderate growth expected in the forecast period")
        else:
            insights.append("📉 **Growth Challenge**: Forecast shows potential revenue decline")
        
        # Insight 2: Volatility analysis
        hist_volatility = historical_df['total_revenue'].std()
        if hist_volatility > hist_avg * 0.3:
            insights.append("🎢 **High Volatility**: Revenue shows significant fluctuations. Consider risk mitigation.")
        
        # Insight 3: Seasonal patterns
        if len(historical_df) >= 30:  # Enough data for seasonal analysis
            weekly_pattern = historical_df.groupby(historical_df['date'].dt.dayofweek)['total_revenue'].mean()
            if weekly_pattern.std() > weekly_pattern.mean() * 0.2:
                insights.append("📅 **Weekly Patterns**: Strong day-of-week effects detected in revenue")
    
    # Display insights
    if insights:
        st.info("### 🎯 Business Insights")
        for i, insight in enumerate(insights, 1):
            st.write(f"{i}. {insight}")
    else:
        st.info("💡 Enable more data tracking for deeper business insights")