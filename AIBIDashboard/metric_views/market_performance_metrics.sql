-- Market Performance Metrics View
-- Reusable metric view for market-level portfolio analytics
-- Enables analysis by geographic and sector dimensions

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE OR REPLACE VIEW market_performance_metrics
  (
    market COMMENT 'Industry sector/market segment',
    city COMMENT 'Property city',
    state COMMENT 'Property state',
    region COMMENT 'Geographic region',
    property_count COMMENT 'Count of unique properties',
    lease_count COMMENT 'Total number of leases',
    total_sqft COMMENT 'Total square footage',
    total_annual_rent COMMENT 'Total annual rental income',
    avg_rent_psf COMMENT 'Average rent per square foot',
    median_rent_psf COMMENT 'Median rent per square foot',
    min_rent_psf COMMENT 'Minimum rent PSF in segment',
    max_rent_psf COMMENT 'Maximum rent PSF in segment',
    walt_years COMMENT 'Weighted Average Lease Term in years',
    avg_lease_size COMMENT 'Average lease square footage',
    occupancy_value COMMENT 'Total occupied rent value'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Market-level performance metrics for portfolio analysis. Provides geographic and sector-based aggregations.'
  AS $$
    version: 1.1
    comment: "CRE market performance metrics"
    source: fins_team_3.lease_management.silver_leases
    filter: tenant_name IS NOT NULL AND lease_end_date IS NOT NULL
    
    dimensions:
      - name: market
        expr: COALESCE(industry_sector, 'Unknown')
        
      - name: city
        expr: COALESCE(property_city, 'Unknown')
        
      - name: state
        expr: COALESCE(property_state, 'Unknown')
        
      - name: region
        expr: >
          CASE 
            WHEN property_state IN ('CA', 'WA', 'OR', 'NV', 'AZ') THEN 'West'
            WHEN property_state IN ('TX', 'OK', 'NM', 'AR', 'LA') THEN 'Southwest'
            WHEN property_state IN ('NY', 'NJ', 'PA', 'CT', 'MA', 'NH', 'VT', 'ME', 'RI') THEN 'Northeast'
            WHEN property_state IN ('FL', 'GA', 'NC', 'SC', 'VA', 'TN', 'AL', 'MS') THEN 'Southeast'
            WHEN property_state IN ('IL', 'OH', 'MI', 'IN', 'WI', 'MN', 'IA', 'MO') THEN 'Midwest'
            WHEN property_state IN ('CO', 'UT', 'WY', 'MT', 'ID') THEN 'Mountain'
            ELSE 'Other'
          END
    
    measures:
      - name: property_count
        expr: COUNT(DISTINCT property_id)
        
      - name: lease_count
        expr: COUNT(1)
        
      - name: total_sqft
        expr: SUM(square_footage)
        
      - name: total_annual_rent
        expr: SUM(estimated_annual_rent)
        
      - name: avg_rent_psf
        expr: AVG(base_rent_psf)
        
      - name: median_rent_psf
        expr: PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY base_rent_psf)
        
      - name: min_rent_psf
        expr: MIN(base_rent_psf)
        
      - name: max_rent_psf
        expr: MAX(base_rent_psf)
        
      - name: walt_years
        expr: >
          SUM(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25 * estimated_annual_rent) 
          / NULLIF(SUM(estimated_annual_rent), 0)
        
      - name: avg_lease_size
        expr: AVG(square_footage)
        
      - name: occupancy_value
        expr: SUM(estimated_annual_rent) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) > 0)
  $$;

-- Example queries using the metric view:
--
-- Market comparison:
-- SELECT market, MEASURE(lease_count), MEASURE(avg_rent_psf), MEASURE(walt_years)
-- FROM market_performance_metrics
-- GROUP BY market
-- ORDER BY MEASURE(total_annual_rent) DESC;
--
-- Regional performance:
-- SELECT region, MEASURE(property_count), MEASURE(total_sqft), MEASURE(total_annual_rent)
-- FROM market_performance_metrics
-- GROUP BY region;
--
-- City-level analysis:
-- SELECT city, state, MEASURE(lease_count), MEASURE(avg_rent_psf), MEASURE(walt_years)
-- FROM market_performance_metrics
-- GROUP BY city, state
-- ORDER BY MEASURE(lease_count) DESC
-- LIMIT 10;
