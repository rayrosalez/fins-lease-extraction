%sql
USE CATALOG ${CATALOG};
USE SCHEMA ${SCHEMA};

CREATE OR REPLACE VIEW gold_lease_risk_scores AS
WITH enriched_leases AS (
  SELECT 
    l.lease_id,
    l.tenant_name,
    l.tenant_id,
    l.landlord_name,
    l.landlord_id,
    l.property_id,
    l.industry_sector,
    l.lease_end_date,
    l.annual_escalation_pct,
    l.estimated_annual_rent,
    l.square_footage,
    
    -- Join tenant enrichment data (LEFT JOIN so we don't lose leases)
    t.financial_health_score as tenant_health_score,
    t.credit_rating as tenant_credit_rating,
    t.bankruptcy_risk as tenant_bankruptcy_risk,
    t.industry_risk as tenant_industry_risk,
    t.payment_history_score as tenant_payment_score,
    t.market_cap as tenant_market_cap,
    t.annual_revenue as tenant_revenue,
    t.enrichment_confidence as tenant_enrichment_confidence,
    
    -- Join landlord enrichment data (LEFT JOIN so we don't lose leases)
    ll.financial_health_score as landlord_health_score,
    ll.credit_rating as landlord_credit_rating,
    ll.bankruptcy_risk as landlord_bankruptcy_risk,
    ll.debt_to_equity_ratio as landlord_debt_to_equity,
    ll.enrichment_confidence as landlord_enrichment_confidence,
    
    -- Flag if enrichment data is available
    CASE WHEN t.tenant_id IS NOT NULL THEN TRUE ELSE FALSE END as has_tenant_enrichment,
    CASE WHEN ll.landlord_id IS NOT NULL THEN TRUE ELSE FALSE END as has_landlord_enrichment
    
  FROM silver_leases l
  LEFT JOIN tenants t ON l.tenant_id = t.tenant_id
  LEFT JOIN landlords ll ON l.landlord_id = ll.landlord_id
  WHERE l.lease_end_date IS NOT NULL
),
risk_calcs AS (
  SELECT 
    *,
    -- Calculate days until expiration
    DATEDIFF(lease_end_date, CURRENT_DATE()) as days_to_expiry,
    
    -- Sector Risk Mapping (higher scores = higher risk)
    -- Use enriched tenant industry risk if available, otherwise fallback to sector mapping
    CASE 
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'HIGH' THEN 80
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'MEDIUM' THEN 50
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'LOW' THEN 20
      WHEN industry_sector IN ('Retail', 'Restaurant') THEN 80
      WHEN industry_sector IN ('Tech', 'Office') THEN 50
      WHEN industry_sector IN ('Healthcare', 'Government') THEN 20
      ELSE 40 
    END as sector_risk_base,
    
    -- Calculate portfolio concentration (larger leases = higher risk if lost)
    estimated_annual_rent / NULLIF(SUM(estimated_annual_rent) OVER (), 0) * 100 as portfolio_concentration_pct,
    
    -- TENANT CREDIT RISK SCORE (0-100, higher = more risk)
    -- Convert financial health (1-10, higher = better) to risk (0-100, higher = worse)
    CASE 
      WHEN has_tenant_enrichment AND tenant_health_score IS NOT NULL THEN
        -- Inverse relationship: health 10 = risk 0, health 1 = risk 100
        ROUND(100 - ((tenant_health_score - 1) / 9.0) * 100, 2)
      ELSE 50  -- Default moderate risk if no enrichment
    END as tenant_credit_risk_score,
    
    -- TENANT BANKRUPTCY RISK SCORE (0-100)
    CASE
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'HIGH' THEN 90
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'MEDIUM' THEN 50
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'LOW' THEN 10
      ELSE 40  -- Default if no enrichment
    END as tenant_bankruptcy_risk_score,
    
    -- LANDLORD FINANCIAL STRENGTH SCORE (0-100, higher = more risk)
    -- Convert financial health (1-10, higher = better) to risk (0-100, higher = worse)
    CASE 
      WHEN has_landlord_enrichment AND landlord_health_score IS NOT NULL THEN
        -- Inverse relationship: health 10 = risk 0, health 1 = risk 100
        ROUND(100 - ((landlord_health_score - 1) / 9.0) * 100, 2)
      ELSE 30  -- Default low-moderate risk for landlords (typically more stable)
    END as landlord_risk_score
    
  FROM enriched_leases
)
SELECT 
  lease_id,
  tenant_name,
  tenant_id,
  landlord_name,
  landlord_id,
  property_id,
  industry_sector,
  lease_end_date,
  annual_escalation_pct,
  estimated_annual_rent,
  square_footage,
  days_to_expiry,
  sector_risk_base,
  portfolio_concentration_pct,
  
  -- Enrichment flags and data
  has_tenant_enrichment,
  has_landlord_enrichment,
  tenant_health_score,
  tenant_credit_rating,
  tenant_bankruptcy_risk,
  tenant_payment_score,
  tenant_enrichment_confidence,
  landlord_health_score,
  landlord_credit_rating,
  landlord_bankruptcy_risk,
  landlord_debt_to_equity,
  landlord_enrichment_confidence,
  
  -- Risk component scores
  tenant_credit_risk_score,
  tenant_bankruptcy_risk_score,
  landlord_risk_score,
  
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
  -- Model changes based on whether we have enrichment data
  CASE
    -- ENRICHED MODEL: When we have both tenant and landlord enrichment
    WHEN has_tenant_enrichment AND has_landlord_enrichment THEN
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
        END * 0.25) +                                  -- Rollover Risk (25%)
        (escalation_risk_score * 0.10) +               -- Inflation Risk (10%)
        (sector_risk_base * 0.10) +                    -- Industry Risk (10%)
        (concentration_risk_score * 0.15) +            -- Portfolio Concentration (15%)
        (tenant_credit_risk_score * 0.20) +            -- Tenant Financial Health (20%)
        (tenant_bankruptcy_risk_score * 0.10) +        -- Tenant Bankruptcy Risk (10%)
        (landlord_risk_score * 0.10),                  -- Landlord Financial Strength (10%)
      2)
    
    -- PARTIALLY ENRICHED MODEL: When we have only tenant enrichment
    WHEN has_tenant_enrichment AND NOT has_landlord_enrichment THEN
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
        END * 0.30) +                                  -- Rollover Risk (30%)
        (escalation_risk_score * 0.15) +               -- Inflation Risk (15%)
        (sector_risk_base * 0.10) +                    -- Industry Risk (10%)
        (concentration_risk_score * 0.15) +            -- Portfolio Concentration (15%)
        (tenant_credit_risk_score * 0.20) +            -- Tenant Financial Health (20%)
        (tenant_bankruptcy_risk_score * 0.10),         -- Tenant Bankruptcy Risk (10%)
      2)
    
    -- PARTIALLY ENRICHED MODEL: When we have only landlord enrichment
    WHEN NOT has_tenant_enrichment AND has_landlord_enrichment THEN
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
        END * 0.35) +                                  -- Rollover Risk (35%)
        (escalation_risk_score * 0.15) +               -- Inflation Risk (15%)
        (sector_risk_base * 0.15) +                    -- Industry Risk (15%)
        (concentration_risk_score * 0.20) +            -- Portfolio Concentration (20%)
        (landlord_risk_score * 0.15),                  -- Landlord Financial Strength (15%)
      2)
    
    -- BASIC MODEL: When we have no enrichment data (fallback)
    ELSE
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
      2)
  END AS total_risk_score,
  
  -- Risk Model Indicator
  CASE
    WHEN has_tenant_enrichment AND has_landlord_enrichment THEN 'FULLY_ENRICHED'
    WHEN has_tenant_enrichment AND NOT has_landlord_enrichment THEN 'TENANT_ENRICHED'
    WHEN NOT has_tenant_enrichment AND has_landlord_enrichment THEN 'LANDLORD_ENRICHED'
    ELSE 'BASIC'
  END as risk_model_used

FROM risk_calcs
ORDER BY total_risk_score DESC, days_to_expiry ASC;
