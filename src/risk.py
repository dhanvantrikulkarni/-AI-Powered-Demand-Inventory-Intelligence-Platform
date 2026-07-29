"""
Inventory Risk Prediction Module
Calculates stockout and overstock risks with actionable recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskPredictor:
    """Predict inventory risks and provide recommendations"""
    
    def __init__(self, stockout_threshold: float = 0.8, overstock_threshold: float = 1.5):
        """
        Initialize risk predictor
        
        Args:
            stockout_threshold: Ratio of forecast to stock that triggers stockout risk
            overstock_threshold: Ratio of stock to forecast that triggers overstock risk
        """
        self.stockout_threshold = stockout_threshold
        self.overstock_threshold = overstock_threshold
    
    def calculate_stockout_risk(self, forecast: float, current_stock: float) -> str:
        """
        Calculate stockout risk level
        
        Args:
            forecast: Predicted demand
            current_stock: Current inventory level
        
        Returns:
            Risk level: 'High', 'Medium', 'Low', or 'None'
        """
        if current_stock == 0:
            return 'High'
        
        ratio = forecast / current_stock
        
        if ratio >= 1.0:
            return 'High'
        elif ratio >= self.stockout_threshold:
            return 'Medium'
        elif ratio >= 0.5:
            return 'Low'
        else:
            return 'None'
    
    def calculate_overstock_risk(self, forecast: float, current_stock: float) -> str:
        """
        Calculate overstock risk level
        
        Args:
            forecast: Predicted demand
            current_stock: Current inventory level
        
        Returns:
            Risk level: 'High', 'Medium', 'Low', or 'None'
        """
        if forecast == 0:
            return 'High' if current_stock > 0 else 'None'
        
        ratio = current_stock / forecast
        
        if ratio >= self.overstock_threshold:
            return 'High'
        elif ratio >= 1.2:
            return 'Medium'
        elif ratio >= 1.0:
            return 'Low'
        else:
            return 'None'
    
    def calculate_risk_score(self, forecast: float, current_stock: float) -> float:
        """
        Calculate overall risk score (0-100)
        
        Args:
            forecast: Predicted demand
            current_stock: Current inventory level
        
        Returns:
            Risk score between 0 and 100
        """
        stockout_risk = self.calculate_stockout_risk(forecast, current_stock)
        overstock_risk = self.calculate_overstock_risk(forecast, current_stock)
        
        risk_scores = {
            'High': 75,
            'Medium': 50,
            'Low': 25,
            'None': 0
        }
        
        # Return the higher of the two risks
        return max(risk_scores[stockout_risk], risk_scores[overstock_risk])
    
    def get_recommendation(self, forecast: float, current_stock: float, 
                          lead_time: float = 7, reorder_point: float = None) -> str:
        """
        Get actionable recommendation based on forecast and inventory
        
        Args:
            forecast: Predicted demand
            current_stock: Current inventory level
            lead_time: Lead time for reordering (days)
            reorder_point: Reorder point threshold
        
        Returns:
            Recommendation: 'Reorder Now', 'Markdown/Clear', 'Watch', or 'Healthy'
        """
        stockout_risk = self.calculate_stockout_risk(forecast, current_stock)
        overstock_risk = self.calculate_overstock_risk(forecast, current_stock)
        
        # Priority: Stockout risk first, then overstock
        if stockout_risk in ['High', 'Medium']:
            return 'Reorder Now'
        elif stockout_risk == 'Low':
            return 'Watch'
        elif overstock_risk == 'High':
            return 'Markdown/Clear'
        elif overstock_risk == 'Medium':
            return 'Watch'
        else:
            return 'Healthy'
    
    def predict_risks(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict risks for all SKUs
        
        Args:
            forecast_df: DataFrame with SKU, Current_Stock, Forecast columns
        
        Returns:
            DataFrame with additional risk columns
        """
        logger.info("Calculating inventory risks...")
        
        results = []
        
        for _, row in forecast_df.iterrows():
            sku = row['SKU']
            current_stock = row['Current_Stock']
            forecast = row['Forecast']
            lead_time = row.get('Lead Time', 7)
            reorder_point = row.get('Reorder Point', None)
            
            stockout_risk = self.calculate_stockout_risk(forecast, current_stock)
            overstock_risk = self.calculate_overstock_risk(forecast, current_stock)
            risk_score = self.calculate_risk_score(forecast, current_stock)
            recommendation = self.get_recommendation(
                forecast, current_stock, lead_time, reorder_point
            )
            
            results.append({
                'SKU': sku,
                'Current_Stock': current_stock,
                'Forecast': forecast,
                'Stockout_Risk': stockout_risk,
                'Overstock_Risk': overstock_risk,
                'Risk_Score': risk_score,
                'Recommendation': recommendation,
                'Category': row.get('Category', 'Unknown')
            })
        
        risk_df = pd.DataFrame(results)
        
        logger.info(f"Risk prediction completed for {len(risk_df)} SKUs")
        
        return risk_df
    
    def get_risk_summary(self, risk_df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of risks
        
        Args:
            risk_df: DataFrame with risk predictions
        
        Returns:
            Dictionary with risk summary statistics
        """
        summary = {
            'total_skus': len(risk_df),
            'high_stockout_risk': len(risk_df[risk_df['Stockout_Risk'] == 'High']),
            'medium_stockout_risk': len(risk_df[risk_df['Stockout_Risk'] == 'Medium']),
            'high_overstock_risk': len(risk_df[risk_df['Overstock_Risk'] == 'High']),
            'medium_overstock_risk': len(risk_df[risk_df['Overstock_Risk'] == 'Medium']),
            'reorder_now': len(risk_df[risk_df['Recommendation'] == 'Reorder Now']),
            'markdown_clear': len(risk_df[risk_df['Recommendation'] == 'Markdown/Clear']),
            'watch': len(risk_df[risk_df['Recommendation'] == 'Watch']),
            'healthy': len(risk_df[risk_df['Recommendation'] == 'Healthy']),
            'avg_risk_score': risk_df['Risk_Score'].mean()
        }
        
        return summary


def analyze_inventory_health(risk_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze overall inventory health by category
    
    Args:
        risk_df: DataFrame with risk predictions
    
    Returns:
        DataFrame with category-wise health metrics
    """
    logger.info("Analyzing inventory health by category...")
    
    category_health = risk_df.groupby('Category').agg({
        'SKU': 'count',
        'Risk_Score': 'mean',
        'Stockout_Risk': lambda x: (x == 'High').sum(),
        'Overstock_Risk': lambda x: (x == 'High').sum(),
        'Recommendation': lambda x: (x == 'Reorder Now').sum()
    }).rename(columns={
        'SKU': 'Total_SKUs',
        'Risk_Score': 'Avg_Risk_Score',
        'Stockout_Risk': 'High_Stockout_Risk_Count',
        'Overstock_Risk': 'High_Overstock_Risk_Count',
        'Recommendation': 'Reorder_Needed_Count'
    })
    
    return category_health


def get_priority_actions(risk_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get top priority actions based on risk scores
    
    Args:
        risk_df: DataFrame with risk predictions
        top_n: Number of top actions to return
    
    Returns:
        DataFrame with top priority actions
    """
    # Sort by risk score descending
    priority_actions = risk_df.sort_values('Risk_Score', ascending=False).head(top_n)
    
    return priority_actions[['SKU', 'Category', 'Current_Stock', 'Forecast', 
                            'Stockout_Risk', 'Overstock_Risk', 'Risk_Score', 
                            'Recommendation']]


def main():
    """Main function for testing"""
    # This would be used with actual data
    print("Risk prediction module loaded successfully")


if __name__ == "__main__":
    main()
