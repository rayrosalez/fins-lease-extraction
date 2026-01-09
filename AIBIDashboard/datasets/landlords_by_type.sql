-- Landlords by Company Type Dataset
-- Distribution of landlord company types

SELECT 
    COALESCE(company_type, 'Unknown') as company_type,
    COUNT(*) as count
FROM ${catalog}.${schema}.landlords
GROUP BY company_type
ORDER BY count DESC
