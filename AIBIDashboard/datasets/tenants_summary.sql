-- Tenants Summary Dataset
-- Aggregate metrics for tenant profiles

SELECT 
    COUNT(*) as total_tenants,
    SUM(annual_revenue) as total_revenue,
    ROUND(AVG(financial_health_score), 1) as avg_health_score,
    COUNT(CASE WHEN revenue_growth_pct > 0 THEN 1 END) as growing_companies,
    COUNT(CASE WHEN bankruptcy_risk = 'LOW' THEN 1 END) as low_risk_count,
    COUNT(CASE WHEN bankruptcy_risk = 'MEDIUM' THEN 1 END) as medium_risk_count,
    COUNT(CASE WHEN bankruptcy_risk = 'HIGH' THEN 1 END) as high_risk_count
FROM ${catalog}.${schema}.tenants
