# FORESIGHT — Demand & Inventory Intelligence

FORESIGHT is a demand forecasting and inventory intelligence dashboard designed to turn historical demand, inventory, forecast, risk, and financial data into actionable business insights.

The project combines a data-processing and forecasting pipeline with an interactive Streamlit dashboard for executive-level monitoring and SKU-level analysis.

---

## Project Overview

Inventory decisions require more than looking at historical sales alone. FORESIGHT brings together:

- Historical demand analysis
- 4-week demand forecasting
- Inventory position and coverage
- Reorder-point analysis
- Inventory risk classification
- Recommended inventory actions
- Revenue and financial exposure
- SKU-level drill-down analysis

The goal is to provide a single workflow from **data → analysis → forecast → risk → financial impact → action**.

---

## Key Features

### Executive Overview
Provides a high-level operational snapshot through:

- 4-week forecast demand
- SKUs requiring reorder
- Potential revenue exposure
- Excess inventory value
- High / Critical risk SKUs
- Historical demand vs. 4-week forecast visualization
- Key business signals

### Demand & Forecast
Focuses specifically on forecast analysis:

- Historical demand metrics
- 4-week forecast metrics
- Forecast interpretation
- Top SKUs by forecast demand

### Inventory Health
Provides visibility into:

- Inventory value
- Stock coverage
- Reorder-point analysis
- Inventory position

### Risk & Actions
Summarizes:

- Risk distribution
- Reorder Now
- Markdown
- Watch
- Healthy
- Risky SKU details
- Recommended actions

### Financial Impact
Provides analysis of:

- Potential revenue exposure
- Gross-margin exposure
- Excess inventory value
- Reorder investment

### SKU Analysis
Allows users to select an individual SKU and inspect:

- Product and category information
- Risk level
- Current stock
- 4-week forecast
- Recommended action
- Historical demand
- Forecast demand
- Inventory position
- Coverage
- Reorder point
- Safety stock
- Lead time
- Inventory composition

---

## Dashboard Navigation

The application opens on the Home page and provides the following navigation:

1. Home
2. Executive Overview
3. Demand & Forecast
4. Inventory Health
5. Risk & Actions
6. Financial Impact
7. SKU Analysis

---

## How FORESIGHT Works

```text
Data
  ↓
Data Cleaning
  ↓
Exploratory Data Analysis
  ↓
Feature Engineering
  ↓
Demand Forecasting
  ↓
Forecast Validation
  ↓
Inventory Risk Analysis
  ↓
Decision Engine
  ↓
Interactive Dashboard
```

The dashboard presents the outputs of this pipeline in a business-oriented interface.

---

## Project Architecture

```text
FORESIGHT/
│
├── app.py
│
├── pages/
│   ├── home.py
│   ├── executive_overview.py
│   ├── demand_forecast.py
│   ├── inventory_health.py
│   ├── risk_actions.py
│   ├── financial_impact.py
│   └── sku_analysis.py
│
├── data/
│   └── Source datasets
│
├── processed/
│   └── Cleaned and model-generated datasets
│
├── inspect_data.py
├── clean_data.py
├── eda.py
├── feature_engineering.py
├── forecasting.py
├── forecast_4_week.py
├── forecast_validation.py
├── inventory_risk.py
├── decision_engine.py
│
├── requirements.txt
└── .gitignore
```

---

## Data Pipeline

The project processes multiple business datasets covering areas such as:

- Daily sales
- SKU master information
- Inventory snapshots
- Calendar information

The processing pipeline generates cleaned and analytical datasets used by the forecasting, risk, decision, and dashboard layers.

Key processed outputs include:

- `weekly_features.csv`
- `forecast_4_week.csv`
- `inventory_risk.csv`
- `decision_table.csv`
- cleaned sales, inventory, calendar, and SKU datasets

---

## Forecasting

FORESIGHT generates a four-week demand forecast at SKU level.

The forecasting workflow includes:

1. Historical demand preparation
2. Feature engineering
3. Forecast generation
4. Forecast validation
5. Four-week forecast output

Forecast outputs are then used downstream by the inventory-risk and decision-engine components.

---

## Inventory Risk & Decision Engine

Forecast demand is combined with inventory-related information to identify operational signals.

The decision workflow considers factors such as:

- Current stock
- On-order inventory
- Reorder point
- Safety stock
- Lead time
- Stock coverage
- Forecast demand
- Risk level

The resulting decision layer supports actions such as:

- **Reorder Now**
- **Markdown**
- **Watch**
- **Healthy**

These outputs are surfaced in both executive-level and SKU-level dashboard views.

---

## Financial Analysis

The dashboard translates inventory and demand signals into business-facing financial indicators, including:

- Potential revenue exposure
- Gross-margin exposure
- Excess inventory value
- Reorder investment

These measures provide financial context alongside operational inventory signals.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and modeling |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computation |
| Scikit-learn | Machine learning / forecasting workflow |
| Plotly | Interactive visualizations |
| Streamlit | Dashboard and application interface |

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FORESIGHT
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The Streamlit application will provide the local dashboard URL in the terminal.

---

## Project Submission

### Source Code
GitHub repository:

**TODO — add public GitHub URL**

### Live Deployment
Public dashboard:

**TODO — add deployment URL**

### Demo Video
**TODO — add demo video URL**

### Feedback Video
**TODO — add feedback video URL**

### Project Report
**TODO — add report link**

---

## Limitations

- Forecast quality depends on the historical data and features available to the model.
- Inventory recommendations depend on the accuracy and completeness of inventory, lead-time, reorder-point, and safety-stock inputs.
- Financial exposure figures are modelled estimates and should be interpreted within the assumptions of the underlying data.
- The dashboard is an analytical decision-support tool and does not replace operational review or business judgment.

---

## Future Improvements

Potential extensions include:

- Automated data refresh
- Additional forecasting models and model comparison
- Forecast confidence intervals
- Scenario-based demand planning
- Promotion and holiday impact modelling
- Automated alerts for critical inventory conditions
- More granular financial scenario analysis
- Cloud-hosted data pipelines and scheduled model retraining

---

## Conclusion

FORESIGHT connects demand forecasting with inventory and financial decision-making in a single interactive platform.

Instead of viewing sales, forecasts, inventory, risk, and financial exposure as separate analyses, the project combines them into one decision-support workflow that can be explored from executive level down to individual SKU level.
