-- MCP Enrichment Agent Workflow
-- This script enriches landlord and tenant records using the MCP server for web search
-- Run this after 02_Structurer.sql has populated bronze_leases

%sql
-- Step 1: Extract unique landlords from bronze_leases that need enrichment
WITH new_landlords AS (
  SELECT DISTINCT
    REPLACE(REPLACE(LOWER(landlord_name), ' ', '_'), ',', '') AS landlord_id,
    landlord_name,
    landlord_address
  FROM ${CATALOG}.${SCHEMA}.bronze_leases
  WHERE landlord_name IS NOT NULL
    AND landlord_name NOT IN (SELECT landlord_name FROM ${CATALOG}.${SCHEMA}.landlords)
),

-- Step 2: Call MCP server to enrich landlord information
landlord_enrichment AS (
  SELECT 
    landlord_id,
    landlord_name,
    landlord_address,
    ai_query(
      '${CATALOG}.${SCHEMA}.mcp_enrichment_agent',
      CONCAT(
        'Search the web for financial and company information about this commercial real estate landlord/property owner: ',
        landlord_name,
        '. Address: ', COALESCE(landlord_address, 'Unknown'),
        '. Find: company type (REIT/Private/Public), stock ticker, market cap, total assets, ',
        'credit rating, annual revenue, total properties owned, property types, and any recent news. ',
        'Return structured JSON with these fields.'
      ),
      modelParameters => named_struct(
        'mcp_server_url', '__MCP_SERVER_URL__',
        'enable_web_search', true,
        'max_search_results', 5
      )
    ) AS enrichment_response
  FROM new_landlords
),

-- Step 3: Parse enrichment response
parsed_landlord_enrichment AS (
  SELECT
    landlord_id,
    landlord_name,
    landlord_address,
    from_json(
      CAST(enrichment_response.result AS STRING),
      'company_type STRING, stock_ticker STRING, market_cap DOUBLE, total_assets DOUBLE, 
       credit_rating STRING, credit_rating_agency STRING, annual_revenue DOUBLE, 
       net_operating_income DOUBLE, debt_to_equity_ratio DOUBLE, total_properties INT,
       total_square_footage DOUBLE, primary_property_types STRING, geographic_focus STRING,
       financial_health_score DOUBLE, bankruptcy_risk STRING, recent_news_sentiment STRING,
       source_urls ARRAY<STRING>'
    ) AS enriched,
    enrichment_response.result AS raw_response
  FROM landlord_enrichment
  WHERE enrichment_response.errorMessage IS NULL
)

-- Step 4: Insert/Update landlords table
MERGE INTO ${CATALOG}.${SCHEMA}.landlords AS target
USING (
  SELECT
    landlord_id,
    landlord_name,
    landlord_address,
    enriched.company_type,
    enriched.stock_ticker,
    enriched.market_cap,
    enriched.total_assets,
    enriched.credit_rating,
    enriched.credit_rating_agency,
    enriched.annual_revenue,
    enriched.net_operating_income,
    enriched.debt_to_equity_ratio,
    enriched.total_properties,
    enriched.total_square_footage,
    enriched.primary_property_types,
    enriched.geographic_focus,
    enriched.financial_health_score,
    enriched.bankruptcy_risk,
    enriched.recent_news_sentiment,
    'MCP_WEB_SEARCH' AS enrichment_source,
    0.85 AS enrichment_confidence,
    CURRENT_TIMESTAMP() AS last_enriched_at,
    to_json(enriched.source_urls) AS source_urls
  FROM parsed_landlord_enrichment
) AS source
ON target.landlord_id = source.landlord_id
WHEN MATCHED THEN UPDATE SET
  target.company_type = source.company_type,
  target.stock_ticker = source.stock_ticker,
  target.market_cap = source.market_cap,
  target.total_assets = source.total_assets,
  target.credit_rating = source.credit_rating,
  target.credit_rating_agency = source.credit_rating_agency,
  target.annual_revenue = source.annual_revenue,
  target.net_operating_income = source.net_operating_income,
  target.debt_to_equity_ratio = source.debt_to_equity_ratio,
  target.total_properties = source.total_properties,
  target.total_square_footage = source.total_square_footage,
  target.primary_property_types = source.primary_property_types,
  target.geographic_focus = source.geographic_focus,
  target.financial_health_score = source.financial_health_score,
  target.bankruptcy_risk = source.bankruptcy_risk,
  target.recent_news_sentiment = source.recent_news_sentiment,
  target.enrichment_source = source.enrichment_source,
  target.enrichment_confidence = source.enrichment_confidence,
  target.last_enriched_at = source.last_enriched_at,
  target.source_urls = source.source_urls,
  target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT *;


-- ============================================================
-- TENANT ENRICHMENT
-- ============================================================

%sql
-- Step 1: Extract unique tenants from bronze_leases that need enrichment
WITH new_tenants AS (
  SELECT DISTINCT
    REPLACE(REPLACE(LOWER(tenant_name), ' ', '_'), ',', '') AS tenant_id,
    tenant_name,
    tenant_address,
    industry_sector
  FROM ${CATALOG}.${SCHEMA}.bronze_leases
  WHERE tenant_name IS NOT NULL
    AND tenant_name NOT IN (SELECT tenant_name FROM ${CATALOG}.${SCHEMA}.tenants)
),

