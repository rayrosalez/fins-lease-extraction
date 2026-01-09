-- Market Summary Dataset
-- Portfolio metrics by industry sector/market

SELECT 
    COALESCE(industry_sector, 'Unknown') as market,
    COUNT(*) as lease_count,
    ROUND(AVG(base_rent_psf), 2) as avg_rent_psf,
    ROUND(AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25), 2) as walt_years,
    SUM(square_footage) as total_sqft,
    SUM(estimated_annual_rent) as total_annual_rent
FROM ${catalog}.${schema}.silver_leases
WHERE lease_end_date IS NOT NULL
GROUP BY industry_sector
ORDER BY lease_count DESC
