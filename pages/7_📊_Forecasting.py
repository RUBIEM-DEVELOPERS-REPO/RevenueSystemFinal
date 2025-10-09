import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from utils.database import get_transaction_data
from utils.forecasting import RevenueForecaster
from components.forecast_dashboard import show_forecast_dashboard
from components.forecast_analysis import show_forecast_analysis

st.set_page_config(page_title="Forecasting", layout="wide")
st.title("📊 Revenue Forecasting & Trends")

# Load data
transactions_df = get_transaction_data()

if not transactions_df.empty and 'created_at' in transactions_df.columns:
    # Convert to time series
    transactions_df['date'] = pd.to_datetime(transactions_df['created_at']).dt.date
    daily_revenue = transactions_df.groupby('date')['amount'].sum().sort_index()
    
    if len(daily_revenue) >= 7:  # Minimum data for forecasting
        # Forecasting parameters
        st.sidebar.header("Forecast Settings")
        periods = st.sidebar.slider("Forecast Periods (days)", 7, 90, 30)
        confidence_level = st.sidebar.slider("Confidence Level", 0.8, 0.99, 0.95)
        
        # Simple forecasting models
        dates_ordinal = pd.Series(daily_revenue.index).apply(lambda x: x.toordinal()).values
        revenue_values = daily_revenue.values
        
        # Linear regression forecast
        lr_model = LinearRegression()
        lr_model.fit(dates_ordinal.reshape(-1, 1), revenue_values)
        
        # Generate future dates
        last_date = dates_ordinal[-1]
        future_dates_ordinal = np.array([last_date + i for i in range(1, periods + 1)])
        future_dates = [pd.Timestamp.fromordinal(int(x)) for x in future_dates_ordinal]
        
        # Predictions
        lr_forecast = lr_model.predict(future_dates_ordinal.reshape(-1, 1))
        
        # Create forecast visualization
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=daily_revenue.index,
            y=daily_revenue.values,
            mode='lines+markers',
            name='Historical Revenue',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=lr_forecast,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="Revenue Forecast",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_forecast = lr_forecast.sum()
            st.metric("Total Forecasted", f"${total_forecast:,.0f}")
        
        with col2:
            avg_daily_forecast = lr_forecast.mean()
            st.metric("Avg Daily Forecast", f"${avg_daily_forecast:,.0f}")
        
        with col3:
            growth_rate = ((lr_forecast[-1] / lr_forecast[0]) - 1) * 100
            st.metric("Projected Growth", f"{growth_rate:+.1f}%")
        
        # Trend analysis
        st.subheader("Trend Analysis")
        
        # Moving averages
        daily_revenue_series = pd.Series(daily_revenue.values, index=daily_revenue.index)
        ma_7 = daily_revenue_series.rolling(window=7).mean()
        ma_30 = daily_revenue_series.rolling(window=30).mean()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=daily_revenue.index, y=daily_revenue.values, 
                                     name='Daily Revenue', line=dict(color='lightblue')))
        fig_trend.add_trace(go.Scatter(x=ma_7.index, y=ma_7.values, 
                                     name='7-Day MA', line=dict(color='blue')))
        fig_trend.add_trace(go.Scatter(x=ma_30.index, y=ma_30.values, 
                                     name='30-Day MA', line=dict(color='red')))
        
        fig_trend.update_layout(title="Revenue Trends with Moving Averages")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    else:
        st.warning("Insufficient data for forecasting. Need at least 7 days of data.")
else:
    st.info("No transaction data with dates available")

# Load data
transactions_df = get_transaction_data()

if transactions_df.empty:
    st.error("No transaction data available for forecasting")
else:
    # Initialize forecaster
    forecaster = RevenueForecaster()
    
    # Prepare data and generate forecasts
    with st.spinner("Generating revenue forecasts..."):
        forecast_results = forecaster.generate_forecast(transactions_df)
    
    # Show dashboard
    show_forecast_dashboard(forecast_results)
    
    # Show detailed analysis
    show_forecast_analysis(forecast_results)
