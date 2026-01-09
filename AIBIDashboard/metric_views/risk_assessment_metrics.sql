-- Risk Assessment Metrics View
-- Reusable metric view for lease risk analytics
-- Based on gold_lease_risk_scores table

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

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
  COMMENT 'Lease risk assessment metrics with multi-factor scoring. Enables risk analysis by industry, status, and risk category dimensions.'
  AS $$
    version: 1.1
    comment: "Lease portfolio risk assessment metrics"
    source: fins_team_3.lease_management.gold_lease_risk_scores
    filter: total_risk_score IS NOT NULL
    
    dimensions:
      - name: industry_sector
        expr: COALESCE(industry_sector, 'Unknown')
        
      - name: lease_status
        expr: lease_status
        
      - name: risk_category
        expr: >
          CASE 
            WHEN total_risk_score >= 80 THEN 'Critical (80-100)'
            WHEN total_risk_score >= 60 THEN 'High (60-79)'
            WHEN total_risk_score >= 40 THEN 'Medium (40-59)'
            WHEN total_risk_score >= 20 THEN 'Low (20-39)'
            ELSE 'Minimal (0-19)'
          END
    
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

-- Example queries using the metric view:
--
-- Portfolio-wide risk summary:
-- SELECT MEASURE(total_leases), MEASURE(avg_risk_score), MEASURE(high_risk_rent)
-- FROM risk_assessment_metrics;
--
-- Risk by industry sector:
-- SELECT industry_sector, MEASURE(avg_risk_score), MEASURE(total_rent_at_risk)
-- FROM risk_assessment_metrics
-- GROUP BY industry_sector
-- ORDER BY MEASURE(avg_risk_score) DESC;
--
-- Risk distribution by category:
-- SELECT risk_category, MEASURE(total_leases), 
--        MEASURE(total_leases) * 100.0 / SUM(MEASURE(total_leases)) OVER () as pct
-- FROM risk_assessment_metrics
-- GROUP BY risk_category;
