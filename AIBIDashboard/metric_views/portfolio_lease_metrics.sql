-- Portfolio Lease Metrics View
-- Reusable metric view for lease portfolio KPIs
-- Can be used across dashboards, notebooks, and applications

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE OR REPLACE VIEW portfolio_lease_metrics
  (
    market COMMENT 'Industry sector/market segment',
    city COMMENT 'Property city location',
    state COMMENT 'Property state location',
    lease_status COMMENT 'Current validation status',
    total_leases COMMENT 'Count of active leases',
    total_sqft COMMENT 'Total leased square footage',
    total_annual_rent COMMENT 'Total estimated annual rent',
    avg_rent_psf COMMENT 'Average rent per square foot',
    avg_years_remaining COMMENT 'Average remaining lease term',
    expiring_90_days COMMENT 'Leases expiring within 90 days',
    expiring_180_days COMMENT 'Leases expiring within 180 days',
    expiring_365_days COMMENT 'Leases expiring within 365 days'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Portfolio-wide lease metrics for CRE analytics. Provides aggregate KPIs with dimensional slicing by market, location, and status.'
  AS $$
    version: 1.1
    comment: "Commercial real estate lease portfolio metrics"
    source: fins_team_3.lease_management.silver_leases
    filter: tenant_name IS NOT NULL
    
    dimensions:
      - name: market
        expr: COALESCE(industry_sector, 'Unknown')
        
      - name: city
        expr: COALESCE(property_city, 'Unknown')
        
      - name: state
        expr: COALESCE(property_state, 'Unknown')
        
      - name: lease_status
        expr: validation_status
    
    measures:
      - name: total_leases
        expr: COUNT(1)
        
      - name: total_sqft
        expr: SUM(square_footage)
        
      - name: total_annual_rent
        expr: SUM(estimated_annual_rent)
        
      - name: avg_rent_psf
        expr: AVG(base_rent_psf)
        
      - name: avg_years_remaining
        expr: AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25)
        
      - name: expiring_90_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 90)
        
      - name: expiring_180_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 180)
        
      - name: expiring_365_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 365)
  $$;

-- Example queries using the metric view:
-- 
-- Portfolio-wide totals:
-- SELECT MEASURE(total_leases), MEASURE(total_annual_rent), MEASURE(avg_rent_psf)
-- FROM portfolio_lease_metrics;
--
-- By market:
-- SELECT market, MEASURE(total_leases), MEASURE(avg_rent_psf)
-- FROM portfolio_lease_metrics
-- GROUP BY market;
--
-- By city with expiring leases:
-- SELECT city, state, MEASURE(total_leases), MEASURE(expiring_90_days)
-- FROM portfolio_lease_metrics
-- GROUP BY city, state
-- HAVING MEASURE(expiring_90_days) > 0;
