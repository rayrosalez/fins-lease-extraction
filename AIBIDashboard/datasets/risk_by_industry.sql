-- Risk by Industry Dataset
-- Average risk scores by industry sector

SELECT 
    COALESCE(industry_sector, 'Unknown') as industry_sector,
    COUNT(*) as lease_count,
    ROUND(AVG(total_risk_score), 1) as avg_risk_score,
    SUM(estimated_annual_rent) as total_rent
FROM ${catalog}.${schema}.gold_lease_risk_scores
WHERE total_risk_score IS NOT NULL
GROUP BY industry_sector
ORDER BY avg_risk_score DESC
