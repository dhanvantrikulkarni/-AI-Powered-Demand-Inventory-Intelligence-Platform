"""
FastAPI Service for Project FORESIGHT
REST API for demand forecasting and inventory risk prediction
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pipeline import DataPipeline
from forecast import DemandForecaster, forecast_next_week
from risk import RiskPredictor, get_priority_actions, analyze_inventory_health

# Initialize FastAPI app
app = FastAPI(
    title="Project FORESIGHT API",
    description="Demand Forecasting and Inventory Risk Prediction API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for cached data
df = None
forecast_df = None
risk_df = None


# Pydantic models
class ForecastRequest(BaseModel):
    model_type: str = "random_forest"
    stockout_threshold: float = 0.8
    overstock_threshold: float = 1.5


class ForecastResponse(BaseModel):
    SKU: str
    Current_Stock: float
    Forecast: float
    Category: str
    Stockout_Risk: str
    Overstock_Risk: str
    Risk_Score: float
    Recommendation: str


class HealthResponse(BaseModel):
    status: str
    total_skus: int
    high_stockout_risk: int
    high_overstock_risk: int
    avg_risk_score: float


# Startup event
@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    global df
    try:
        pipeline = DataPipeline()
        df = pipeline.run_pipeline()
        print("Data loaded successfully on startup")
    except Exception as e:
        print(f"Error loading data on startup: {e}")


# Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Project FORESIGHT API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "API health check",
            "/load-data": "Load and process data",
            "/forecast": "Generate demand forecasts",
            "/risk": "Get inventory risks",
            "/recommendations": "Get action recommendations",
            "/sku/{sku}": "Get details for specific SKU",
            "/category/{category}": "Get category-wise analysis"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_loaded": df is not None
    }


@app.post("/load-data")
async def load_data():
    """Load and process data"""
    global df
    try:
        pipeline = DataPipeline()
        df = pipeline.run_pipeline()
        return {
            "status": "success",
            "message": "Data loaded successfully",
            "rows": len(df),
            "columns": len(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast", response_model=List[ForecastResponse])
async def generate_forecast(request: ForecastRequest):
    """Generate demand forecasts"""
    global df, forecast_df, risk_df
    
    if df is None:
        raise HTTPException(status_code=400, detail="Data not loaded. Call /load-data first.")
    
    try:
        # Generate forecast
        forecast_df = forecast_next_week(df, model_type=request.model_type)
        
        # Predict risks
        risk_predictor = RiskPredictor(
            stockout_threshold=request.stockout_threshold,
            overstock_threshold=request.overstock_threshold
        )
        risk_df = risk_predictor.predict_risks(forecast_df)
        
        # Convert to response format
        responses = []
        for _, row in risk_df.iterrows():
            responses.append(ForecastResponse(
                SKU=row['SKU'],
                Current_Stock=row['Current_Stock'],
                Forecast=row['Forecast'],
                Category=row['Category'],
                Stockout_Risk=row['Stockout_Risk'],
                Overstock_Risk=row['Overstock_Risk'],
                Risk_Score=row['Risk_Score'],
                Recommendation=row['Recommendation']
            ))
        
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk")
async def get_risk_summary():
    """Get risk summary statistics"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    risk_predictor = RiskPredictor()
    summary = risk_predictor.get_risk_summary(risk_df)
    
    return summary


@app.get("/recommendations")
async def get_recommendations(
    top_n: int = Query(10, ge=1, le=100, description="Number of top recommendations to return")
):
    """Get top priority recommendations"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    priority_actions = get_priority_actions(risk_df, top_n=top_n)
    
    return priority_actions.to_dict(orient='records')


@app.get("/sku/{sku}")
async def get_sku_details(sku: str):
    """Get details for a specific SKU"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    sku_data = risk_df[risk_df['SKU'] == sku]
    
    if sku_data.empty:
        raise HTTPException(status_code=404, detail=f"SKU {sku} not found")
    
    return sku_data.iloc[0].to_dict()


@app.get("/category/{category}")
async def get_category_analysis(category: str):
    """Get category-wise analysis"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    category_data = risk_df[risk_df['Category'] == category]
    
    if category_data.empty:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")
    
    category_health = analyze_inventory_health(risk_df)
    
    if category in category_health.index:
        return category_health.loc[category].to_dict()
    else:
        raise HTTPException(status_code=404, detail=f"Category {category} not found in health analysis")


@app.get("/categories")
async def get_all_categories():
    """Get all available categories"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    categories = risk_df['Category'].unique().tolist()
    
    return {"categories": categories}


@app.get("/skus")
async def get_all_skus(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of SKUs to return")
):
    """Get all SKUs with optional category filter"""
    global risk_df
    
    if risk_df is None:
        raise HTTPException(status_code=400, detail="Forecast not generated. Call /forecast first.")
    
    filtered_df = risk_df.copy()
    
    if category:
        filtered_df = filtered_df[filtered_df['Category'] == category]
    
    skus = filtered_df.head(limit)[['SKU', 'Category', 'Current_Stock', 'Forecast', 'Recommendation']]
    
    return skus.to_dict(orient='records')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