-- Step 2: Call MCP server to enrich tenant information
tenant_enrichment AS (
  SELECT 
    tenant_id,
    tenant_name,
    tenant_address,
    industry_sector,
    ai_query(
      '${CATALOG}.${SCHEMA}.mcp_enrichment_agent',
      CONCAT(
        'Search the web for financial and company information about this business/tenant: ',
        tenant_name,
        '. Industry: ', COALESCE(industry_sector, 'Unknown'),
        '. Address: ', COALESCE(tenant_address, 'Unknown'),
        '. Find: company type (Public/Private/Subsidiary), parent company, stock ticker, ',
        'founding year, employee count, headquarters, market cap, annual revenue, net income, ',
        'revenue growth, profit margin, credit rating, payment history, bankruptcy risk, ',
        'industry risk, recent news sentiment, and any litigation. Return structured JSON.'
      ),
      modelParameters => named_struct(
        'mcp_server_url', '__MCP_SERVER_URL__',
        'enable_web_search', true,
        'max_search_results', 5
      )
    ) AS enrichment_response
  FROM new_tenants
),

-- Step 3: Parse enrichment response
parsed_tenant_enrichment AS (
  SELECT
    tenant_id,
    tenant_name,
    tenant_address,
    industry_sector,
    from_json(
      CAST(enrichment_response.result AS STRING),
      'company_type STRING, parent_company STRING, stock_ticker STRING, founding_year INT,
       employee_count INT, headquarters_location STRING, market_cap DOUBLE, annual_revenue DOUBLE,
       net_income DOUBLE, revenue_growth_pct DOUBLE, profit_margin_pct DOUBLE,
       credit_rating STRING, credit_rating_agency STRING, duns_number STRING,
       payment_history_score DOUBLE, financial_health_score DOUBLE, bankruptcy_risk STRING,
       industry_risk STRING, recent_news_sentiment STRING, litigation_flag BOOLEAN,
       locations_count INT, years_in_business INT, source_urls ARRAY<STRING>'
    ) AS enriched,
    enrichment_response.result AS raw_response
  FROM tenant_enrichment
  WHERE enrichment_response.errorMessage IS NULL
)

-- Step 4: Insert/Update tenants table
MERGE INTO ${CATALOG}.${SCHEMA}.tenants AS target
USING (
  SELECT
    tenant_id,
    tenant_name,
    tenant_address,
    industry_sector,
    enriched.company_type,
    enriched.parent_company,
    enriched.stock_ticker,
    enriched.founding_year,
    enriched.employee_count,
    enriched.headquarters_location,
    enriched.market_cap,
    enriched.annual_revenue,
    enriched.net_income,
    enriched.revenue_growth_pct,
    enriched.profit_margin_pct,
    enriched.credit_rating,
    enriched.credit_rating_agency,
    enriched.duns_number,
    enriched.payment_history_score,
    enriched.financial_health_score,
    enriched.bankruptcy_risk,
    enriched.industry_risk,
    enriched.recent_news_sentiment,
    enriched.litigation_flag,
    enriched.locations_count,
    enriched.years_in_business,
    'MCP_WEB_SEARCH' AS enrichment_source,
    0.85 AS enrichment_confidence,
    CURRENT_TIMESTAMP() AS last_enriched_at,
    to_json(enriched.source_urls) AS source_urls
  FROM parsed_tenant_enrichment
) AS source
ON target.tenant_id = source.tenant_id
WHEN MATCHED THEN UPDATE SET
  target.company_type = source.company_type,
  target.parent_company = source.parent_company,
  target.stock_ticker = source.stock_ticker,
  target.founding_year = source.founding_year,
  target.employee_count = source.employee_count,
  target.headquarters_location = source.headquarters_location,
  target.market_cap = source.market_cap,
  target.annual_revenue = source.annual_revenue,
  target.net_income = source.net_income,
  target.revenue_growth_pct = source.revenue_growth_pct,
  target.profit_margin_pct = source.profit_margin_pct,
  target.credit_rating = source.credit_rating,
  target.credit_rating_agency = source.credit_rating_agency,
  target.duns_number = source.duns_number,
  target.payment_history_score = source.payment_history_score,
  target.financial_health_score = source.financial_health_score,
  target.bankruptcy_risk = source.bankruptcy_risk,
  target.industry_risk = source.industry_risk,
  target.recent_news_sentiment = source.recent_news_sentiment,
  target.litigation_flag = source.litigation_flag,
  target.locations_count = source.locations_count,
  target.years_in_business = source.years_in_business,
  target.enrichment_source = source.enrichment_source,
  target.enrichment_confidence = source.enrichment_confidence,
  target.last_enriched_at = source.last_enriched_at,
  target.source_urls = source.source_urls,
  target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT *;


-- ============================================================
-- UPDATE BRONZE LEASES WITH ENRICHMENT STATUS
-- ============================================================

%sql
-- Mark bronze records as enriched and link to landlord/tenant tables
UPDATE ${CATALOG}.${SCHEMA}.bronze_leases bl
SET 
  validation_status = CASE 
    WHEN validation_status = 'NEW' THEN 'ENRICHED'
    ELSE validation_status
  END
WHERE EXISTS (
  SELECT 1 FROM ${CATALOG}.${SCHEMA}.landlords l 
  WHERE REPLACE(REPLACE(LOWER(bl.landlord_name), ' ', '_'), ',', '') = l.landlord_id
)
AND EXISTS (
  SELECT 1 FROM ${CATALOG}.${SCHEMA}.tenants t 
  WHERE REPLACE(REPLACE(LOWER(bl.tenant_name), ' ', '_'), ',', '') = t.tenant_id
);

