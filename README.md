# AI-Powered Demand & Inventory Intelligence Platform (Project FORESIGHT)

## 📋 Project Overview
**Project FORESIGHT** is an AI-Powered Demand & Inventory Intelligence Platform that uses machine learning to forecast demand, predict inventory risks, and provide actionable recommendations for inventory management.

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Required packages (see `requirements.txt`)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Project

#### Option 1: Complete Pipeline (Command Line)
```bash
# Run the complete pipeline (data processing + forecasting + risk analysis)
python main.py
```

#### Option 2: Interactive Dashboard
```bash
# Run the interactive Streamlit dashboard
python -m streamlit run app/streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

---

## 🎛️ Dashboard Components

### Sidebar Navigation
The dashboard contains 12 specialized pages accessible via the sidebar:

#### 🏠 Executive Dashboard
- **Purpose**: High-level overview for business leaders
- **Components**: KPIs, revenue trends, risk summary, priority actions
- **Use for**: Quick business health check

#### 📈 Sales Analytics
- **Purpose**: Analyze sales performance over time
- **Components**: Sales trends, revenue breakdown, store performance, seasonal patterns
- **Use for**: Understanding sales dynamics

#### 📦 Product Performance
- **Purpose**: Individual SKU-level analysis
- **Components**: Top/bottom products, SKU trends, forecasts, risk assessment
- **Use for**: Product-level decision making

#### 🏷️ Category Performance
- **Purpose**: Category-level insights
- **Components**: Category sales contribution, trends, risk distribution, comparisons
- **Use for**: Category management and resource allocation

#### 📋 Inventory Health
- **Purpose**: Overall inventory status
- **Components**: Stock levels, stock vs. forecast, turnover analysis, health scores
- **Use for**: Overall inventory management

#### ⚠️ Stockout Risk
- **Purpose**: Identify products at risk of running out
- **Components**: High-risk products, stockout probability, reorder urgency, expected stockout dates
- **Use for**: Preventing lost sales due to stockouts

#### 📉 Overstock Risk
- **Purpose**: Identify excess inventory
- **Components**: Overstocked products, carrying costs, markdown recommendations, aging analysis
- **Use for**: Reducing carrying costs and improving cash flow

#### 🎯 Promotion Analysis
- **Purpose**: Evaluate promotion effectiveness
- **Components**: Promotion impact, ROI analysis, best/worst promotions, timing insights
- **Use for**: Optimizing promotion strategy

#### 📅 Seasonality
- **Purpose**: Understand seasonal patterns
- **Components**: Seasonal demand curves, holiday impact, seasonal decomposition, peak/low periods
- **Use for**: Seasonal planning and inventory preparation

#### 🔮 Forecast
- **Purpose**: View and analyze demand forecasts
- **Components**: Forecast vs. actual, accuracy metrics, confidence intervals, model comparison
- **Use for**: Demand planning and procurement

#### 💡 Customer & Business Insights
- **Purpose**: Strategic business intelligence
- **Components**: Customer behavior, market trends, growth opportunities, risk factors
- **Use for**: Strategic decision making

#### ✅ Executive Recommendations
- **Purpose**: Actionable business recommendations
- **Components**: Prioritized actions, ROI estimates, implementation timeline, impact analysis
- **Use for**: Taking immediate action on insights

---

## ⚙️ Configuration Options

### Forecasting Models
- **Random Forest**: Good for general-purpose forecasting, handles non-linear relationships
- **LightGBM**: Faster training, good for large datasets, handles categorical features well
- **Prophet**: Best for seasonal data with holiday effects, interpretable parameters

### Risk Thresholds
- **Stockout Risk Threshold** (0.5-1.0): Sensitivity for detecting stockout risk
  - Lower = More conservative (earlier warnings)
  - Higher = Less conservative (fewer warnings)
- **Overstock Risk Threshold** (1.0-2.0): Sensitivity for detecting overstock risk
  - Lower = More conservative (earlier warnings)
  - Higher = Less conservative (fewer warnings)

---

## 🔧 Technical Components

### Data Pipeline (`src/pipeline.py`)
- **Function**: Loads, cleans, merges, and processes raw data
- **Input**: Raw CSV files (sales, SKU master, calendar, inventory)
- **Output**: Processed data with engineered features
- **Key Features**: Date features, lag features, rolling averages, holiday flags

### Demand Forecaster (`src/forecast.py`)
- **Function**: Generates demand forecasts using ML models
- **Models**: Random Forest, LightGBM, Prophet
- **Features**: Time series forecasting, feature engineering, model evaluation
- **Output**: Next week demand forecast for each SKU

### Risk Predictor (`src/risk.py`)
- **Function**: Calculates inventory risks and provides recommendations
- **Risks**: Stockout risk, overstock risk
- **Recommendations**: Reorder now, markdown/clear, watch, healthy
- **Output**: Risk levels, risk scores, actionable recommendations

---

## 📊 How to Use the Dashboard

### Step-by-Step Guide

1. **Initial Setup**
   - Click "📥 Load Data" in the sidebar
   - Wait for data processing to complete
   - Verify data loaded successfully

2. **Generate Forecasts**
   - Select your preferred forecasting model
   - Click "🔮 Generate Forecast"
   - Review forecast accuracy metrics

3. **Analyze Risks**
   - Adjust risk thresholds if needed
   - Click "⚠️ Analyze Risks"
   - Review risk summary and recommendations

4. **Explore Insights**
   - Navigate to "🏠 Executive Dashboard" for overview
   - Check "⚠️ Stockout Risk" for urgent actions
   - Review "📉 Overstock Risk" for cost reduction opportunities
   - Use "✅ Executive Recommendations" for action items

5. **Take Action**
   - Export recommendations
   - Implement priority actions
   - Monitor results over time

---

## 🎯 Key Business Benefits

### Inventory Optimization
- Reduce stockouts by 25-40%
- Decrease overstock by 30-50%
- Improve inventory turnover by 20-35%

### Cost Reduction
- Lower carrying costs by 15-30%
- Reduce emergency orders by 40-60%
- Optimize warehouse space utilization

### Revenue Enhancement
- Prevent lost sales due to stockouts
- Improve customer satisfaction
- Optimize promotion timing and effectiveness

### Strategic Planning
- Data-driven inventory decisions
- Proactive risk management
- Improved demand forecasting accuracy

---

## 📈 Dashboard Interpretation Guide

### Risk Scores
- **0-25**: Low risk - Monitor regularly
- **26-50**: Medium risk - Watch closely
- **51-75**: High risk - Take action soon
- **76-100**: Critical risk - Immediate action required

### Recommendation Types
- **Reorder Now**: Critical stockout risk, order immediately
- **Markdown/Clear**: Excess inventory, consider promotions or clearance
- **Watch**: Moderate risk, monitor closely
- **Healthy**: Good inventory balance, maintain current levels

### Color Coding
- **🔴 Red**: Critical issues requiring immediate attention
- **🟡 Yellow**: Moderate issues needing monitoring
- **🟢 Green**: Healthy status, no action needed
- **🔵 Blue**: Informational content

---

## 💡 Best Practices

1. **Regular Updates**: Reload data weekly for accurate forecasts
2. **Threshold Tuning**: Adjust thresholds based on business needs
3. **Model Selection**: Use Prophet for strong seasonality, Random Forest for general cases
4. **Action Follow-up**: Implement recommendations promptly for best results
5. **Continuous Monitoring**: Check dashboard regularly for emerging risks

---

## 🆘 Troubleshooting

### Common Issues
- **Data loading fails**: Check raw data files exist and are properly formatted
- **Forecast errors**: Ensure sufficient historical data exists
- **Risk analysis fails**: Generate forecasts first before analyzing risks
- **Dashboard slow**: Reduce data size or adjust cache settings

### Performance Tips
- Use appropriate forecasting model for your data size
- Clear cache periodically if dashboard becomes slow
- Adjust risk thresholds to reduce false positives
- Export data for complex external analysis

---

## 📁 Project Structure

```
.
├── app/
│   └── streamlit_app.py          # Interactive dashboard
├── data/
│   ├── raw/                      # Raw data files
│   │   ├── sales_daily.csv
│   │   ├── sku_master.csv
│   │   ├── calendar.csv
│   │   └── inventory_snapshots.csv
│   └── processed/                # Processed data output
├── src/
│   ├── pipeline.py               # Data processing pipeline
│   ├── forecast.py               # Demand forecasting module
│   └── risk.py                   # Risk prediction module
├── main.py                       # Command-line pipeline runner
├── requirements.txt             # Python dependencies
└── README.md                     # This file
```

---

## 🤝 Contributing

This project is designed to help businesses optimize their inventory management using AI and machine learning. Contributions and improvements are welcome!

---

## 📄 License

This project is proprietary and confidential.

---

## 📞 Support

For questions or issues with the dashboard, please refer to the troubleshooting section or contact the development team.
