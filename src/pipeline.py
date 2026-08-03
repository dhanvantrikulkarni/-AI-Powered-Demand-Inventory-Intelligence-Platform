"""
Data Pipeline Module
Handles data loading, cleaning, merging, and feature engineering
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPipeline:
    """Data processing pipeline for demand forecasting"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all raw datasets"""
        logger.info("Loading raw datasets...")
        
        sales = pd.read_csv(self.data_dir / "sales_daily.csv")
        sku_master = pd.read_csv(self.data_dir / "sku_master.csv")
        calendar = pd.read_csv(self.data_dir / "calendar.csv")
        inventory = pd.read_csv(self.data_dir / "inventory_snapshots.csv")
        
        logger.info(f"Sales data shape: {sales.shape}")
        logger.info(f"SKU master shape: {sku_master.shape}")
        logger.info(f"Calendar shape: {calendar.shape}")
        logger.info(f"Inventory shape: {inventory.shape}")
        
        return sales, sku_master, calendar, inventory
    
    def clean_sales(self, sales: pd.DataFrame) -> pd.DataFrame:
        """Clean sales data"""
        logger.info("Cleaning sales data...")
        
        # Remove duplicates
        sales = sales.drop_duplicates()
        
        # Rename columns to match expected format
        sales = sales.rename(columns={
            'date': 'Date',
            'store_id': 'Store_ID',
            'sku_id': 'SKU',
            'units_sold': 'Units Sold',
            'revenue': 'Revenue',
            'unit_price': 'Price',
            'promotion': 'Promotion'
        })
        
        # Convert date column
        sales['Date'] = pd.to_datetime(sales['Date'])
        
        # Fill missing values
        sales['Units Sold'] = sales['Units Sold'].fillna(0)
        sales['Revenue'] = sales['Revenue'].fillna(0)
        sales['Price'] = sales['Price'].fillna(sales['Price'].median())
        sales['Promotion'] = sales['Promotion'].fillna(0)
        
        return sales
    
    def clean_sku_master(self, sku_master: pd.DataFrame) -> pd.DataFrame:
        """Clean SKU master data"""
        logger.info("Cleaning SKU master data...")
        
        # Remove duplicates
        sku_master = sku_master.drop_duplicates()
        
        # Rename columns to match expected format
        sku_master = sku_master.rename(columns={
            'sku_id': 'SKU',
            'sku_name': 'SKU_Name',
            'category': 'Category',
            'subcategory': 'Subcategory',
            'unit_price': 'Price',
            'cost_price': 'Cost',
            'brand': 'Brand'
        })
        
        # Fill missing values
        sku_master['Category'] = sku_master['Category'].fillna('Unknown')
        sku_master['Cost'] = sku_master['Cost'].fillna(sku_master['Cost'].median())
        sku_master['Price'] = sku_master['Price'].fillna(sku_master['Price'].median())
        
        return sku_master
    
    def clean_calendar(self, calendar: pd.DataFrame) -> pd.DataFrame:
        """Clean calendar data"""
        logger.info("Cleaning calendar data...")
        
        # Remove duplicates
        calendar = calendar.drop_duplicates()
        
        # Rename columns to match expected format
        calendar = calendar.rename(columns={
            'date': 'Date',
            'week': 'Week',
            'month': 'Month',
            'season': 'Season',
            'holiday_flag': 'Holiday',
            'promotion_events': 'Promotion_Events'
        })
        
        # Convert date column
        calendar['Date'] = pd.to_datetime(calendar['Date'])
        
        # Fill missing values
        calendar['Holiday'] = calendar['Holiday'].fillna(0)
        calendar['Season'] = calendar['Season'].fillna('Regular')
        
        return calendar
    
    def clean_inventory(self, inventory: pd.DataFrame) -> pd.DataFrame:
        """Clean inventory data"""
        logger.info("Cleaning inventory data...")
        
        # Remove duplicates
        inventory = inventory.drop_duplicates()
        
        # Rename columns to match expected format
        inventory = inventory.rename(columns={
            'store_id': 'Store_ID',
            'sku_id': 'SKU',
            'stock_on_hand': 'Current Stock',
            'reorder_point': 'Reorder Point',
            'safety_stock': 'Safety Stock',
            'last_restock_date': 'Last Restock Date'
        })
        
        # Fill missing values
        inventory['Current Stock'] = inventory['Current Stock'].fillna(0)
        inventory['Reorder Point'] = inventory['Reorder Point'].fillna(inventory['Reorder Point'].median())
        
        # Calculate ordered stock and lead time if not present
        if 'Ordered Stock' not in inventory.columns:
            inventory['Ordered Stock'] = 0
        else:
            inventory['Ordered Stock'] = inventory['Ordered Stock'].fillna(0)
            
        if 'Lead Time' not in inventory.columns:
            inventory['Lead Time'] = 7  # Default lead time
        else:
            inventory['Lead Time'] = inventory['Lead Time'].fillna(7)
        
        return inventory
    
    def merge_data(self, sales: pd.DataFrame, sku_master: pd.DataFrame, 
                   calendar: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
        """Merge all datasets"""
        logger.info("Merging datasets...")
        
        # Merge sales with SKU master
        df = sales.merge(sku_master, on='SKU', how='left')
        
        # Merge with calendar
        df = df.merge(calendar, on='Date', how='left')
        
        # Merge with inventory
        df = df.merge(inventory, on='SKU', how='left')
        
        logger.info(f"Merged data shape: {df.shape}")
        
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features"""
        logger.info("Creating features...")
        
        # Date-based features
        df['Day'] = df['Date'].dt.day
        df['Week'] = df['Date'].dt.isocalendar().week.astype(int)
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
        
        # Lag features (grouped by SKU)
        df = df.sort_values(['SKU', 'Date'])
        df['Lag_1'] = df.groupby('SKU')['Units Sold'].shift(1)
        df['Lag_7'] = df.groupby('SKU')['Units Sold'].shift(7)
        
        # Rolling average features
        df['Rolling_Mean_7'] = df.groupby('SKU')['Units Sold'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['Rolling_Mean_14'] = df.groupby('SKU')['Units Sold'].transform(
            lambda x: x.rolling(window=14, min_periods=1).mean()
        )
        
        # Fill missing lag and rolling values
        df['Lag_1'] = df['Lag_1'].fillna(0)
        df['Lag_7'] = df['Lag_7'].fillna(0)
        df['Rolling_Mean_7'] = df['Rolling_Mean_7'].fillna(df['Units Sold'])
        df['Rolling_Mean_14'] = df['Rolling_Mean_14'].fillna(df['Units Sold'])
        
        # Holiday and promotion flags
        df['IsHoliday'] = df['Holiday'].fillna(0).astype(int)
        df['IsPromotion'] = df['Promotion'].fillna(0).astype(int)
        
        logger.info(f"Features created. Shape: {df.shape}")
        
        return df
    
    def run_pipeline(self) -> pd.DataFrame:
        """Run the complete data pipeline"""
        logger.info("Starting data pipeline...")
        
        # Load data
        sales, sku_master, calendar, inventory = self.load_data()
        
        # Clean data
        sales = self.clean_sales(sales)
        sku_master = self.clean_sku_master(sku_master)
        calendar = self.clean_calendar(calendar)
        inventory = self.clean_inventory(inventory)
        
        # Merge data
        df = self.merge_data(sales, sku_master, calendar, inventory)
        
        # Create features
        df = self.create_features(df)
        
        # Save processed data
        output_path = self.processed_dir / "processed_data.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to {output_path}")
        
        return df


def main():
    """Main function to run the pipeline"""
    pipeline = DataPipeline()
    df = pipeline.run_pipeline()
    print(f"Pipeline completed. Processed data shape: {df.shape}")
    return df


if __name__ == "__main__":
    main()
