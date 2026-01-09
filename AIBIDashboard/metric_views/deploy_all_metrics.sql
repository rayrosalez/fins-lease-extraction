-- Deploy All Metric Views
-- Run this script to create all portfolio metric views in your Unity Catalog
-- Update the catalog and schema as needed

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- ============================================================================
-- 1. PORTFOLIO LEASE METRICS
-- Core lease metrics with market, city, and status dimensions
-- ============================================================================
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
  COMMENT 'Portfolio-wide lease metrics for CRE analytics.'
  AS $$
    version: 1.1
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

-- ============================================================================
-- 2. RISK ASSESSMENT METRICS
-- Risk scoring metrics with industry and status dimensions
-- ============================================================================
CREATE OR REPLACE VIEW risk_assessment_metrics
  (
    industry_sector COMMENT 'Tenant industry sector',
    lease_status COMMENT 'Risk-based status category',
    risk_category COMMENT 'Categorized risk level',
    total_leases COMMENT 'Count of leases in segment',
    avg_risk_score COMMENT 'Average total risk score (0-100)',
    total_rent_at_risk COMMENT 'Sum of annual rent for leases',
    high_risk_rent COMMENT 'Annual rent from high-risk leases (score > 70)',
    critical_lease_count COMMENT 'Leases in critical status',
    high_priority_count COMMENT 'Leases in high priority status',
    avg_rollover_risk COMMENT 'Average rollover risk component',
    avg_escalation_risk COMMENT 'Average escalation risk component',
    avg_concentration_risk COMMENT 'Average concentration risk component',
    avg_industry_risk COMMENT 'Average sector/industry risk component',
    avg_days_to_expiry COMMENT 'Average days until lease expiration'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Lease risk assessment metrics with multi-factor scoring.'
  AS $$
    version: 1.1
    source: fins_team_3.lease_management.gold_lease_risk_scores
    filter: total_risk_score IS NOT NULL
    dimensions:
      - name: industry_sector
        expr: COALESCE(industry_sector, 'Unknown')
      - name: lease_status
        expr: lease_status
      - name: risk_category
        expr: "CASE WHEN total_risk_score >= 80 THEN 'Critical (80-100)' WHEN total_risk_score >= 60 THEN 'High (60-79)' WHEN total_risk_score >= 40 THEN 'Medium (40-59)' WHEN total_risk_score >= 20 THEN 'Low (20-39)' ELSE 'Minimal (0-19)' END"
    measures:
      - name: total_leases
        expr: COUNT(1)
      - name: avg_risk_score
        expr: AVG(total_risk_score)
      - name: total_rent_at_risk
        expr: SUM(estimated_annual_rent)
      - name: high_risk_rent
        expr: SUM(estimated_annual_rent) FILTER (WHERE total_risk_score > 70)
      - name: critical_lease_count
        expr: COUNT(1) FILTER (WHERE lease_status = 'CRITICAL')
      - name: high_priority_count
        expr: COUNT(1) FILTER (WHERE lease_status = 'HIGH_PRIORITY')
      - name: avg_rollover_risk
        expr: AVG(rollover_score)
      - name: avg_escalation_risk
        expr: AVG(escalation_risk_score)
      - name: avg_concentration_risk
        expr: AVG(concentration_risk_score)
      - name: avg_industry_risk
        expr: AVG(sector_risk_base)
      - name: avg_days_to_expiry
        expr: AVG(days_to_expiry)
  $$;

-- ============================================================================
-- 3. LANDLORD METRICS
-- Landlord profile metrics with company type and risk dimensions
-- ============================================================================
CREATE OR REPLACE VIEW landlord_metrics
  (
    company_type COMMENT 'Company classification',
    bankruptcy_risk COMMENT 'Risk level (LOW, MEDIUM, HIGH)',
    news_sentiment COMMENT 'Recent news sentiment',
    credit_rating_tier COMMENT 'Credit rating tier',
    total_landlords COMMENT 'Count of landlord entities',
    total_revenue COMMENT 'Sum of annual revenue',
    total_assets COMMENT 'Sum of total assets',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    total_properties COMMENT 'Sum of properties owned',
    avg_market_cap COMMENT 'Average market capitalization',
    avg_debt_to_equity COMMENT 'Average debt-to-equity ratio',
    low_risk_count COMMENT 'LOW bankruptcy risk count',
    medium_risk_count COMMENT 'MEDIUM bankruptcy risk count',
    high_risk_count COMMENT 'HIGH bankruptcy risk count',
    positive_sentiment_count COMMENT 'POSITIVE sentiment count',
    negative_sentiment_count COMMENT 'NEGATIVE sentiment count'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Landlord financial and risk metrics.'
  AS $$
    version: 1.1
    source: fins_team_3.lease_management.landlords
    dimensions:
      - name: company_type
        expr: COALESCE(company_type, 'Unknown')
      - name: bankruptcy_risk
        expr: COALESCE(bankruptcy_risk, 'Unknown')
      - name: news_sentiment
        expr: COALESCE(recent_news_sentiment, 'Unknown')
      - name: credit_rating_tier
        expr: "CASE WHEN credit_rating IN ('AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-') THEN 'Investment Grade' WHEN credit_rating IN ('BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D') THEN 'High Yield' ELSE 'Not Rated' END"
    measures:
      - name: total_landlords
        expr: COUNT(1)
      - name: total_revenue
        expr: SUM(annual_revenue)
      - name: total_assets
        expr: SUM(total_assets)
      - name: avg_health_score
        expr: AVG(financial_health_score)
      - name: total_properties
        expr: SUM(total_properties)
      - name: avg_market_cap
        expr: AVG(market_cap)
      - name: avg_debt_to_equity
        expr: AVG(debt_to_equity_ratio)
      - name: low_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'LOW')
      - name: medium_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'MEDIUM')
      - name: high_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'HIGH')
      - name: positive_sentiment_count
        expr: COUNT(1) FILTER (WHERE recent_news_sentiment = 'POSITIVE')
      - name: negative_sentiment_count
        expr: COUNT(1) FILTER (WHERE recent_news_sentiment = 'NEGATIVE')
  $$;

