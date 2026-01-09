-- Landlord Metrics View
-- Reusable metric view for landlord/property owner analytics
-- Based on enriched landlords table

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE OR REPLACE VIEW landlord_metrics
  (
    company_type COMMENT 'Company classification (REIT, Private, Public, etc.)',
    bankruptcy_risk COMMENT 'Risk level (LOW, MEDIUM, HIGH)',
    news_sentiment COMMENT 'Recent news sentiment (POSITIVE, NEUTRAL, NEGATIVE)',
    credit_rating_tier COMMENT 'Credit rating tier (Investment Grade, High Yield, Not Rated)',
    total_landlords COMMENT 'Count of landlord entities',
    total_revenue COMMENT 'Sum of annual revenue across landlords',
    total_assets COMMENT 'Sum of total assets across landlords',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    total_properties COMMENT 'Sum of properties owned',
    avg_market_cap COMMENT 'Average market capitalization',
    avg_debt_to_equity COMMENT 'Average debt-to-equity ratio',
    low_risk_count COMMENT 'Landlords with LOW bankruptcy risk',
    medium_risk_count COMMENT 'Landlords with MEDIUM bankruptcy risk',
    high_risk_count COMMENT 'Landlords with HIGH bankruptcy risk',
    positive_sentiment_count COMMENT 'Landlords with POSITIVE news sentiment',
    negative_sentiment_count COMMENT 'Landlords with NEGATIVE news sentiment'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Landlord financial and risk metrics. Provides aggregate analysis of property owner profiles with dimensional slicing.'
  AS $$
    version: 1.1
    comment: "Commercial real estate landlord metrics"
    source: fins_team_3.lease_management.landlords
    
    dimensions:
      - name: company_type
        expr: COALESCE(company_type, 'Unknown')
        
      - name: bankruptcy_risk
        expr: COALESCE(bankruptcy_risk, 'Unknown')
        
      - name: news_sentiment
        expr: COALESCE(recent_news_sentiment, 'Unknown')
        
      - name: credit_rating_tier
        expr: >
          CASE 
            WHEN credit_rating IN ('AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-') THEN 'Investment Grade'
            WHEN credit_rating IN ('BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D') THEN 'High Yield'
            ELSE 'Not Rated'
          END
    
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

-- Example queries using the metric view:
--
-- Overall landlord summary:
-- SELECT MEASURE(total_landlords), MEASURE(avg_health_score), MEASURE(total_revenue)
-- FROM landlord_metrics;
--
-- By company type:
-- SELECT company_type, MEASURE(total_landlords), MEASURE(avg_health_score)
-- FROM landlord_metrics
-- GROUP BY company_type;
--
-- Risk distribution:
-- SELECT bankruptcy_risk, MEASURE(total_landlords), MEASURE(total_revenue)
-- FROM landlord_metrics
-- GROUP BY bankruptcy_risk;
