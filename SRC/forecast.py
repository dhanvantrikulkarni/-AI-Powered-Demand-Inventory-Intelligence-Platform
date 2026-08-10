"""
Demand Forecasting Module
Handles demand forecasting using multiple ML models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import joblib

# Try to import optional models
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available. Install with: pip install prophet")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logging.warning("LightGBM not available. Install with: pip install lightgbm")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemandForecaster:
    """Demand forecasting using multiple ML models"""
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize forecaster
        
        Args:
            model_type: Type of model ('random_forest', 'lightgbm', 'prophet')
        """
        self.model_type = model_type
        self.model = None
        self.feature_cols = None
        self.target_col = 'Units Sold'
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for training"""
        logger.info("Preparing features...")
        
        # Define feature columns
        feature_cols = [
            'Day', 'Week', 'Month', 'Year', 'DayOfWeek', 'IsWeekend',
            'Lag_1', 'Lag_7', 'Rolling_Mean_7', 'Rolling_Mean_14',
            'IsHoliday', 'IsPromotion', 'Price', 'Cost'
        ]
        
        # Filter available columns
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_cols = available_cols
        
        X = df[available_cols].copy()
        y = df[self.target_col].copy()
        
        # Fill missing values
        X = X.fillna(0)
        y = y.fillna(0)
        
        logger.info(f"Features prepared. X shape: {X.shape}, y shape: {y.shape}")
        
        return X, y
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
        """Train Random Forest model"""
        logger.info("Training Random Forest model...")
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X, y)
        
        return model
    
    def train_lightgbm(self, X: pd.DataFrame, y: pd.Series) -> lgb.LGBMRegressor:
        """Train LightGBM model"""
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM not available")
        
        logger.info("Training LightGBM model...")
        
        model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            verbose=-1
        )
        model.fit(X, y)
        
        return model
    
    def train_prophet(self, df: pd.DataFrame) -> Prophet:
        """Train Prophet model"""
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not available")
        
        logger.info("Training Prophet model...")
        
        # Prepare data for Prophet
        prophet_df = df[['Date', 'Units Sold']].copy()
        prophet_df.columns = ['ds', 'y']
        
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.fit(prophet_df)
        
        return model
    
    def train(self, df: pd.DataFrame):
        """Train the forecasting model"""
        logger.info(f"Training {self.model_type} model...")
        
        if self.model_type == "prophet":
            self.model = self.train_prophet(df)
        else:
            X, y = self.prepare_features(df)
            
            if self.model_type == "random_forest":
                self.model = self.train_random_forest(X, y)
            elif self.model_type == "lightgbm":
                self.model = self.train_lightgbm(X, y)
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
        
        logger.info("Model training completed")
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if self.model_type == "prophet":
            # Prepare future dates for Prophet
            future = self.model.make_future_dataframe(periods=7)
            forecast = self.model.predict(future)
            predictions = forecast['yhat'].tail(len(df)).values
        else:
            X, _ = self.prepare_features(df)
            predictions = self.model.predict(X)
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def calculate_wape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Weighted Absolute Percentage Error"""
        wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100
        return wape
    
    def seasonal_naive_baseline(self, df: pd.DataFrame, forecast_horizon: int = 7) -> np.ndarray:
        """Seasonal naive baseline (use same period from previous week)"""
        logger.info("Calculating seasonal naive baseline...")
        
        predictions = []
        for sku in df['SKU'].unique():
            sku_data = df[df['SKU'] == sku].sort_values('Date')
            last_week_sales = sku_data.tail(7)['Units Sold'].values
            predictions.extend(last_week_sales)
        
        return np.array(predictions[:forecast_horizon])
    
    def rolling_origin_backtest(self, df: pd.DataFrame, n_splits: int = 5) -> Dict:
        """Perform rolling-origin backtesting"""
        logger.info("Performing rolling-origin backtesting...")
        
        results = {
            'model_wape': [],
            'baseline_wape': [],
            'improvement': []
        }
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        for train_idx, test_idx in tscv.split(df):
            train_df = df.iloc[train_idx]
            test_df = df.iloc[test_idx]
            
            # Train model
            self.train(train_df)
            
            # Make predictions
            predictions = self.predict(test_df)
            actuals = test_df[self.target_col].values
            
            # Calculate WAPE
            model_wape = self.calculate_wape(actuals, predictions)
            baseline_pred = self.seasonal_naive_baseline(train_df, len(test_df))
            baseline_wape = self.calculate_wape(actuals, baseline_pred)
            
            improvement = ((baseline_wape - model_wape) / baseline_wape) * 100
            
            results['model_wape'].append(model_wape)
            results['baseline_wape'].append(baseline_wape)
            results['improvement'].append(improvement)
        
        # Calculate average metrics
        avg_results = {
            'avg_model_wape': np.mean(results['model_wape']),
            'avg_baseline_wape': np.mean(results['baseline_wape']),
            'avg_improvement': np.mean(results['improvement'])
        }
        
        logger.info(f"Backtesting completed. Model WAPE: {avg_results['avg_model_wape']:.2f}%, "
                   f"Baseline WAPE: {avg_results['avg_baseline_wape']:.2f}%, "
                   f"Improvement: {avg_results['avg_improvement']:.2f}%")
        
        return avg_results
    
    def save_model(self, path: str):
        """Save trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model"""
        self.model = joblib.load(path)
        logger.info(f"Model loaded from {path}")


def forecast_next_week(df: pd.DataFrame, model_type: str = "random_forest") -> pd.DataFrame:
    """
    Forecast next week's demand for all SKUs
    
    Args:
        df: Processed data with features
        model_type: Type of model to use
    
    Returns:
        DataFrame with SKU, current_stock, forecast, and risk indicators
    """
    logger.info("Forecasting next week's demand...")
    
    # Get unique SKUs
    skus = df['SKU'].unique()
    
    # Train model on all data
    forecaster = DemandForecaster(model_type=model_type)
    forecaster.train(df)
    
    # Prepare forecast results
    forecasts = []
    
    for sku in skus:
        sku_data = df[df['SKU'] == sku].copy()
        
        # Get current stock
        current_stock = sku_data['Current Stock'].iloc[-1] if 'Current Stock' in sku_data.columns else 0
        
        # Get recent data for prediction
        recent_data = sku_data.tail(1).copy()
        
        # Make prediction
        prediction = forecaster.predict(recent_data)[0]
        
        forecasts.append({
            'SKU': sku,
            'Current_Stock': current_stock,
            'Forecast': prediction,
            'Category': sku_data['Category'].iloc[-1] if 'Category' in sku_data.columns else 'Unknown'
        })
    
    forecast_df = pd.DataFrame(forecasts)
    
    logger.info(f"Forecast completed for {len(skus)} SKUs")
    
    return forecast_df


def main():
    """Main function for testing"""
    # This would be used with actual data
    print("Forecast module loaded successfully")
    print(f"Prophet available: {PROPHET_AVAILABLE}")
    print(f"LightGBM available: {LIGHTGBM_AVAILABLE}")


if __name__ == "__main__":
    main()
