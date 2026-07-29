"""
Main Entry Point for Project FORESIGHT
Orchestrates the complete pipeline from data loading to risk prediction
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from pipeline import DataPipeline
from forecast import DemandForecaster, forecast_next_week
from risk import RiskPredictor, get_priority_actions, analyze_inventory_health
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_complete_pipeline(
    model_type: str = "random_forest",
    stockout_threshold: float = 0.8,
    overstock_threshold: float = 1.5
):
    """
    Run the complete pipeline from data loading to risk prediction
    
    Args:
        model_type: Type of forecasting model to use
        stockout_threshold: Threshold for stockout risk
        overstock_threshold: Threshold for overstock risk
    
    Returns:
        Tuple of (processed_data, forecast_df, risk_df)
    """
    logger.info("=" * 60)
    logger.info("Starting Project FORESIGHT Pipeline")
    logger.info("=" * 60)
    
    # Step 1: Data Pipeline
    logger.info("\n[Step 1/4] Running Data Pipeline...")
    pipeline = DataPipeline()
    df = pipeline.run_pipeline()
    logger.info(f"Data pipeline completed. Processed {len(df)} rows")
    
    # Step 2: Demand Forecasting
    logger.info(f"\n[Step 2/4] Generating Forecasts using {model_type}...")
    forecast_df = forecast_next_week(df, model_type=model_type)
    logger.info(f"Forecasting completed for {len(forecast_df)} SKUs")
    
    # Step 3: Risk Prediction
    logger.info("\n[Step 3/4] Predicting Inventory Risks...")
    risk_predictor = RiskPredictor(
        stockout_threshold=stockout_threshold,
        overstock_threshold=overstock_threshold
    )
    risk_df = risk_predictor.predict_risks(forecast_df)
    logger.info("Risk prediction completed")
    
    # Step 4: Generate Summary
    logger.info("\n[Step 4/4] Generating Summary Report...")
    summary = risk_predictor.get_risk_summary(risk_df)
    
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total SKUs: {summary['total_skus']}")
    logger.info(f"High Stockout Risk: {summary['high_stockout_risk']} ({summary['high_stockout_risk']/summary['total_skus']*100:.1f}%)")
    logger.info(f"High Overstock Risk: {summary['high_overstock_risk']} ({summary['high_overstock_risk']/summary['total_skus']*100:.1f}%)")
    logger.info(f"Reorder Now: {summary['reorder_now']}")
    logger.info(f"Markdown/Clear: {summary['markdown_clear']}")
    logger.info(f"Watch: {summary['watch']}")
    logger.info(f"Healthy: {summary['healthy']}")
    logger.info(f"Average Risk Score: {summary['avg_risk_score']:.1f}")
    logger.info("=" * 60)
    
    # Save results
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    forecast_df.to_csv(output_dir / "forecasts.csv", index=False)
    risk_df.to_csv(output_dir / "risks.csv", index=False)
    
    logger.info(f"\nResults saved to {output_dir}")
    logger.info("- forecasts.csv")
    logger.info("- risks.csv")
    
    return df, forecast_df, risk_df


def print_top_actions(risk_df: pd.DataFrame, top_n: int = 10):
    """Print top priority actions"""
    logger.info(f"\nTop {top_n} Priority Actions:")
    logger.info("-" * 100)
    
    priority_actions = get_priority_actions(risk_df, top_n=top_n)
    
    for _, row in priority_actions.iterrows():
        logger.info(
            f"SKU: {row['SKU']:<15} | "
            f"Category: {row['Category']:<15} | "
            f"Stock: {int(row['Current_Stock']):<6} | "
            f"Forecast: {row['Forecast']:<6.1f} | "
            f"Risk Score: {row['Risk_Score']:<5.1f} | "
            f"Action: {row['Recommendation']}"
        )


def print_category_health(risk_df: pd.DataFrame):
    """Print category-wise health analysis"""
    logger.info("\nCategory-wise Inventory Health:")
    logger.info("-" * 100)
    
    category_health = analyze_inventory_health(risk_df)
    
    logger.info(f"{'Category':<20} | {'Total SKUs':<12} | {'Avg Risk Score':<15} | {'High Stockout':<15} | {'High Overstock':<15}")
    logger.info("-" * 100)
    
    for category, row in category_health.iterrows():
        logger.info(
            f"{category:<20} | "
            f"{int(row['Total_SKUs']):<12} | "
            f"{row['Avg_Risk_Score']:<15.1f} | "
            f"{int(row['High_Stockout_Risk_Count']):<15} | "
            f"{int(row['High_Overstock_Risk_Count']):<15}"
        )


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Project FORESIGHT - Demand & Inventory Intelligence")
    parser.add_argument(
        "--model",
        type=str,
        default="random_forest",
        choices=["random_forest", "lightgbm", "prophet"],
        help="Forecasting model to use"
    )
    parser.add_argument(
        "--stockout-threshold",
        type=float,
        default=0.8,
        help="Stockout risk threshold (0.5-1.0)"
    )
    parser.add_argument(
        "--overstock-threshold",
        type=float,
        default=1.5,
        help="Overstock risk threshold (1.0-2.0)"
    )
    parser.add_argument(
        "--top-actions",
        type=int,
        default=10,
        help="Number of top priority actions to display"
    )
    
    args = parser.parse_args()
    
    try:
        # Run complete pipeline
        df, forecast_df, risk_df = run_complete_pipeline(
            model_type=args.model,
            stockout_threshold=args.stockout_threshold,
            overstock_threshold=args.overstock_threshold
        )
        
        # Print additional insights
        print_top_actions(risk_df, top_n=args.top_actions)
        print_category_health(risk_df)
        
        logger.info("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
