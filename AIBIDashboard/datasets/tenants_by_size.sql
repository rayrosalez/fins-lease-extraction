-- Tenants by Size Dataset
-- Company size distribution based on employee count

SELECT 
    CASE 
        WHEN COALESCE(employee_count, 0) < 100 THEN 'Small (<100)'
        WHEN employee_count >= 100 AND employee_count < 1000 THEN 'Medium (100-1K)'
        WHEN employee_count >= 1000 AND employee_count < 10000 THEN 'Large (1K-10K)'
        ELSE 'Enterprise (10K+)'
    END as company_size,
    COUNT(*) as count
FROM ${catalog}.${schema}.tenants
GROUP BY 
    CASE 
        WHEN COALESCE(employee_count, 0) < 100 THEN 'Small (<100)'
        WHEN employee_count >= 100 AND employee_count < 1000 THEN 'Medium (100-1K)'
        WHEN employee_count >= 1000 AND employee_count < 10000 THEN 'Large (1K-10K)'
        ELSE 'Enterprise (10K+)'
    END
ORDER BY 
    CASE 
        WHEN COALESCE(employee_count, 0) < 100 THEN 1
        WHEN employee_count >= 100 AND employee_count < 1000 THEN 2
        WHEN employee_count >= 1000 AND employee_count < 10000 THEN 3
        ELSE 4
    END
