-- Landlords Summary Dataset
-- Aggregate metrics for landlord profiles

SELECT 
    COUNT(*) as total_landlords,
    SUM(annual_revenue) as total_revenue,
    ROUND(AVG(financial_health_score), 1) as avg_health_score,
    COUNT(CASE WHEN bankruptcy_risk = 'LOW' THEN 1 END) as low_risk_count,
    COUNT(CASE WHEN bankruptcy_risk = 'MEDIUM' THEN 1 END) as medium_risk_count,
    COUNT(CASE WHEN bankruptcy_risk = 'HIGH' THEN 1 END) as high_risk_count
FROM ${catalog}.${schema}.landlords
