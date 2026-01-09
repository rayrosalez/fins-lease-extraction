-- Tenant Metrics View
-- Reusable metric view for commercial tenant analytics
-- Based on enriched tenants table

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE OR REPLACE VIEW tenant_metrics
  (
    industry_sector COMMENT 'Primary industry sector',
    company_type COMMENT 'Company classification (Public, Private, etc.)',
    bankruptcy_risk COMMENT 'Risk level (LOW, MEDIUM, HIGH)',
    industry_risk COMMENT 'Industry volatility risk (LOW, MEDIUM, HIGH)',
    company_size COMMENT 'Size category based on employee count',
    total_tenants COMMENT 'Count of tenant entities',
    total_revenue COMMENT 'Sum of annual revenue across tenants',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    avg_employee_count COMMENT 'Average employee count',
    avg_revenue_growth COMMENT 'Average revenue growth percentage',
    avg_profit_margin COMMENT 'Average profit margin percentage',
    growing_companies COMMENT 'Tenants with positive revenue growth',
    declining_companies COMMENT 'Tenants with negative revenue growth',
    low_risk_count COMMENT 'Tenants with LOW bankruptcy risk',
    high_risk_count COMMENT 'Tenants with HIGH bankruptcy risk',
    litigation_count COMMENT 'Tenants with active litigation'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Commercial tenant financial and risk metrics. Enables analysis of tenant base health and performance characteristics.'
  AS $$
    version: 1.1
    comment: "Commercial real estate tenant metrics"
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
        expr: >
          CASE 
            WHEN COALESCE(employee_count, 0) < 100 THEN 'Small (<100)'
            WHEN employee_count >= 100 AND employee_count < 1000 THEN 'Medium (100-1K)'
            WHEN employee_count >= 1000 AND employee_count < 10000 THEN 'Large (1K-10K)'
            ELSE 'Enterprise (10K+)'
          END
    
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

-- Example queries using the metric view:
--
-- Overall tenant summary:
-- SELECT MEASURE(total_tenants), MEASURE(avg_health_score), 
--        MEASURE(growing_companies), MEASURE(declining_companies)
-- FROM tenant_metrics;
--
-- By industry sector:
-- SELECT industry_sector, MEASURE(total_tenants), MEASURE(avg_revenue_growth)
-- FROM tenant_metrics
-- GROUP BY industry_sector
-- ORDER BY MEASURE(avg_revenue_growth) DESC;
--
-- By company size:
-- SELECT company_size, MEASURE(total_tenants), MEASURE(avg_health_score)
-- FROM tenant_metrics
-- GROUP BY company_size;
