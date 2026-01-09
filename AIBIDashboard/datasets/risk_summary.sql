-- Risk Summary KPIs Dataset
-- Summary statistics for risk assessment

SELECT 
    COUNT(CASE WHEN lease_status = 'CRITICAL' THEN 1 END) as critical_leases,
    COUNT(CASE WHEN lease_status = 'HIGH_PRIORITY' THEN 1 END) as high_priority_leases,
    ROUND(AVG(total_risk_score), 1) as avg_risk_score,
    SUM(CASE WHEN total_risk_score > 70 THEN estimated_annual_rent ELSE 0 END) as revenue_at_risk
FROM ${catalog}.${schema}.gold_lease_risk_scores
WHERE total_risk_score IS NOT NULL
