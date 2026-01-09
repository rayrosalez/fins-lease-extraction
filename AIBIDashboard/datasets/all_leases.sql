-- All Leases Dataset
-- Complete lease inventory with key metrics

SELECT 
    lease_id,
    COALESCE(property_id, 'Unknown Property') as property_name,
    COALESCE(industry_sector, 'Unknown') as market,
    COALESCE(lease_type, 'Unknown') as asset_type,
    tenant_name,
    industry_sector,
    lease_start_date as commencement_date,
    lease_end_date as expiration_date,
    base_rent_psf,
    square_footage,
    estimated_annual_rent,
    annual_escalation_pct,
    validation_status as status,
    ROUND(DATEDIFF(lease_end_date, CURRENT_DATE()) / 365.25, 1) as years_remaining
FROM ${catalog}.${schema}.silver_leases
WHERE tenant_name IS NOT NULL
ORDER BY lease_end_date ASC
