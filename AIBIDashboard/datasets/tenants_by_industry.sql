-- Tenants by Industry Dataset
-- Distribution of tenants across industry sectors

SELECT 
    COALESCE(industry_sector, 'Unknown') as industry_sector,
    COUNT(*) as count
FROM ${catalog}.${schema}.tenants
GROUP BY industry_sector
ORDER BY count DESC
LIMIT 10
