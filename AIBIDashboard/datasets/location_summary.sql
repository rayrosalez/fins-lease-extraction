-- Location Summary Dataset
-- Geographic distribution of portfolio properties

SELECT 
    COALESCE(property_city, 'Unknown') as city,
    COALESCE(property_state, 'Unknown') as state,
    COUNT(*) as lease_count,
    SUM(square_footage) as total_sqft,
    AVG(base_rent_psf) as avg_rent_psf,
    SUM(estimated_annual_rent) as total_annual_rent
FROM ${catalog}.${schema}.silver_leases
WHERE property_city IS NOT NULL
GROUP BY property_city, property_state
ORDER BY lease_count DESC
