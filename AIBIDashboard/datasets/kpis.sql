-- Portfolio KPIs Dataset
-- Provides overall portfolio key performance indicators

WITH base_kpis AS (
    SELECT 
        COUNT(*) as total_leases,
        COUNT(DISTINCT COALESCE(property_id, 'Unknown')) as total_properties,
        COUNT(DISTINCT tenant_name) as total_tenants,
        COUNT(DISTINCT COALESCE(industry_sector, 'Unknown')) as markets_count,
        AVG(base_rent_psf) as avg_rent_psf,
        AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt,
        SUM(CASE WHEN DATEDIFF(lease_end_date, CURRENT_DATE()) <= 365 AND DATEDIFF(lease_end_date, CURRENT_DATE()) >= 0 THEN 1 ELSE 0 END) as expiring_12_months
    FROM ${catalog}.${schema}.silver_leases
    WHERE tenant_name IS NOT NULL
),
risk_kpis AS (
    SELECT 
        AVG(total_risk_score) as avg_risk_score
    FROM ${catalog}.${schema}.gold_lease_risk_scores
)
SELECT 
    b.total_leases,
    b.total_properties,
    b.total_tenants,
    b.markets_count,
    b.avg_rent_psf,
    b.portfolio_walt,
    COALESCE(r.avg_risk_score, 0) as avg_risk_score,
    b.expiring_12_months
FROM base_kpis b
CROSS JOIN risk_kpis r
