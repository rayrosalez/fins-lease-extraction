-- Top Risky Leases Dataset
-- Top 10 highest risk leases for immediate attention

SELECT 
    tenant_name,
    industry_sector,
    lease_status,
    days_to_expiry,
    estimated_annual_rent,
    portfolio_concentration_pct,
    total_risk_score
FROM ${catalog}.${schema}.gold_lease_risk_scores
WHERE total_risk_score IS NOT NULL
ORDER BY total_risk_score DESC
LIMIT 10
