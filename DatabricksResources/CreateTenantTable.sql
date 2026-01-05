USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Create Tenant table with financial and profile information
CREATE TABLE IF NOT EXISTS tenants (
    -- Primary Key
    tenant_id STRING NOT NULL COMMENT 'Unique identifier for tenant (derived from name)',
    
    -- Basic Information (from lease extraction)
    tenant_name STRING COMMENT 'Legal name of the tenant',
    tenant_address STRING COMMENT 'Headquarters or primary business address',
    industry_sector STRING COMMENT 'Primary industry sector',
    
    -- Company Information (enriched via MCP web search)
    company_type STRING COMMENT 'Public, Private, Subsidiary, Non-profit',
    parent_company STRING COMMENT 'Parent company if subsidiary',
    stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
    founding_year INT COMMENT 'Year company was founded',
    employee_count INT COMMENT 'Approximate number of employees',
    headquarters_location STRING COMMENT 'HQ city and state',
    
    -- Financial Information
    market_cap DOUBLE COMMENT 'Market capitalization in USD (if public)',
    annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
    net_income DOUBLE COMMENT 'Net income in USD',
    revenue_growth_pct DOUBLE COMMENT 'Year-over-year revenue growth %',
    profit_margin_pct DOUBLE COMMENT 'Profit margin percentage',
    
    -- Credit & Risk Information
    credit_rating STRING COMMENT 'Credit rating (e.g., AAA, BBB+)',
    credit_rating_agency STRING COMMENT 'Rating agency (S&P, Moody\'s, Fitch)',
    duns_number STRING COMMENT 'D&B DUNS number',
    payment_history_score DOUBLE COMMENT 'Payment history score (1-100)',
    
    -- Risk Assessment
    financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
    bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
    industry_risk STRING COMMENT 'LOW, MEDIUM, HIGH based on sector volatility',
    recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE based on recent news',
    litigation_flag BOOLEAN COMMENT 'True if significant ongoing litigation found',
    
    -- Operational Information
    locations_count INT COMMENT 'Number of business locations',
    years_in_business INT COMMENT 'Years the company has been operating',
    
    -- Data Provenance
    enrichment_source STRING COMMENT 'MCP_WEB_SEARCH, MANUAL, API',
    enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
    last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
    source_urls STRING COMMENT 'JSON array of source URLs used for enrichment',
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP,
    
    CONSTRAINT tenants_pk PRIMARY KEY (tenant_id)
)
USING DELTA
COMMENT 'Tenant master table with financial profiles enriched via MCP web search'
TBLPROPERTIES (delta.enableChangeDataFeed = true);

