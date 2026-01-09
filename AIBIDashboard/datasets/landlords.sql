-- Landlords Dataset
-- Full landlord profiles with financial data

SELECT 
    landlord_id,
    landlord_name,
    landlord_address,
    company_type,
    stock_ticker,
    market_cap,
    total_assets,
    credit_rating,
    credit_rating_agency,
    annual_revenue,
    net_operating_income,
    debt_to_equity_ratio,
    total_properties,
    total_square_footage,
    primary_property_types,
    geographic_focus,
    financial_health_score,
    bankruptcy_risk,
    recent_news_sentiment,
    enrichment_source,
    last_enriched_at
FROM ${catalog}.${schema}.landlords
ORDER BY landlord_name
