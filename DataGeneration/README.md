# Synthetic Data Generation with Full Enrichment

Generate comprehensive synthetic lease data with full tenant and landlord enrichment to demonstrate the complete risk scoring ecosystem.

## Overview

This data generator creates a fully populated lease management system with:
- **Silver Layer Leases** with tenant_id and landlord_id references
- **Tenant Enrichment Table** with financial health scores, credit ratings, bankruptcy risk
- **Landlord Enrichment Table** with REIT profiles, financial metrics, portfolio data

The generated data demonstrates all 4 risk models:
- ✅ **FULLY_ENRICHED** - Leases with both tenant and landlord enrichment
- ✅ **TENANT_ENRICHED** - Leases with tenant enrichment only
- ✅ **LANDLORD_ENRICHED** - Leases with landlord enrichment only
- ✅ **BASIC** - Leases without enrichment (fallback model)

## Features

### Realistic Data Generation
- **20 Major REITs** - Blackstone, Brookfield, Boston Properties, etc.
- **Varied Industries** - Technology, Healthcare, Finance, Retail (16 sectors)
- **12 Major Markets** - SF, NYC, Boston, Austin, etc. with market-specific rents
- **Intelligent Correlations**:
  - Larger companies → higher health scores
  - High-risk industries (Retail, Restaurant) → lower financial health
  - REITs → stronger credit ratings and lower bankruptcy risk

### Tenant Enrichment
Each tenant gets:
- Financial health score (1-10) based on industry and company size
- Credit rating (AAA to B) correlated with health score
- Bankruptcy risk (LOW/MEDIUM/HIGH) based on financials
- Industry risk assessment
- Revenue, profit margins, employee count
- Payment history scores
- Market cap (if public company)
- Years in business, locations count

### Landlord Enrichment
Each landlord (REIT/property company) gets:
- Financial health score (typically 7-9.5 for REITs)
- Credit rating (usually A to AAA range)
- Total assets, market cap, annual revenue
- Debt-to-equity ratios (realistic for REITs)
- Portfolio size (properties, total sq ft)
- Property type focus (Office, Retail, Industrial, etc.)
- Geographic focus (markets served)
- Low bankruptcy risk profiles

### Smart Lease Generation
- Date ranges: Last 8 years through next 10 years
- Varied lease terms: 3, 5, 7, and 10 years
- Market-appropriate rents (SF: $55-95/sqft, Phoenix: $24-40/sqft)
- Escalation clauses (0-4% annually)
- Property locations with full addresses
- Suite numbers and lease types

## Quick Start

### 1. Setup Environment

```bash
cd DataGeneration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Databricks

Create `.env` file:
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token-here
```

### 3. Ensure Tables Exist

Run these SQL scripts in Databricks first:
1. `DatabricksResources/CreateTenantTable.sql`
2. `DatabricksResources/CreateLandlordTable.sql`
3. `DatabricksResources/CreateSilverTable.sql` (updated version with tenant_id/landlord_id)
4. `DatabricksResources/CreateGoldTable.sql` (enhanced risk model)

### 4. Generate Data

```bash
python generate_enriched_data.py
```

You'll be prompted for:
- **Number of leases**: Recommended 50-200 for demo
- **Enrichment rate**: 0.5-1.0 (0.8 = 80% enriched, 20% basic)

### 5. Verify Results

Check in Databricks:

```sql
-- Check landlords
SELECT COUNT(*), AVG(financial_health_score), AVG(debt_to_equity_ratio)
FROM fins_team_3.lease_management.landlords;

-- Check tenants
SELECT bankruptcy_risk, COUNT(*) 
FROM fins_team_3.lease_management.tenants
GROUP BY bankruptcy_risk;

-- Check leases with enrichment
SELECT risk_model_used, COUNT(*), AVG(total_risk_score)
FROM fins_team_3.lease_management.gold_lease_risk_scores
GROUP BY risk_model_used;
```

## What Gets Generated

### Example: 100 Leases with 80% Enrichment

**Tables Populated:**
- `landlords`: 20 records (all major REITs)
- `tenants`: ~70 records (unique companies across leases)
- `silver_leases`: 100 records with tenant_id and landlord_id

**Risk Model Distribution:**
- FULLY_ENRICHED: ~64 leases (both tenant & landlord enriched)
- TENANT_ENRICHED: ~16 leases (tenant only)
- BASIC: ~20 leases (no enrichment - demonstrates fallback)

### Sample Tenant Profile

```
Tenant: Quantum Data Solutions Inc
─────────────────────────────────────
Health Score: 8.2/10
Credit Rating: A+
Bankruptcy Risk: LOW
Industry Risk: MEDIUM (Technology)
Annual Revenue: $245M
Employees: 1,200
Payment History: 87/100
Market Cap: $1.8B (Public)
Founded: 2008
Locations: 12
```

### Sample Landlord Profile

```
Landlord: Boston Properties (BXP)
──────────────────────────────────────
Health Score: 8.9/10
Credit Rating: AA
Bankruptcy Risk: LOW
Total Assets: $28.5B
Market Cap: $15.2B
Portfolio: 187 properties
Total Sq Ft: 32.4M
Property Types: Office, Life Science
Geographic Focus: Gateway Cities
Debt/Equity: 0.68
```

## Data Quality Features

### Realistic Correlations
1. **Size → Health**: Larger companies (more employees, higher revenue) get better health scores
2. **Industry → Risk**: Retail/Restaurant sectors get higher risk assessments than Healthcare/Finance
3. **Health → Credit**: Health score directly influences credit rating
4. **Credit → Bankruptcy**: Lower credit ratings correlate with higher bankruptcy risk
5. **REITs → Stability**: All landlords (REITs) have strong financial profiles

