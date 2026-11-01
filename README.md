# CustomerInsight AI — Customer Intelligence Platform

A production-quality Customer Intelligence & Predictive Analytics Platform that transforms raw transaction datasets into actionable customer segments, revenue forecasts, basket association rules, and executive business insights.

The platform combines robust statistical machine learning, empirical Bayesian recurrence modeling, multi-dataset workspace ingestion, and a grounded conversational AI data assistant.

---

## 🌟 Platform Capabilities

### 1. Multi-Dataset Workspace (`pages/data_workspace.py`)
- **Universal Ingestion**: Supports `.csv`, `.xlsx`, and `.xls` transaction uploads.
- **Smart Schema Detection**: Heuristically maps messy column headers to the canonical transaction schema (`order_id`, `customer_id`, `order_date`, `product_id`, `product_name`, `quantity`, `unit_price`, `currency`, `country`).
- **Data Quality & Cleaning Audit**: Configurable scrubbing rules (negative/zero quantity cancellation removal, unit price filtering, customer ID drop, deduplication).
- **High-Performance Storage**: Persists canonical records into columnar Parquet caches with SQLite metadata indexing for sub-second analytical queries across 400,000+ rows.

### 2. Generalised Customer & Revenue Analytics (`pages/revenue_analytics.py`, `customer_insights.py`)
- **Top-Line Financial KPIs**: Gross Revenue, Completed Orders, Average Order Value (AOV), Unique Customers, and Average Spend per Account.
- **Sales Momentum Timeline**: Aggregations across Daily, Weekly, and Monthly intervals with interactive Plotly visualisations.
- **Geographic Breakdown**: Country revenue rankings, order counts, and market share contributions.
- **Top Accounts Ranking**: Identifies top spending accounts with order counts, AOV, and CSV export.
- **RFM Segmentation**: Dynamic Recency, Frequency, Monetary calculations with K-Means, Agglomerative, and DBSCAN clustering.

### 3. Product & Market Basket Intelligence (`pages/product_intelligence.py`)
- **Bestseller Rankings**: Catalog item analysis sorted by Gross Revenue or Total Units Dispatched.
- **Long-Tail Inventory Audit**: Detects underperforming items to inform clearance or reordering.
- **Association Rules Engine**: Computes pairwise product co-occurrence frequencies across unique customer baskets to evaluate **Support**, **Confidence**, and **Lift** multipliers for cross-sell bundles.

### 4. Predictive CLV & Churn Intelligence (`pages/predictive_intelligence.py`)
- **Eligibility Validation**: Rigorously validates dataset history depth (>=45 days) and repeat purchase density (>=5%).
- **Empirical Bayesian Recurrence**: Models individual customer repeat purchase probability based on elapsed inactivity decay and personal transaction cadence.
- **Churn Risk Tiers**: Classifies accounts into Low Risk (Active), Medium Risk (Slowing), and High Risk (At-Risk / Lapsed).
- **90-Day Forward Spend Projection**: Applies Bayesian shrinkage to historical spend to project 90-day Customer Lifetime Value without extreme outlier distortion.

### 5. Grounded AI Data Assistant (`pages/ai_data_assistant.py`)
- **Natural Language Query Engine**: Answers stakeholder business questions directly in conversational English.
- **Zero Hallucination Guarantee**: Classifies intent and routes to strictly deterministic analytical functions in `TOOL_REGISTRY` (zero fabricated figures).
- **Enriched Responses**: Returns direct numerical answers, supporting KPI cards, tabular data, exact analysis period scope, and methodology caveats.

### 6. Strategic Business Insights Engine (`pages/business_insights_page.py`)
- **Automated Evidence-Backed Rules**: Evaluates Pareto revenue concentration (80/20 rule), high-value account lapse risk, single-order buyer retention opportunities, and basket cross-sell synergies.
- **Actionable Guidance**: Delivers prioritized recommendations with supporting evidence metrics.

### 7. Executive Brief & Data Export Center (`pages/reports_exports.py`)
- **Executive Summary Brief**: Generates a complete synthesized Markdown document ready for leadership presentation.
- **Structured CSV Exports**: One-click download for Enriched Customer Segments, Product Catalog Performance, Daily Revenue Trends, and Predictive CLV Scores.

### 8. Preserved Research Lab
- Retains all 6 original research notebooks, baseline algorithm comparisons, K-Means seed/subset/noise stability analysis, model validation studio, and research health evidence.

---

## 🚀 Quickstart & Installation

Python 3.11+ is required.

```powershell
# 1. Clone repository and navigate to root
cd customerinsight-ai

# 2. Set up virtual environment and install dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dashboard,dev]"

# 3. Launch UI via npm or streamlit
npm run dev
# OR
streamlit run app/main.py
```

The application opens at `http://localhost:8501`.

---

## 🧪 Testing & Verification

Run the comprehensive test suite (69 tests covering platform core, UI pages, and research benchmarks):

```powershell
pytest -q
```

All 69 unit and integration tests pass with 100% success rate.

---

## 📂 Repository Architecture

```text
customerinsight-ai/
├── app/
│   ├── main.py                     # Main navigation and sidebar dataset switcher
│   ├── dashboard_ui.py             # Shared presentation, styling, and active workspace state
│   ├── customer_insights.py        # Customer RFM behavior and cluster explorer
│   ├── pages/
│   │   ├── research_overview.py    # Main landing dashboard
│   │   ├── data_workspace.py       # Ingestion, schema mapping, and dataset management
│   │   ├── revenue_analytics.py    # Financial KPIs, sales trends, geographic breakdown
│   │   ├── product_intelligence.py # Catalog rankings and market basket association rules
│   │   ├── predictive_intelligence.py # Churn risk and 90-day CLV spend projections
│   │   ├── ai_data_assistant.py    # Grounded natural language assistant
│   │   ├── business_insights_page.py # Automated strategic business insights
│   │   ├── reports_exports.py      # Executive markdown briefs and CSV exports
│   │   ├── retail_data_explorer.py # Raw transaction audit (Research Lab)
│   │   ├── rfm_intelligence.py     # RFM feature distributions (Research Lab)
│   │   ├── research_findings.py    # Algorithm comparison and stability (Research Lab)
│   │   ├── model_validation_studio.py # Preprocessing & cluster count sensitivity (Research Lab)
│   │   └── research_health.py      # Research evidence integrity verification (Research Lab)
├── src/customerinsight/
│   ├── schema.py                   # Canonical schema and column auto-mapping
│   ├── cleaning.py                 # Data quality audit and sanitization
│   ├── datasets.py                 # Parquet storage engine and SQLite registry
│   ├── analytics.py                # Generalized RFM, KPIs, trends, top customers
│   ├── products.py                 # Catalog rankings and market basket rules
│   ├── prediction.py               # Empirical recurrence and CLV forecasting
│   ├── ai_assistant.py             # Grounded AI assistant tool registry
│   ├── insights_engine.py          # Evidence-backed business insights
│   └── reporting.py                # Executive brief markdown and CSV generator
├── tests/
│   ├── test_platform_core.py       # Unit tests for platform modules
│   ├── test_platform_ui.py         # Integration tests for new UI pages
│   └── test_dashboard_ui.py        # UI navigation and link verification
└── data/
    └── datasets/                   # Parquet cache and SQLite registry
```
