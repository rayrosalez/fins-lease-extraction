-- Tenants Dataset
-- Full tenant profiles with financial data

SELECT 
    tenant_id,
    tenant_name,
    tenant_address,
    industry_sector,
    company_type,
    parent_company,
    stock_ticker,
    founding_year,
    employee_count,
    headquarters_location,
    market_cap,
    annual_revenue,
    net_income,
    revenue_growth_pct,
    profit_margin_pct,
    credit_rating,
    financial_health_score,
    bankruptcy_risk,
    industry_risk,
    recent_news_sentiment,
    litigation_flag,
    years_in_business
FROM ${catalog}.${schema}.tenants
ORDER BY tenant_name
