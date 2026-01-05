USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Create Landlord table with financial and profile information
CREATE TABLE IF NOT EXISTS landlords (
    -- Primary Key
    landlord_id STRING NOT NULL COMMENT 'Unique identifier for landlord (derived from name)',
    
    -- Basic Information (from lease extraction)
    landlord_name STRING COMMENT 'Legal name of the landlord/property owner',
    landlord_address STRING COMMENT 'Primary business address',
    
    -- Financial Information (enriched via MCP web search)
    company_type STRING COMMENT 'REIT, Private, Public, etc.',
    stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
    market_cap DOUBLE COMMENT 'Market capitalization in USD',
    total_assets DOUBLE COMMENT 'Total assets under management in USD',
    credit_rating STRING COMMENT 'Credit rating (e.g., AAA, BBB+)',
    credit_rating_agency STRING COMMENT 'Rating agency (S&P, Moody\'s, Fitch)',
    annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
    net_operating_income DOUBLE COMMENT 'NOI in USD',
    debt_to_equity_ratio DOUBLE COMMENT 'D/E ratio',
    
    -- Portfolio Information
    total_properties INT COMMENT 'Total number of properties owned',
    total_square_footage DOUBLE COMMENT 'Total portfolio square footage',
    primary_property_types STRING COMMENT 'Main property types (Office, Retail, Industrial)',
    geographic_focus STRING COMMENT 'Primary geographic markets',
    
    -- Risk & Profile
    financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
    bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
    recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE based on recent news',
    
    -- Data Provenance
    enrichment_source STRING COMMENT 'MCP_WEB_SEARCH, MANUAL, API',
    enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
    last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
    source_urls STRING COMMENT 'JSON array of source URLs used for enrichment',
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP,
    
    CONSTRAINT landlords_pk PRIMARY KEY (landlord_id)
)
USING DELTA
COMMENT 'Landlord master table with financial profiles enriched via MCP web search'
TBLPROPERTIES (delta.enableChangeDataFeed = true);

