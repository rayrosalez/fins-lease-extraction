# Lease Portfolio Analytics - Databricks AI/BI Dashboard

This folder contains the Databricks AI/BI dashboard definition that mirrors the React Portfolio component visualizations. The dashboard provides comprehensive analytics for commercial real estate lease portfolios.

## 📊 Dashboard Pages

The dashboard includes the following tabs (pages), matching the React application:

| Page | Description |
|------|-------------|
| **Overview** | Portfolio KPIs, summary metrics, and recent extractions |
| **Risk Assessment** | Risk distribution charts, industry risk analysis, top risky leases |
| **Location Analysis** | Geographic distribution of properties (replaces Map View) |
| **All Leases** | Complete lease inventory table |
| **Market Summary** | Portfolio metrics by industry sector |
| **Landlords** | Landlord profiles with financial metrics and risk assessment |
| **Tenants** | Tenant profiles with financial metrics and growth indicators |
| **Glossary** | Definitions of key terms (PSF, WALT, Risk Score) |

## 📁 File Structure

```
AIBIDashboard/
├── LeasePortfolioAnalytics.lvdash.json   # Main dashboard definition
├── README.md                              # This file
├── datasets/                              # SQL query files for reference
│   ├── kpis.sql
│   ├── all_leases.sql
│   ├── risk_assessment.sql
│   ├── risk_distribution.sql
│   ├── market_summary.sql
│   ├── location_summary.sql
│   ├── landlords.sql
│   ├── landlords_summary.sql
│   ├── tenants.sql
│   ├── tenants_summary.sql
│   ├── tenants_by_industry.sql
│   └── tenants_by_size.sql
└── metric_views/                          # Databricks Metric View definitions
    ├── deploy_all_metrics.sql             # Single script to deploy all metric views
    ├── portfolio_lease_metrics.sql        # Core lease KPIs
    ├── risk_assessment_metrics.sql        # Risk scoring metrics
    ├── landlord_metrics.sql               # Landlord profile aggregates
    ├── tenant_metrics.sql                 # Tenant profile aggregates
    └── market_performance_metrics.sql     # Geographic & sector metrics
```

## 🚀 Deployment Instructions

### Option 1: Import via Databricks UI

1. Navigate to your Databricks workspace
2. Go to **Dashboards** in the left sidebar
3. Click **Create Dashboard** → **Import from file**
4. Select `LeasePortfolioAnalytics.lvdash.json`
5. Configure the dashboard parameters (see below)

### Option 2: Import via Workspace API

```bash
# Encode the dashboard file
CONTENT=$(base64 -i LeasePortfolioAnalytics.lvdash.json)

# Import via REST API
curl -X POST \
  "https://<your-workspace>.databricks.com/api/2.0/workspace/import" \
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/<your-email>/Dashboards/LeasePortfolioAnalytics.lvdash.json",
    "content": "'${CONTENT}'",
    "format": "AUTO"
  }'
```

### Option 3: Deploy via Databricks CLI

```bash
databricks workspace import \
  --file LeasePortfolioAnalytics.lvdash.json \
  --path /Users/<your-email>/Dashboards/LeasePortfolioAnalytics.lvdash.json \
  --format AUTO
```

## ⚙️ Configuration

### Required Parameters

After importing, you need to configure the following parameters in the dashboard:

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `${catalog}` | Unity Catalog name | `fins_team_3` |
| `${schema}` | Schema name | `lease_management` |

### Setting Parameters

1. Open the imported dashboard in edit mode
2. Click on the **Data** tab
3. For each dataset, update the SQL query to replace:
   - `${catalog}` with your actual catalog name (e.g., `fins_team_3`)
   - `${schema}` with your actual schema name (e.g., `lease_management`)

Alternatively, use Databricks dashboard parameters feature to make these configurable at runtime.

### Required Tables

Ensure the following tables exist in your Unity Catalog:

| Table | Description |
|-------|-------------|
| `silver_leases` | Validated lease records |
| `gold_lease_risk_scores` | Risk assessment view/table |
| `landlords` | Enriched landlord profiles |
| `tenants` | Enriched tenant profiles |

## 📈 Visualizations Included

### KPI Counters
- Total Leases
- Average Rent PSF
- Portfolio WALT (Weighted Average Lease Term)
- Average Risk Score
- Expiring in 12 Months
- Total Markets

### Charts
- **Pie Charts**: Risk distribution, company type distribution, square footage by market
- **Bar Charts**: Risk by category, risk by industry, leases by city, rent by market
- **Tables**: All leases, top risky leases, landlord profiles, tenant profiles

### Text Widgets
- Dashboard titles and descriptions
- Risk scoring methodology explanation
- Comprehensive glossary of CRE terms

## 🔗 Data Sources

The dashboard queries the following tables from Unity Catalog:

