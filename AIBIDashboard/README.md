# Lease Portfolio Analytics - Databricks AI/BI Dashboard

This folder contains the Databricks AI/BI dashboard definition that mirrors the React Portfolio component visualizations. The dashboard provides comprehensive analytics for commercial real estate lease portfolios.

## Dashboard Pages

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

## File Structure

```
AIBIDashboard/
├── LeasePortfolioAnalytics.lvdash.json   # Main dashboard definition
├── README.md                              # This file
└── metric_views/                          # Databricks Metric View definitions
    ├── deploy_all_metrics.sql             # Single script to deploy all metric views
```

## Deployment Instructions

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

## Configuration

### Required Parameters

After importing, you need to configure the following parameters in the dashboard:

| Parameter | Description | Sample Value |
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

## Customization

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

## Differences from React App

| Feature | React App | AI/BI Dashboard |
|---------|-----------|-----------------|
| Map View | Interactive Leaflet map | Bar charts by city (need lat/long values for map visualization) |
| Real-time Updates | WebSocket/polling | Manual refresh or scheduled |
| Custom Styling | CSS/React components | Dashboard themes |

## Metric Views

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

## Related Documentation

- [Databricks AI/BI Dashboards](https://docs.databricks.com/en/dashboards/)
- [Databricks Metric Views](https://docs.databricks.com/en/metric-views/)
- [Dashboard REST API](https://docs.databricks.com/api/workspace/lakeview)
- [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/)

## Troubleshooting

### Dashboard Not Loading
- Verify warehouse is running and accessible
- Check catalog/schema permissions
- Ensure all required tables exist

### Empty Visualizations
- Run the SQL queries in `datasets/` folder manually to debug
- Check for NULL values in required columns
- Verify date ranges are appropriate
