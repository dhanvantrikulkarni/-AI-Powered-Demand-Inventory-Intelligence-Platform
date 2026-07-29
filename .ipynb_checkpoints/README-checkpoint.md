# Project FORESIGHT – Demand & Inventory Intelligence

## Overview
A 4-week Data Science internship project building a complete demand forecasting and inventory risk prediction system for NorthBay Living.

## Problem Statement
NorthBay Living, an online shopping company with ~200 products (SKUs), faces two key challenges:
- **Stockouts**: Products become out of stock → customers cannot buy → lost revenue
- **Overstock**: Too much inventory → products remain in warehouse → capital blocked

## Solution
An AI system that provides:
- Weekly demand forecasts for all products
- Stockout risk predictions
- Overstock risk predictions
- Actionable recommendations (Reorder Now, Markdown/Clear, Watch, Healthy)

## Technologies
- **Language**: Python
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn, Prophet, LightGBM
- **Visualization**: Matplotlib, Plotly
- **Dashboard**: Streamlit
- **API**: FastAPI (optional)

## Project Structure
```
Project_FORESIGHT/
│
├── data/
│   ├── raw/              # Raw input datasets
│   │   ├── sales_daily.csv
│   │   ├── sku_master.csv
│   │   ├── calendar.csv
│   │   └── inventory_snapshots.csv
│   └── processed/        # Cleaned and processed data
│
├── notebooks/
│   ├── EDA.ipynb         # Exploratory Data Analysis
│   └── Forecast.ipynb    # Forecasting experiments
│
├── src/
│   ├── pipeline.py       # Data cleaning and processing
│   ├── forecast.py       # Demand forecasting models
│   └── risk.py           # Inventory risk prediction
│
├── app/
│   └── streamlit_app.py  # Streamlit dashboard
│
├── service/
│   └── api.py            # FastAPI service
│
├── reports/
│   ├── EDA_Report.pdf
│   └── Executive_Report.pdf
│
├── requirements.txt
├── README.md
└── main.py
```

## Data Sources
1. **sales_daily.csv**: Daily sales data (Date, SKU, Units Sold, Revenue, Price, Promotion)
2. **sku_master.csv**: Product information (SKU, Category, Cost, Price)
3. **calendar.csv**: Calendar data (Holidays, Seasons, Week, Month)
4. **inventory_snapshots.csv**: Inventory data (Current Stock, Ordered Stock, Lead Time, Reorder Point)

## Project Pipeline

### Step 1: Data Collection
Load and merge all four datasets

### Step 2: Data Cleaning
- Remove duplicates
- Fill missing values
- Convert date formats
- Merge all tables

### Step 3: Exploratory Data Analysis
- Best/worst selling products
- Seasonal trends
- Monthly sales patterns
- Category-wise sales
- Promotion impact

### Step 4: Feature Engineering
Create features:
- Day, Week, Month, Year
- Lag Sales
- Rolling Average
- Holiday indicators
- Promotion flags

### Step 5: Demand Forecasting
Build ML models (Random Forest, XGBoost, Prophet, LightGBM)
- Compare against seasonal-naive baseline
- Use rolling-origin backtesting
- Report WAPE (Weighted Absolute Percentage Error)

### Step 6: Risk Prediction
- **Stockout Risk**: If Forecast > Current Stock → High Risk
- **Overstock Risk**: If Current Stock >> Forecast → Overstock
- **Recommendations**: Reorder Now, Markdown/Clear, Watch, Healthy

### Step 7: Dashboard
Streamlit dashboard with:
- Sales Trend visualization
- Forecast display
- Risk Score
- Product Search
- Category Filter
- Action Recommendations

### Step 8: Deployment
- Deploy Streamlit app
- Deploy FastAPI service

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Project_FORESIGHT

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Data Pipeline
```bash
python main.py
```

### Run Streamlit Dashboard
```bash
streamlit run app/streamlit_app.py
```

### Run FastAPI Service
```bash
uvicorn service.api:app --reload
```

### Run Jupyter Notebooks
```bash
jupyter lab
```

## Model Evaluation
- **Metric**: WAPE (Weighted Absolute Percentage Error)
- **Baseline**: Seasonal-naive model
- **Validation**: Rolling-origin backtesting

## Dashboard Features
- **Sales Trend**: Historical sales visualization
- **Forecast**: Next week sales predictions
- **Risk Score**: Stockout and overstock risk indicators
- **Product Search**: Search by SKU or product name
- **Category Filter**: Filter by product category
- **Recommendations**: Actionable inventory recommendations

## Project Timeline (4 Weeks)
- **Week 1**: Data collection, cleaning, and EDA
- **Week 2**: Feature engineering and model development
- **Week 3**: Risk prediction and dashboard development
- **Week 4**: Testing, deployment, and documentation

## License
Copyright (c) 2025 Project Jupyter Contributors