### Silver Layer
```sql
${catalog}.${schema}.silver_leases
```
Contains validated lease data with fields:
- `lease_id`, `tenant_name`, `property_id`
- `lease_start_date`, `lease_end_date`
- `base_rent_psf`, `square_footage`, `estimated_annual_rent`
- `industry_sector`, `property_city`, `property_state`

### Gold Layer
```sql
${catalog}.${schema}.gold_lease_risk_scores
```
Contains calculated risk scores with fields:
- `total_risk_score`, `rollover_score`, `escalation_risk_score`
- `concentration_risk_score`, `sector_risk_base`
- `lease_status`, `days_to_expiry`

### Entity Tables
```sql
${catalog}.${schema}.landlords
${catalog}.${schema}.tenants
```
Contains enriched company profiles with financial metrics.

## 🎨 Customization

### Modifying Visualizations

1. Open the dashboard in edit mode
2. Click on any widget to modify:
   - Chart type
   - Data fields
   - Colors and formatting
   - Titles and descriptions

### Adding New Pages

1. In edit mode, click **Add Page**
2. Drag widgets from the widget palette
3. Configure datasets and visualizations

### Using AI Assistance

Databricks AI/BI dashboards support AI-assisted chart creation:
1. Click **Add Widget** → **AI Generate**
2. Describe the visualization you want in natural language
3. Select the dataset to use
4. AI will generate the chart configuration

## 🔄 Differences from React App

| Feature | React App | AI/BI Dashboard |
|---------|-----------|-----------------|
| Map View | Interactive Leaflet map | Bar charts by city (maps not supported) |
| Real-time Updates | WebSocket/polling | Manual refresh or scheduled |
| Animations | Framer Motion | Native transitions |
| Custom Styling | CSS/React components | Dashboard themes |

## 📐 Metric Views

This dashboard includes reusable **Databricks Metric Views** for key aggregate calculations. Metric views provide centralized, governed metric definitions that can be used across dashboards, notebooks, and applications.

### Available Metric Views

| Metric View | Description | Key Measures |
|-------------|-------------|--------------|
| `portfolio_lease_metrics` | Core lease KPIs | total_leases, avg_rent_psf, expiring_90_days |
| `risk_assessment_metrics` | Risk scoring metrics | avg_risk_score, high_risk_rent, critical_lease_count |
| `landlord_metrics` | Landlord profiles | avg_health_score, total_revenue, low_risk_count |
| `tenant_metrics` | Tenant profiles | avg_revenue_growth, growing_companies, litigation_count |
| `market_performance_metrics` | Geographic metrics | walt_years, avg_rent_psf, total_annual_rent |

### Deploying Metric Views

Run the deployment script in a Databricks SQL editor or notebook:

```sql
-- Run the deployment script
%run ./metric_views/deploy_all_metrics.sql
```

Or deploy individually:
```sql
USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Create a single metric view
%run ./metric_views/portfolio_lease_metrics.sql
```

### Using Metric Views

Metric views use the `MEASURE()` function to aggregate measures:

```sql
-- Portfolio-wide totals
SELECT MEASURE(total_leases), MEASURE(total_annual_rent), MEASURE(avg_rent_psf)
FROM portfolio_lease_metrics;

-- By market dimension
SELECT market, MEASURE(total_leases), MEASURE(avg_rent_psf)
FROM portfolio_lease_metrics
GROUP BY market;

-- Risk by industry with filtering
SELECT industry_sector, MEASURE(avg_risk_score), MEASURE(total_rent_at_risk)
FROM risk_assessment_metrics
GROUP BY industry_sector
HAVING MEASURE(avg_risk_score) > 50;

-- Cross-dimensional analysis
SELECT market, city, MEASURE(lease_count), MEASURE(walt_years)
FROM market_performance_metrics
GROUP BY market, city
ORDER BY MEASURE(total_annual_rent) DESC
LIMIT 10;
```

### Benefits of Metric Views

- **Single Source of Truth**: Metric definitions are centralized
- **Consistent Calculations**: Same formulas across all consumers
- **Governed Access**: Unity Catalog permissions apply
- **AI/BI Integration**: Automatically available in dashboards
- **Genie Compatibility**: Works with natural language queries

## 📚 Related Documentation

- [Databricks AI/BI Dashboards](https://docs.databricks.com/en/dashboards/)
- [Databricks Metric Views](https://docs.databricks.com/en/metric-views/)
- [Dashboard REST API](https://docs.databricks.com/api/workspace/lakeview)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/)

## 🆘 Troubleshooting

### Dashboard Not Loading
- Verify warehouse is running and accessible
- Check catalog/schema permissions
- Ensure all required tables exist

### Empty Visualizations
- Run the SQL queries in `datasets/` folder manually to debug
- Check for NULL values in required columns
- Verify date ranges are appropriate

### Performance Issues
- Consider adding table optimizations (Z-ORDER, partitioning)
- Limit data in queries with WHERE clauses
- Use aggregations at query level rather than visualization level

---

*This dashboard was generated to match the React Portfolio component in `app/src/components/Portfolio.js`*
