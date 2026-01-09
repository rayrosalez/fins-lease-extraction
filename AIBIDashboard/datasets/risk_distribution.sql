-- Risk Distribution Dataset
-- Categorized risk breakdown for visualization

SELECT 
    CASE 
        WHEN total_risk_score >= 80 THEN 'Critical (80-100)'
        WHEN total_risk_score >= 60 THEN 'High (60-79)'
        WHEN total_risk_score >= 40 THEN 'Medium (40-59)'
        WHEN total_risk_score >= 20 THEN 'Low (20-39)'
        ELSE 'Minimal (0-19)'
    END as risk_category,
    COUNT(*) as lease_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM ${catalog}.${schema}.gold_lease_risk_scores
WHERE total_risk_score IS NOT NULL
GROUP BY 
    CASE 
        WHEN total_risk_score >= 80 THEN 'Critical (80-100)'
        WHEN total_risk_score >= 60 THEN 'High (60-79)'
        WHEN total_risk_score >= 40 THEN 'Medium (40-59)'
        WHEN total_risk_score >= 20 THEN 'Low (20-39)'
        ELSE 'Minimal (0-19)'
    END
ORDER BY 
    CASE 
        WHEN total_risk_score >= 80 THEN 1
        WHEN total_risk_score >= 60 THEN 2
        WHEN total_risk_score >= 40 THEN 3
        WHEN total_risk_score >= 20 THEN 4
        ELSE 5
    END
