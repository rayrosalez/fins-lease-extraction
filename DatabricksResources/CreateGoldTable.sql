%sql
USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE OR REPLACE VIEW gold_lease_risk_scores AS
WITH risk_calcs AS (
  SELECT 
    lease_id,
    tenant_name,
    property_id,
    industry_sector,
    lease_end_date,
    annual_escalation_pct,
    estimated_annual_rent,
    -- 1. Rollover Risk: Days until expiration
    DATEDIFF(lease_end_date, CURRENT_DATE()) as days_to_expiry,
    -- 2. Sector Risk Mapping (Example)
    CASE 
      WHEN industry_sector IN ('Retail', 'Restaurant') THEN 80
      WHEN industry_sector IN ('Tech', 'Office') THEN 50
      WHEN industry_sector IN ('Healthcare', 'Government') THEN 20
      ELSE 40 
    END as sector_risk_base
  FROM silver_leases
)
SELECT 
  *,
  -- Normalized Component Scores (0-100)
  CASE 
    WHEN days_to_expiry < 0 THEN 100         -- Already expired
    WHEN days_to_expiry < 365 THEN 80       -- Expires within a year
    WHEN days_to_expiry < 730 THEN 40       -- Expires within 2 years
    ELSE 10                                 -- Long term stability
  END as rollover_score,
  
  CASE 
    WHEN annual_escalation_pct < 2.0 THEN 90
    WHEN annual_escalation_pct < 3.0 THEN 50
    ELSE 10 
  END as escalation_risk_score,

  -- Final Weighted Risk Score
  ROUND(
    (CASE WHEN days_to_expiry < 365 THEN 80 ELSE 20 END * 0.40) + -- Rollover (40%)
    (escalation_risk_score * 0.20) +                             -- Inflation (20%)
    (sector_risk_base * 0.20) +                                  -- Industry (20%)
    (40 * 0.20),                                                 -- Placeholder for Portfolio Concentration (20%)
  2) AS total_risk_score
FROM risk_calcs;