### Variance for Testing
- **10-15% Poor Health** (scores 1-4): Tests high-risk scenarios
- **40-50% Moderate Health** (scores 4-7): Tests mixed portfolios  
- **35-45% Good Health** (scores 7-10): Tests low-risk scenarios

### Edge Cases Included
- Small companies with high growth (startups)
- Large companies with low margins (retail chains)
- Negative revenue growth scenarios
- High debt/equity ratios
- Litigation flags (10% of tenants)
- Private vs public companies
- Subsidiaries with parent companies

## Customization

### Adjust Company Size Mix

Edit in `generate_enriched_data.py`:
```python
size_tier = random.choices(
    ["enterprise", "mid", "small"],
    weights=[0.3, 0.4, 0.3]  # Adjust these weights
)[0]
```

### Change Risk Distribution

Modify industry risk levels:
```python
INDUSTRY_RISK = {
    "Retail": "HIGH",      # Change to "MEDIUM"
    "Restaurant": "HIGH",   # to reduce risk
    # ...
}
```

### Add More Landlords

Extend `LANDLORD_PROFILES`:
```python
LANDLORD_PROFILES = [
    {"name": "Your REIT Name", "type": "REIT", "ticker": "REIT"},
    # ...
]
```

## Troubleshooting

### "Table not found" Error

Solution: Run the table creation scripts first:
```sql
-- In Databricks SQL Editor
USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Run CreateTenantTable.sql
-- Run CreateLandlordTable.sql  
-- Run CreateSilverTable.sql (updated version)
```

### "Warehouse not found" Error

Solution: Update `WAREHOUSE_ID` in the script:
```python
WAREHOUSE_ID = "your-warehouse-id-here"
```

Find it in Databricks: SQL Warehouses → Your Warehouse → Connection Details

### Slow Insert Performance

Solution: Reduce batch size or use smaller datasets for testing:
```bash
python generate_enriched_data.py
# Enter: 50 leases (instead of 200)
```

### "Column not found: tenant_id"

Solution: You need the updated silver table schema. Run:
```sql
-- Drop and recreate with new schema
DROP TABLE IF EXISTS silver_leases;
-- Then run updated CreateSilverTable.sql
```

## Performance

| Leases | Tenants | Landlords | Time | DB Size |
|--------|---------|-----------|------|---------|
| 50     | ~35     | 20        | 30s  | 5KB     |
| 100    | ~70     | 20        | 1min | 10KB    |
| 200    | ~140    | 20        | 2min | 20KB    |
| 500    | ~350    | 20        | 5min | 50KB    |

## Verification Queries

### Check Enrichment Coverage
```sql
SELECT 
  risk_model_used,
  COUNT(*) as leases,
  ROUND(AVG(total_risk_score), 1) as avg_risk,
  ROUND(AVG(estimated_annual_rent), 0) as avg_rent
FROM gold_lease_risk_scores
GROUP BY risk_model_used
ORDER BY leases DESC;
```

### Top Risky Tenants
```sql
SELECT 
  t.tenant_name,
  t.financial_health_score,
  t.bankruptcy_risk,
  COUNT(l.lease_id) as lease_count,
  SUM(l.estimated_annual_rent) as total_rent
FROM tenants t
JOIN silver_leases l ON t.tenant_id = l.tenant_id
GROUP BY t.tenant_name, t.financial_health_score, t.bankruptcy_risk
ORDER BY total_rent DESC
LIMIT 10;
```

### Landlord Portfolio Stats
```sql
SELECT 
  ll.landlord_name,
  ll.financial_health_score,
  ll.credit_rating,
  COUNT(l.lease_id) as properties_leased,
  SUM(l.estimated_annual_rent) as noi_from_leases,
  SUM(l.square_footage) as total_leased_sqft
FROM landlords ll
JOIN silver_leases l ON ll.landlord_id = l.landlord_id
GROUP BY ll.landlord_name, ll.financial_health_score, ll.credit_rating
ORDER BY noi_from_leases DESC;
```

## Frontend Demonstration

After generating data, the Risk Assessment page will show:

1. **Enrichment Coverage Card**: Shows 70-80% enrichment rate
2. **Risk Model Badges**: Mix of FULLY_ENRICHED (green), TENANT_ENRICHED (blue), and BASIC (gray)
3. **Expandable Details**: Click any lease to see:
   - Risk component breakdown
   - Tenant financial profile (health score, credit rating, bankruptcy risk)
   - Landlord financial profile (REIT metrics, portfolio stats)
4. **Visual Indicators**: [✓] checkmarks next to enriched tenants/landlords

## Next Steps

1. **Generate baseline data**: 100-200 leases with 80% enrichment
2. **Test risk models**: Verify all 4 models appear in frontend
3. **Compare scores**: See how enrichment improves accuracy
4. **Demo scenarios**:
   - High-risk lease (Retail tenant, low health score, expiring soon)
   - Low-risk lease (Healthcare tenant, high health score, long-term)
   - Mixed portfolio (variety of risk levels and enrichment states)

## Architecture

```
generate_enriched_data.py
    │
    ├─> Generate Landlord Profiles
    │   └─> Insert into landlords table
    │
    ├─> Generate Tenant Profiles
    │   └─> Insert into tenants table
    │
    └─> Generate Leases with IDs
        └─> Insert into silver_leases table
            │
            └─> gold_lease_risk_scores view
                └─> JOIN with tenants & landlords
                    └─> Calculate enriched risk scores
                        └─> Frontend displays results
```

## Support

For issues or questions:
1. Check `RISK_MODEL_ENRICHMENT.md` for risk calculation details
2. Check `DEPLOYMENT_GUIDE.md` for database setup
3. Check `FRONTEND_ENRICHMENT_GUIDE.md` for UI features

Happy data generation! 🎉
