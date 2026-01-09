-- Risk Assessment Dataset
-- Comprehensive risk data from gold layer

SELECT 
    lease_id,
    tenant_name,
    property_id,
    industry_sector,
    lease_end_date,
    annual_escalation_pct,
    estimated_annual_rent,
    square_footage,
    days_to_expiry,
    sector_risk_base,
    portfolio_concentration_pct,
    rollover_score,
    escalation_risk_score,
    concentration_risk_score,
    lease_status,
    total_risk_score
FROM ${catalog}.${schema}.gold_lease_risk_scores
WHERE total_risk_score IS NOT NULL
ORDER BY total_risk_score DESC
LIMIT 100
