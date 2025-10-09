import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_forecast_dashboard(forecast_results):
    """Display revenue forecasting dashboard"""
    
    st.subheader("📊 Daily Revenue Overview")
    
    # Show historical data chart
    show_revenue_chart(forecast_results)
    
    # Show forecast
    show_forecast_chart(forecast_results)
    
    # Key metrics
    show_forecast_metrics(forecast_results)

def show_revenue_chart(forecast_results):
    """Display historical revenue chart"""
    
    if 'historical_data' in forecast_results:
        historical_df = forecast_results['historical_data']
        
        fig = px.line(
            historical_df,
            x='date',
            y='total_revenue',
            title="Historical Daily Revenue",
            labels={'total_revenue': 'Revenue ($)', 'date': 'Date'}
        )
        
        # Add transaction count if available
        if 'transaction_count' in historical_df.columns:
            fig.add_bar(
                x=historical_df['date'],
                y=historical_df['transaction_count'],
                name='Transaction Count',
                yaxis='y2',
                opacity=0.3
            )
            
            fig.update_layout(
                yaxis2=dict(
                    title='Transaction Count',
                    overlaying='y',
                    side='right'
                )
            )
        
        st.plotly_chart(fig, use_container_width=True)

def show_forecast_chart(forecast_results):
    """Display forecast chart with historical data"""
    
    if 'historical_data' in forecast_results and 'forecast_data' in forecast_results:
        historical_df = forecast_results['historical_data']
        forecast_df = forecast_results['forecast_data']
        
        # Create combined chart
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_df['date'],
            y=historical_df['total_revenue'],
            mode='lines+markers',
            name='Historical Revenue',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast data
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['forecast_revenue'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Confidence interval if available
        if 'confidence_lower' in forecast_df.columns and 'confidence_upper' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
                y=forecast_df['confidence_upper'].tolist() + forecast_df['confidence_lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval'
            ))
        
        fig.update_layout(
            title="Revenue Forecast with Historical Data",
            xaxis_title="Date",
            yaxis_title="Revenue ($)"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_forecast_metrics(forecast_results):
    """Display key forecast metrics"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'historical_data' in forecast_results:
            total_historical = forecast_results['historical_data']['total_revenue'].sum()
            st.metric("Total Historical Revenue", f"${total_historical:,.2f}")
    
    with col2:
        if 'forecast_data' in forecast_results:
            total_forecast = forecast_results['forecast_data']['forecast_revenue'].sum()
            st.metric("Total Forecast Revenue", f"${total_forecast:,.2f}")
    
    with col3:
        if 'historical_data' in forecast_results and 'forecast_data' in forecast_results:
            historical_avg = forecast_results['historical_data']['total_revenue'].mean()
            forecast_avg = forecast_results['forecast_data']['forecast_revenue'].mean()
            growth = ((forecast_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
            st.metric("Avg Daily Growth", f"{growth:+.1f}%")
    
    with col4:
        if 'model_accuracy' in forecast_results:
            accuracy = forecast_results['model_accuracy']
            st.metric("Model Accuracy", f"{accuracy:.1f}%")