-- ============================================================================
-- 4. TENANT METRICS
-- Tenant profile metrics with industry and size dimensions
-- ============================================================================
CREATE OR REPLACE VIEW tenant_metrics
  (
    industry_sector COMMENT 'Primary industry sector',
    company_type COMMENT 'Company classification',
    bankruptcy_risk COMMENT 'Risk level',
    industry_risk COMMENT 'Industry volatility risk',
    company_size COMMENT 'Size category based on employees',
    total_tenants COMMENT 'Count of tenant entities',
    total_revenue COMMENT 'Sum of annual revenue',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    avg_employee_count COMMENT 'Average employee count',
    avg_revenue_growth COMMENT 'Average revenue growth %',
    avg_profit_margin COMMENT 'Average profit margin %',
    growing_companies COMMENT 'Positive revenue growth count',
    declining_companies COMMENT 'Negative revenue growth count',
    low_risk_count COMMENT 'LOW bankruptcy risk count',
    high_risk_count COMMENT 'HIGH bankruptcy risk count',
    litigation_count COMMENT 'Active litigation count'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Commercial tenant financial and risk metrics.'
  AS $$
    version: 1.1
    source: fins_team_3.lease_management.tenants
    dimensions:
      - name: industry_sector
        expr: COALESCE(industry_sector, 'Unknown')
      - name: company_type
        expr: COALESCE(company_type, 'Unknown')
      - name: bankruptcy_risk
        expr: COALESCE(bankruptcy_risk, 'Unknown')
      - name: industry_risk
        expr: COALESCE(industry_risk, 'Unknown')
      - name: company_size
        expr: "CASE WHEN COALESCE(employee_count, 0) < 100 THEN 'Small (<100)' WHEN employee_count >= 100 AND employee_count < 1000 THEN 'Medium (100-1K)' WHEN employee_count >= 1000 AND employee_count < 10000 THEN 'Large (1K-10K)' ELSE 'Enterprise (10K+)' END"
    measures:
      - name: total_tenants
        expr: COUNT(1)
      - name: total_revenue
        expr: SUM(annual_revenue)
      - name: avg_health_score
        expr: AVG(financial_health_score)
      - name: avg_employee_count
        expr: AVG(employee_count)
      - name: avg_revenue_growth
        expr: AVG(revenue_growth_pct)
      - name: avg_profit_margin
        expr: AVG(profit_margin_pct)
      - name: growing_companies
        expr: COUNT(1) FILTER (WHERE revenue_growth_pct > 0)
      - name: declining_companies
        expr: COUNT(1) FILTER (WHERE revenue_growth_pct < 0)
      - name: low_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'LOW')
      - name: high_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'HIGH')
      - name: litigation_count
        expr: COUNT(1) FILTER (WHERE litigation_flag = TRUE)
  $$;

-- ============================================================================
-- 5. MARKET PERFORMANCE METRICS
-- Geographic and sector-level performance metrics
-- ============================================================================
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
    min_rent_psf COMMENT 'Minimum rent PSF',
    max_rent_psf COMMENT 'Maximum rent PSF',
    walt_years COMMENT 'Weighted Average Lease Term',
    avg_lease_size COMMENT 'Average lease square footage',
    occupancy_value COMMENT 'Total occupied rent value'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Market-level performance metrics for portfolio analysis.'
  AS $$
    version: 1.1
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
        expr: "CASE WHEN property_state IN ('CA', 'WA', 'OR', 'NV', 'AZ') THEN 'West' WHEN property_state IN ('TX', 'OK', 'NM', 'AR', 'LA') THEN 'Southwest' WHEN property_state IN ('NY', 'NJ', 'PA', 'CT', 'MA', 'NH', 'VT', 'ME', 'RI') THEN 'Northeast' WHEN property_state IN ('FL', 'GA', 'NC', 'SC', 'VA', 'TN', 'AL', 'MS') THEN 'Southeast' WHEN property_state IN ('IL', 'OH', 'MI', 'IN', 'WI', 'MN', 'IA', 'MO') THEN 'Midwest' WHEN property_state IN ('CO', 'UT', 'WY', 'MT', 'ID') THEN 'Mountain' ELSE 'Other' END"
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
      - name: min_rent_psf
        expr: MIN(base_rent_psf)
      - name: max_rent_psf
        expr: MAX(base_rent_psf)
      - name: walt_years
        expr: "SUM(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25 * estimated_annual_rent) / NULLIF(SUM(estimated_annual_rent), 0)"
      - name: avg_lease_size
        expr: AVG(square_footage)
      - name: occupancy_value
        expr: SUM(estimated_annual_rent) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) > 0)
  $$;

-- ============================================================================
-- Verification: List all created metric views
-- ============================================================================
SHOW VIEWS IN lease_management LIKE '*_metrics';
