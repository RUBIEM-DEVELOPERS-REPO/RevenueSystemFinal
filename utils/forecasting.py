import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

class RevenueForecaster:
    """Revenue forecasting using ARIMA model"""
    
    def __init__(self, forecast_days=7):
        self.forecast_days = forecast_days
        self.model = None
    
    def generate_forecast(self, transactions_df):
        """Generate revenue forecast from transaction data"""
        
        # Prepare data
        processed_data = self._prepare_data(transactions_df)
        
        if processed_data.empty:
            return {"error": "Insufficient data for forecasting"}
        
        # Generate forecast
        forecast_result = self._generate_arima_forecast(processed_data)
        
        return forecast_result
    
    def _prepare_data(self, transactions_df):
        """Prepare data for forecasting"""
        
        if 'created_at' not in transactions_df.columns or 'amount' not in transactions_df.columns:
            return pd.DataFrame()
        
        # Convert and process dates
        transactions_df["created_at"] = pd.to_datetime(transactions_df["created_at"])
        transactions_df["date"] = transactions_df["created_at"].dt.date
        
        # Daily revenue aggregation
        daily_revenue = transactions_df.groupby("date").agg(
            total_revenue=("amount", "sum"),
            transaction_count=("amount", "count")
        ).reset_index()
        
        # Ensure we have enough data
        if len(daily_revenue) < 14:  # Minimum 2 weeks of data
            return pd.DataFrame()
        
        return daily_revenue
    
    def _generate_arima_forecast(self, daily_revenue):
        """Generate ARIMA forecast"""
        
        ts = daily_revenue.set_index("date")["total_revenue"]
        
        try:
            # Build ARIMA model (simple configuration)
            model = ARIMA(ts, order=(2, 1, 2))
            model_fit = model.fit()
            
            # Forecast next days
            forecast = model_fit.forecast(steps=self.forecast_days)
            
            # Create forecast dataframe
            forecast_df = pd.DataFrame({
                "date": pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), periods=self.forecast_days),
                "forecast_revenue": forecast
            })
            
            # Calculate model accuracy (using last 20% of data for validation)
            train_size = int(len(ts) * 0.8)
            if train_size > 0:
                train_data = ts[:train_size]
                test_data = ts[train_size:]
                
                # Retrain on training data
                model_train = ARIMA(train_data, order=(2, 1, 2))
                model_train_fit = model_train.fit()
                
                # Forecast test period
                test_forecast = model_train_fit.forecast(steps=len(test_data))
                
                # Calculate accuracy metrics
                mae = mean_absolute_error(test_data, test_forecast)
                accuracy = max(0, 100 - (mae / test_data.mean() * 100))
            else:
                accuracy = 0
            
            return {
                "historical_data": daily_revenue,
                "forecast_data": forecast_df,
                "model_accuracy": accuracy,
                "model_summary": model_fit.summary()
            }
            
        except Exception as e:
            return {"error": f"Forecasting failed: {str(e)}"}