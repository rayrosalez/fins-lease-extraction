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
    square_footage,
    -- Calculate days until expiration
    DATEDIFF(lease_end_date, CURRENT_DATE()) as days_to_expiry,
    -- Sector Risk Mapping (higher scores = higher risk)
    CASE 
      WHEN industry_sector IN ('Retail', 'Restaurant') THEN 80
      WHEN industry_sector IN ('Tech', 'Office') THEN 50
      WHEN industry_sector IN ('Healthcare', 'Government') THEN 20
      ELSE 40 
    END as sector_risk_base,
    -- Calculate portfolio concentration (larger leases = higher risk if lost)
    estimated_annual_rent / NULLIF(SUM(estimated_annual_rent) OVER (), 0) * 100 as portfolio_concentration_pct
  FROM silver_leases
  WHERE lease_end_date IS NOT NULL
)
SELECT 
  *,
  -- 1. ROLLOVER RISK: Days until lease expiration
  CASE 
    -- Critical: Expiring very soon (0-90 days)
    WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100
    -- High: Expiring soon (91-180 days)
    WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90
    -- Elevated: Expiring this year (181-365 days)
    WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75
    -- Moderate: Expiring next year (1-2 years)
    WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40
    -- Low: Long-term stable (2+ years)
    WHEN days_to_expiry > 730 THEN 10
    
    -- Recently expired - still needs attention (0-90 days ago)
    WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85
    -- Expired recently (90 days to 6 months ago) - should be addressed
    WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60
    -- Expired 6-12 months ago - medium priority
    WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35
    -- Expired over 1 year ago - low priority (old data)
    WHEN days_to_expiry < -365 THEN 5
    
    ELSE 0
  END as rollover_score,
  
  -- 2. ESCALATION RISK: Low escalation = higher inflation risk
  -- (Rents not keeping pace with inflation create future revenue risk)
  CASE 
    WHEN annual_escalation_pct IS NULL THEN 50
    WHEN annual_escalation_pct < 2.0 THEN 80    -- Below inflation, high risk
    WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50  -- Moderate
    WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30  -- Good
    WHEN annual_escalation_pct >= 4.0 THEN 20   -- Above inflation, low risk
    ELSE 40 
  END as escalation_risk_score,
  
  -- 3. CONCENTRATION RISK: Large leases represent higher portfolio risk
  CASE 
    WHEN portfolio_concentration_pct >= 10.0 THEN 90  -- >10% of portfolio
    WHEN portfolio_concentration_pct >= 5.0 THEN 70   -- 5-10% of portfolio
    WHEN portfolio_concentration_pct >= 2.0 THEN 40   -- 2-5% of portfolio
    WHEN portfolio_concentration_pct >= 1.0 THEN 20   -- 1-2% of portfolio
    ELSE 10                                            -- <1% of portfolio
  END as concentration_risk_score,
  
  -- 4. LEASE STATUS: Quick status indicator
  CASE 
    WHEN days_to_expiry < -365 THEN 'EXPIRED_OLD'
    WHEN days_to_expiry < 0 THEN 'EXPIRED_RECENT'
    WHEN days_to_expiry <= 90 THEN 'CRITICAL'
    WHEN days_to_expiry <= 180 THEN 'HIGH_PRIORITY'
    WHEN days_to_expiry <= 365 THEN 'NEEDS_ATTENTION'
    WHEN days_to_expiry <= 730 THEN 'MONITOR'
    ELSE 'STABLE'
  END as lease_status,

  -- FINAL WEIGHTED RISK SCORE (0-100 scale)
  ROUND(
    (CASE 
      WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100
      WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90
      WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75
      WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40
      WHEN days_to_expiry > 730 THEN 10
      WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85
      WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60
      WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35
      WHEN days_to_expiry < -365 THEN 5
      ELSE 0
    END * 0.40) +                                  -- Rollover Risk (40%)
    (escalation_risk_score * 0.20) +               -- Inflation Risk (20%)
    (sector_risk_base * 0.20) +                    -- Industry Risk (20%)
    (concentration_risk_score * 0.20),             -- Portfolio Concentration (20%)
  2) AS total_risk_score
FROM risk_calcs
ORDER BY total_risk_score DESC, days_to_expiry ASC;