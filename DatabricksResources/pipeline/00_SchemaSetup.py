# Databricks notebook source
# MAGIC %md
# MAGIC # Step 0: Schema & Table Setup
# MAGIC Creates the Unity Catalog resources (catalog, schema, volume) and all tables/views
# MAGIC needed by the lease extraction pipeline. Safe to re-run — uses `IF NOT EXISTS`.

# COMMAND ----------

dbutils.widgets.text("catalog", "", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")
dbutils.widgets.text("volume", "raw_lease_docs", "UC Volume")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
VOLUME = dbutils.widgets.get("volume")

print(f"Catalog: {CATALOG}")
print(f"Schema:  {CATALOG}.{SCHEMA}")
print(f"Volume:  {CATALOG}.{SCHEMA}.{VOLUME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog, Schema & Volume

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME} COMMENT 'Raw lease PDF documents'")

# Create uploads subdirectory
dbutils.fs.mkdirs(f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/uploads")
print("Unity Catalog resources created.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Tables

# COMMAND ----------

# --- raw_leases ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.raw_leases (
    file_path STRING,
    raw_parsed_json STRING,
    ingested_at TIMESTAMP,
    trace_id STRING COMMENT 'UUID correlation ID for end-to-end pipeline tracing'
) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
print("Created: raw_leases")

# --- bronze_leases ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.bronze_leases (
    extraction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    raw_source_row_id BIGINT,
    uploaded_at TIMESTAMP COMMENT 'Timestamp when file was uploaded to bronze layer',
    extracted_at TIMESTAMP COMMENT 'Timestamp when data was extracted',
    landlord_name STRING,
    landlord_address STRING COMMENT 'Full address of landlord',
    tenant_name STRING,
    tenant_address STRING COMMENT 'Full address of tenant',
    industry_sector STRING,
    suite_number STRING,
    lease_type STRING,
    commencement_date DATE,
    expiration_date DATE,
    term_months INT,
    rentable_square_feet DOUBLE,
    annual_base_rent DOUBLE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    renewal_notice_days INT,
    guarantor STRING,
    property_address STRING COMMENT 'Full property address',
    property_street_address STRING COMMENT 'Street address of the property',
    property_city STRING COMMENT 'City where property is located',
    property_state STRING COMMENT 'State where property is located',
    property_zip_code STRING COMMENT 'ZIP code of the property',
    property_country STRING COMMENT 'Country where property is located',
    raw_json_payload STRING,
    is_fully_extracted BOOLEAN,
    validation_status STRING,
    trace_id STRING COMMENT 'UUID correlation ID inherited from raw_leases'
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true, 'delta.feature.allowColumnDefaults'='supported')
""")
print("Created: bronze_leases")

# --- silver_leases ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.silver_leases (
    lease_id STRING COMMENT 'Unique lease identifier (landlord_tenant_suite)',
    property_id STRING COMMENT 'Property identifier (PROP_landlord_suite)',
    tenant_name STRING,
    tenant_id STRING COMMENT 'Foreign key to tenants table',
    landlord_name STRING COMMENT 'Name of the landlord/property owner',
    landlord_id STRING COMMENT 'Foreign key to landlords table',
    industry_sector STRING COMMENT 'Normalized industry (Healthcare, Retail, etc.)',
    suite_id STRING,
    square_footage DOUBLE,
    lease_type STRING,
    lease_start_date DATE,
    lease_end_date DATE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    property_address STRING COMMENT 'Full property address',
    property_street_address STRING COMMENT 'Street address of the property',
    property_city STRING COMMENT 'City where property is located',
    property_state STRING COMMENT 'State where property is located',
    property_zip_code STRING COMMENT 'ZIP code of the property',
    property_country STRING COMMENT 'Country where property is located',
    estimated_annual_rent DOUBLE COMMENT 'Calculated: square_footage * base_rent_psf',
    next_escalation_date DATE COMMENT 'Next rent escalation date',
    enhancement_source STRING COMMENT 'AI_ONLY, AI_MCP, AI_HUMAN_VERIFIED, or USER_ENTRY',
    validation_status STRING COMMENT 'PENDING, VERIFIED, or OVERRIDDEN',
    verified_by STRING COMMENT 'User who verified the record',
    verified_at TIMESTAMP COMMENT 'When the record was verified',
    raw_document_path STRING COMMENT 'Path to source PDF in Unity Catalog Volumes',
    uploaded_at TIMESTAMP COMMENT 'When the document was originally uploaded',
    trace_id STRING COMMENT 'UUID correlation ID inherited from bronze_leases',
    updated_at TIMESTAMP COMMENT 'Last update timestamp'
)
USING DELTA
COMMENT 'Silver layer: Verified and enriched lease data ready for analytics'
TBLPROPERTIES (
    delta.enableChangeDataFeed = true,
    delta.autoOptimize.optimizeWrite = true,
    delta.autoOptimize.autoCompact = true
)
""")
print("Created: silver_leases")

# --- landlords ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.landlords (
    landlord_id STRING NOT NULL COMMENT 'Unique identifier for landlord',
    landlord_name STRING COMMENT 'Legal name of the landlord/property owner',
    landlord_address STRING COMMENT 'Primary business address',
    company_type STRING COMMENT 'REIT, Private, Public, etc.',
    stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
    market_cap DOUBLE COMMENT 'Market capitalization in USD',
    total_assets DOUBLE COMMENT 'Total assets under management in USD',
    credit_rating STRING COMMENT 'Credit rating (e.g., AAA, BBB+)',
    credit_rating_agency STRING COMMENT 'Rating agency',
    annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
    net_operating_income DOUBLE COMMENT 'NOI in USD',
    debt_to_equity_ratio DOUBLE COMMENT 'D/E ratio',
    total_properties INT COMMENT 'Total number of properties owned',
    total_square_footage DOUBLE COMMENT 'Total portfolio square footage',
    primary_property_types STRING COMMENT 'Main property types',
    geographic_focus STRING COMMENT 'Primary geographic markets',
    financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
    bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
    recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE',
    enrichment_source STRING COMMENT 'MCP_WEB_SEARCH, MANUAL, API',
    enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
    last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
    source_urls STRING COMMENT 'JSON array of source URLs',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP,
    CONSTRAINT landlords_pk PRIMARY KEY (landlord_id)
)
USING DELTA
COMMENT 'Landlord master table with financial profiles enriched via MCP web search'
TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
print("Created: landlords")

# --- tenants ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.tenants (
    tenant_id STRING NOT NULL COMMENT 'Unique identifier for tenant',
    tenant_name STRING COMMENT 'Legal name of the tenant',
    tenant_address STRING COMMENT 'Headquarters or primary business address',
    industry_sector STRING COMMENT 'Primary industry sector',
    company_type STRING COMMENT 'Public, Private, Subsidiary, Non-profit',
    parent_company STRING COMMENT 'Parent company if subsidiary',
    stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
    founding_year INT COMMENT 'Year company was founded',
    employee_count INT COMMENT 'Approximate number of employees',
    headquarters_location STRING COMMENT 'HQ city and state',
    market_cap DOUBLE COMMENT 'Market capitalization in USD (if public)',
    annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
    net_income DOUBLE COMMENT 'Net income in USD',
    revenue_growth_pct DOUBLE COMMENT 'Year-over-year revenue growth percent',
    profit_margin_pct DOUBLE COMMENT 'Profit margin percentage',
    credit_rating STRING COMMENT 'Credit rating',
    credit_rating_agency STRING COMMENT 'Rating agency',
    duns_number STRING COMMENT 'D&B DUNS number',
    payment_history_score DOUBLE COMMENT 'Payment history score (1-100)',
    financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
    bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
    industry_risk STRING COMMENT 'LOW, MEDIUM, HIGH based on sector volatility',
    recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE',
    litigation_flag BOOLEAN COMMENT 'True if significant ongoing litigation found',
    locations_count INT COMMENT 'Number of business locations',
    years_in_business INT COMMENT 'Years the company has been operating',
    enrichment_source STRING COMMENT 'MCP_WEB_SEARCH, MANUAL, API',
    enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
    last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
    source_urls STRING COMMENT 'JSON array of source URLs',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP,
    CONSTRAINT tenants_pk PRIMARY KEY (tenant_id)
)
USING DELTA
COMMENT 'Tenant master table with financial profiles enriched via MCP web search'
TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
print("Created: tenants")

# --- upload_trace_map ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.upload_trace_map (
    file_path STRING COMMENT 'Full volume path of the uploaded file',
    trace_id STRING COMMENT 'UUID correlation ID generated at upload time',
    uploaded_at TIMESTAMP COMMENT 'When the file was uploaded'
)
USING DELTA
COMMENT 'Maps uploaded file paths to trace IDs for end-to-end pipeline correlation'
TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
print("Created: upload_trace_map")

# --- pipeline_events ---
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.pipeline_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY,
    trace_id STRING COMMENT 'UUID correlation ID linking to upload_trace_map',
    stage STRING COMMENT 'Pipeline stage: UPLOAD, INGEST, STRUCTURE, ENRICH_LANDLORD, ENRICH_TENANT, PROMOTE',
    status STRING COMMENT 'Event status: STARTED, COMPLETED, FAILED, RETRIED',
    duration_ms LONG COMMENT 'Stage execution duration in milliseconds',
    records_affected INT COMMENT 'Number of records processed in this stage',
    error_message STRING COMMENT 'Error details if status is FAILED',
    metadata STRING COMMENT 'JSON blob for stage-specific metrics',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When this event was recorded'
)
USING DELTA
COMMENT 'Audit log of all pipeline stage executions for monitoring and traceability'
TBLPROPERTIES (
    delta.enableChangeDataFeed = true,
    delta.autoOptimize.optimizeWrite = true
)
""")
print("Created: pipeline_events")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Gold View (Risk Scores)

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.gold_lease_risk_scores AS
WITH enriched_leases AS (
  SELECT
    l.lease_id, l.tenant_name, l.tenant_id, l.landlord_name, l.landlord_id,
    l.property_id, l.industry_sector, l.lease_end_date, l.annual_escalation_pct,
    l.estimated_annual_rent, l.square_footage,
    t.financial_health_score as tenant_health_score,
    t.credit_rating as tenant_credit_rating,
    t.bankruptcy_risk as tenant_bankruptcy_risk,
    t.industry_risk as tenant_industry_risk,
    t.payment_history_score as tenant_payment_score,
    t.market_cap as tenant_market_cap,
    t.annual_revenue as tenant_revenue,
    t.enrichment_confidence as tenant_enrichment_confidence,
    ll.financial_health_score as landlord_health_score,
    ll.credit_rating as landlord_credit_rating,
    ll.bankruptcy_risk as landlord_bankruptcy_risk,
    ll.debt_to_equity_ratio as landlord_debt_to_equity,
    ll.enrichment_confidence as landlord_enrichment_confidence,
    CASE WHEN t.tenant_id IS NOT NULL THEN TRUE ELSE FALSE END as has_tenant_enrichment,
    CASE WHEN ll.landlord_id IS NOT NULL THEN TRUE ELSE FALSE END as has_landlord_enrichment
  FROM {CATALOG}.{SCHEMA}.silver_leases l
  LEFT JOIN {CATALOG}.{SCHEMA}.tenants t ON l.tenant_id = t.tenant_id
  LEFT JOIN {CATALOG}.{SCHEMA}.landlords ll ON l.landlord_id = ll.landlord_id
  WHERE l.lease_end_date IS NOT NULL
),
risk_calcs AS (
  SELECT *,
    DATEDIFF(lease_end_date, CURRENT_DATE()) as days_to_expiry,
    CASE
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'HIGH' THEN 80
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'MEDIUM' THEN 50
      WHEN has_tenant_enrichment AND tenant_industry_risk = 'LOW' THEN 20
      WHEN industry_sector IN ('Retail', 'Restaurant') THEN 80
      WHEN industry_sector IN ('Tech', 'Office') THEN 50
      WHEN industry_sector IN ('Healthcare', 'Government') THEN 20
      ELSE 40
    END as sector_risk_base,
    estimated_annual_rent / NULLIF(SUM(estimated_annual_rent) OVER (), 0) * 100 as portfolio_concentration_pct,
    CASE
      WHEN has_tenant_enrichment AND tenant_health_score IS NOT NULL THEN
        ROUND(100 - ((tenant_health_score - 1) / 9.0) * 100, 2)
      ELSE 50
    END as tenant_credit_risk_score,
    CASE
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'HIGH' THEN 90
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'MEDIUM' THEN 50
      WHEN has_tenant_enrichment AND tenant_bankruptcy_risk = 'LOW' THEN 10
      ELSE 40
    END as tenant_bankruptcy_risk_score,
    CASE
      WHEN has_landlord_enrichment AND landlord_health_score IS NOT NULL THEN
        ROUND(100 - ((landlord_health_score - 1) / 9.0) * 100, 2)
      ELSE 30
    END as landlord_risk_score
  FROM enriched_leases
)
SELECT
  lease_id, tenant_name, tenant_id, landlord_name, landlord_id,
  property_id, industry_sector, lease_end_date, annual_escalation_pct,
  estimated_annual_rent, square_footage, days_to_expiry, sector_risk_base,
  portfolio_concentration_pct,
  has_tenant_enrichment, has_landlord_enrichment,
  tenant_health_score, tenant_credit_rating, tenant_bankruptcy_risk,
  tenant_payment_score, tenant_enrichment_confidence,
  landlord_health_score, landlord_credit_rating, landlord_bankruptcy_risk,
  landlord_debt_to_equity, landlord_enrichment_confidence,
  tenant_credit_risk_score, tenant_bankruptcy_risk_score, landlord_risk_score,
  -- Rollover risk
  CASE
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
  END as rollover_score,
  -- Escalation risk
  CASE
    WHEN annual_escalation_pct IS NULL THEN 50
    WHEN annual_escalation_pct < 2.0 THEN 80
    WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50
    WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30
    WHEN annual_escalation_pct >= 4.0 THEN 20
    ELSE 40
  END as escalation_risk_score,
  -- Concentration risk
  CASE
    WHEN portfolio_concentration_pct >= 10.0 THEN 90
    WHEN portfolio_concentration_pct >= 5.0 THEN 70
    WHEN portfolio_concentration_pct >= 2.0 THEN 40
    WHEN portfolio_concentration_pct >= 1.0 THEN 20
    ELSE 10
  END as concentration_risk_score,
  -- Lease status
  CASE
    WHEN days_to_expiry < -365 THEN 'EXPIRED_OLD'
    WHEN days_to_expiry < 0 THEN 'EXPIRED_RECENT'
    WHEN days_to_expiry <= 90 THEN 'CRITICAL'
    WHEN days_to_expiry <= 180 THEN 'HIGH_PRIORITY'
    WHEN days_to_expiry <= 365 THEN 'NEEDS_ATTENTION'
    WHEN days_to_expiry <= 730 THEN 'MONITOR'
    ELSE 'STABLE'
  END as lease_status,
  -- Weighted total risk score
  CASE
    WHEN has_tenant_enrichment AND has_landlord_enrichment THEN
      ROUND(
        (CASE WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100 WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90 WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75 WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40 WHEN days_to_expiry > 730 THEN 10 WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85 WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60 WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35 WHEN days_to_expiry < -365 THEN 5 ELSE 0 END * 0.25) +
        (CASE WHEN annual_escalation_pct IS NULL THEN 50 WHEN annual_escalation_pct < 2.0 THEN 80 WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50 WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30 WHEN annual_escalation_pct >= 4.0 THEN 20 ELSE 40 END * 0.10) +
        (sector_risk_base * 0.10) + (CASE WHEN portfolio_concentration_pct >= 10.0 THEN 90 WHEN portfolio_concentration_pct >= 5.0 THEN 70 WHEN portfolio_concentration_pct >= 2.0 THEN 40 WHEN portfolio_concentration_pct >= 1.0 THEN 20 ELSE 10 END * 0.15) +
        (tenant_credit_risk_score * 0.20) + (tenant_bankruptcy_risk_score * 0.10) + (landlord_risk_score * 0.10), 2)
    WHEN has_tenant_enrichment AND NOT has_landlord_enrichment THEN
      ROUND(
        (CASE WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100 WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90 WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75 WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40 WHEN days_to_expiry > 730 THEN 10 WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85 WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60 WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35 WHEN days_to_expiry < -365 THEN 5 ELSE 0 END * 0.30) +
        (CASE WHEN annual_escalation_pct IS NULL THEN 50 WHEN annual_escalation_pct < 2.0 THEN 80 WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50 WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30 WHEN annual_escalation_pct >= 4.0 THEN 20 ELSE 40 END * 0.15) +
        (sector_risk_base * 0.10) + (CASE WHEN portfolio_concentration_pct >= 10.0 THEN 90 WHEN portfolio_concentration_pct >= 5.0 THEN 70 WHEN portfolio_concentration_pct >= 2.0 THEN 40 WHEN portfolio_concentration_pct >= 1.0 THEN 20 ELSE 10 END * 0.15) +
        (tenant_credit_risk_score * 0.20) + (tenant_bankruptcy_risk_score * 0.10), 2)
    WHEN NOT has_tenant_enrichment AND has_landlord_enrichment THEN
      ROUND(
        (CASE WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100 WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90 WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75 WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40 WHEN days_to_expiry > 730 THEN 10 WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85 WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60 WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35 WHEN days_to_expiry < -365 THEN 5 ELSE 0 END * 0.35) +
        (CASE WHEN annual_escalation_pct IS NULL THEN 50 WHEN annual_escalation_pct < 2.0 THEN 80 WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50 WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30 WHEN annual_escalation_pct >= 4.0 THEN 20 ELSE 40 END * 0.15) +
        (sector_risk_base * 0.15) + (CASE WHEN portfolio_concentration_pct >= 10.0 THEN 90 WHEN portfolio_concentration_pct >= 5.0 THEN 70 WHEN portfolio_concentration_pct >= 2.0 THEN 40 WHEN portfolio_concentration_pct >= 1.0 THEN 20 ELSE 10 END * 0.20) +
        (landlord_risk_score * 0.15), 2)
    ELSE
      ROUND(
        (CASE WHEN days_to_expiry >= 0 AND days_to_expiry <= 90 THEN 100 WHEN days_to_expiry > 90 AND days_to_expiry <= 180 THEN 90 WHEN days_to_expiry > 180 AND days_to_expiry <= 365 THEN 75 WHEN days_to_expiry > 365 AND days_to_expiry <= 730 THEN 40 WHEN days_to_expiry > 730 THEN 10 WHEN days_to_expiry >= -90 AND days_to_expiry < 0 THEN 85 WHEN days_to_expiry >= -180 AND days_to_expiry < -90 THEN 60 WHEN days_to_expiry >= -365 AND days_to_expiry < -180 THEN 35 WHEN days_to_expiry < -365 THEN 5 ELSE 0 END * 0.40) +
        (CASE WHEN annual_escalation_pct IS NULL THEN 50 WHEN annual_escalation_pct < 2.0 THEN 80 WHEN annual_escalation_pct >= 2.0 AND annual_escalation_pct < 3.0 THEN 50 WHEN annual_escalation_pct >= 3.0 AND annual_escalation_pct < 4.0 THEN 30 WHEN annual_escalation_pct >= 4.0 THEN 20 ELSE 40 END * 0.20) +
        (sector_risk_base * 0.20) + (CASE WHEN portfolio_concentration_pct >= 10.0 THEN 90 WHEN portfolio_concentration_pct >= 5.0 THEN 70 WHEN portfolio_concentration_pct >= 2.0 THEN 40 WHEN portfolio_concentration_pct >= 1.0 THEN 20 ELSE 10 END * 0.20), 2)
  END AS total_risk_score,
  -- Risk model indicator
  CASE
    WHEN has_tenant_enrichment AND has_landlord_enrichment THEN 'FULLY_ENRICHED'
    WHEN has_tenant_enrichment AND NOT has_landlord_enrichment THEN 'TENANT_ENRICHED'
    WHEN NOT has_tenant_enrichment AND has_landlord_enrichment THEN 'LANDLORD_ENRICHED'
    ELSE 'BASIC'
  END as risk_model_used
FROM risk_calcs
ORDER BY total_risk_score DESC, days_to_expiry ASC
""")
print("Created: gold_lease_risk_scores (view)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create AI/BI Metric Views

# COMMAND ----------

# Portfolio lease metrics
spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.portfolio_lease_metrics
  (
    market COMMENT 'Industry sector/market segment',
    city COMMENT 'Property city location',
    state COMMENT 'Property state location',
    lease_status COMMENT 'Current validation status',
    total_leases COMMENT 'Count of active leases',
    total_sqft COMMENT 'Total leased square footage',
    total_annual_rent COMMENT 'Total estimated annual rent',
    avg_rent_psf COMMENT 'Average rent per square foot',
    avg_years_remaining COMMENT 'Average remaining lease term',
    expiring_90_days COMMENT 'Leases expiring within 90 days',
    expiring_180_days COMMENT 'Leases expiring within 180 days',
    expiring_365_days COMMENT 'Leases expiring within 365 days'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Portfolio-wide lease metrics for CRE analytics.'
  AS $$
    version: 1.1
    source: {CATALOG}.{SCHEMA}.silver_leases
    filter: tenant_name IS NOT NULL
    dimensions:
      - name: market
        expr: COALESCE(industry_sector, 'Unknown')
      - name: city
        expr: COALESCE(property_city, 'Unknown')
      - name: state
        expr: COALESCE(property_state, 'Unknown')
      - name: lease_status
        expr: validation_status
    measures:
      - name: total_leases
        expr: COUNT(1)
      - name: total_sqft
        expr: CAST(SUM(square_footage) AS DOUBLE)
      - name: total_annual_rent
        expr: CAST(SUM(estimated_annual_rent) AS DOUBLE)
      - name: avg_rent_psf
        expr: CAST(AVG(base_rent_psf) AS DOUBLE)
      - name: avg_years_remaining
        expr: CAST(AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25) AS DOUBLE)
      - name: expiring_90_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 90)
      - name: expiring_180_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 180)
      - name: expiring_365_days
        expr: COUNT(1) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND 365)
  $$
""")
print("Created: portfolio_lease_metrics (metric view)")

# Risk assessment metrics
spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.risk_assessment_metrics
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
  COMMENT 'Lease risk assessment metrics with multi-factor scoring.'
  AS $$
    version: 1.1
    source: {CATALOG}.{SCHEMA}.gold_lease_risk_scores
    filter: total_risk_score IS NOT NULL
    dimensions:
      - name: industry_sector
        expr: COALESCE(industry_sector, 'Unknown')
      - name: lease_status
        expr: lease_status
      - name: risk_category
        expr: "CASE WHEN total_risk_score >= 80 THEN 'Critical (80-100)' WHEN total_risk_score >= 60 THEN 'High (60-79)' WHEN total_risk_score >= 40 THEN 'Medium (40-59)' WHEN total_risk_score >= 20 THEN 'Low (20-39)' ELSE 'Minimal (0-19)' END"
    measures:
      - name: total_leases
        expr: COUNT(1)
      - name: avg_risk_score
        expr: CAST(AVG(total_risk_score) AS DOUBLE)
      - name: total_rent_at_risk
        expr: CAST(SUM(estimated_annual_rent) AS DOUBLE)
      - name: high_risk_rent
        expr: CAST(SUM(estimated_annual_rent) FILTER (WHERE total_risk_score > 70) AS DOUBLE)
      - name: critical_lease_count
        expr: COUNT(1) FILTER (WHERE lease_status = 'CRITICAL')
      - name: high_priority_count
        expr: COUNT(1) FILTER (WHERE lease_status = 'HIGH_PRIORITY')
      - name: avg_rollover_risk
        expr: CAST(AVG(rollover_score) AS DOUBLE)
      - name: avg_escalation_risk
        expr: CAST(AVG(escalation_risk_score) AS DOUBLE)
      - name: avg_concentration_risk
        expr: CAST(AVG(concentration_risk_score) AS DOUBLE)
      - name: avg_industry_risk
        expr: CAST(AVG(sector_risk_base) AS DOUBLE)
      - name: avg_days_to_expiry
        expr: CAST(AVG(days_to_expiry) AS DOUBLE)
  $$
""")
print("Created: risk_assessment_metrics (metric view)")

# Landlord metrics
spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.landlord_metrics
  (
    company_type COMMENT 'Company classification',
    bankruptcy_risk COMMENT 'Risk level (LOW, MEDIUM, HIGH)',
    news_sentiment COMMENT 'Recent news sentiment',
    credit_rating_tier COMMENT 'Credit rating tier',
    total_landlords COMMENT 'Count of landlord entities',
    total_revenue COMMENT 'Sum of annual revenue',
    total_assets COMMENT 'Sum of total assets',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    total_properties COMMENT 'Sum of properties owned',
    avg_market_cap COMMENT 'Average market capitalization',
    avg_debt_to_equity COMMENT 'Average debt-to-equity ratio',
    low_risk_count COMMENT 'LOW bankruptcy risk count',
    medium_risk_count COMMENT 'MEDIUM bankruptcy risk count',
    high_risk_count COMMENT 'HIGH bankruptcy risk count',
    positive_sentiment_count COMMENT 'POSITIVE sentiment count',
    negative_sentiment_count COMMENT 'NEGATIVE sentiment count'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Landlord financial and risk metrics.'
  AS $$
    version: 1.1
    source: {CATALOG}.{SCHEMA}.landlords
    dimensions:
      - name: company_type
        expr: COALESCE(company_type, 'Unknown')
      - name: bankruptcy_risk
        expr: COALESCE(bankruptcy_risk, 'Unknown')
      - name: news_sentiment
        expr: COALESCE(recent_news_sentiment, 'Unknown')
      - name: credit_rating_tier
        expr: "CASE WHEN credit_rating IN ('AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-') THEN 'Investment Grade' WHEN credit_rating IN ('BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D') THEN 'High Yield' ELSE 'Not Rated' END"
    measures:
      - name: total_landlords
        expr: COUNT(1)
      - name: total_revenue
        expr: CAST(SUM(annual_revenue) AS DOUBLE)
      - name: total_assets
        expr: CAST(SUM(total_assets) AS DOUBLE)
      - name: avg_health_score
        expr: CAST(AVG(financial_health_score) AS DOUBLE)
      - name: total_properties
        expr: CAST(SUM(total_properties) AS DOUBLE)
      - name: avg_market_cap
        expr: CAST(AVG(market_cap) AS DOUBLE)
      - name: avg_debt_to_equity
        expr: CAST(AVG(debt_to_equity_ratio) AS DOUBLE)
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
  $$
""")
print("Created: landlord_metrics (metric view)")

# Tenant metrics
spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.tenant_metrics
  (
    industry_sector COMMENT 'Primary industry sector',
    company_type COMMENT 'Company classification',
    bankruptcy_risk COMMENT 'Risk level',
    industry_risk COMMENT 'Industry volatility risk',
    company_size COMMENT 'Size category based on employees',
    total_tenants COMMENT 'Count of tenant entities',
    total_revenue COMMENT 'Sum of annual revenue',
    avg_health_score COMMENT 'Average financial health score (1-10)',
    avg_employee_count COMMENT 'Average employee count',
    avg_revenue_growth COMMENT 'Average revenue growth percent',
    avg_profit_margin COMMENT 'Average profit margin percent',
    growing_companies COMMENT 'Positive revenue growth count',
    declining_companies COMMENT 'Negative revenue growth count',
    low_risk_count COMMENT 'LOW bankruptcy risk count',
    medium_risk_count COMMENT 'MEDIUM bankruptcy risk count',
    high_risk_count COMMENT 'HIGH bankruptcy risk count',
    litigation_count COMMENT 'Active litigation count'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Commercial tenant financial and risk metrics.'
  AS $$
    version: 1.1
    source: {CATALOG}.{SCHEMA}.tenants
    dimensions:
      - name: industry_sector
        expr: COALESCE(industry_sector, 'Unknown')
      - name: company_type
        expr: COALESCE(company_type, 'Unknown')
      - name: bankruptcy_risk
        expr: COALESCE(bankruptcy_risk, 'Unknown')
      - name: industry_risk
        expr: COALESCE(industry_risk, 'Unknown')
      - name: company_size
        expr: "CASE WHEN COALESCE(employee_count, 0) < 100 THEN 'Small (<100)' WHEN employee_count >= 100 AND employee_count < 1000 THEN 'Medium (100-1K)' WHEN employee_count >= 1000 AND employee_count < 10000 THEN 'Large (1K-10K)' ELSE 'Enterprise (10K+)' END"
    measures:
      - name: total_tenants
        expr: COUNT(1)
      - name: total_revenue
        expr: CAST(SUM(annual_revenue) AS DOUBLE)
      - name: avg_health_score
        expr: CAST(AVG(financial_health_score) AS DOUBLE)
      - name: avg_employee_count
        expr: CAST(AVG(employee_count) AS DOUBLE)
      - name: avg_revenue_growth
        expr: CAST(AVG(revenue_growth_pct) AS DOUBLE)
      - name: avg_profit_margin
        expr: CAST(AVG(profit_margin_pct) AS DOUBLE)
      - name: growing_companies
        expr: COUNT(1) FILTER (WHERE revenue_growth_pct > 0)
      - name: declining_companies
        expr: COUNT(1) FILTER (WHERE revenue_growth_pct < 0)
      - name: low_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'LOW')
      - name: medium_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'MEDIUM')
      - name: high_risk_count
        expr: COUNT(1) FILTER (WHERE bankruptcy_risk = 'HIGH')
      - name: litigation_count
        expr: COUNT(1) FILTER (WHERE litigation_flag = TRUE)
  $$
""")
print("Created: tenant_metrics (metric view)")

# Market performance metrics
spark.sql(f"""
CREATE OR REPLACE VIEW {CATALOG}.{SCHEMA}.market_performance_metrics
  (
    market COMMENT 'Industry sector/market segment',
    city COMMENT 'Property city',
    state COMMENT 'Property state',
    region COMMENT 'Geographic region',
    property_count COMMENT 'Count of unique properties',
    lease_count COMMENT 'Total number of leases',
    total_sqft COMMENT 'Total square footage',
    total_annual_rent COMMENT 'Total annual rental income',
    avg_rent_psf COMMENT 'Average rent per square foot',
    min_rent_psf COMMENT 'Minimum rent PSF',
    max_rent_psf COMMENT 'Maximum rent PSF',
    walt_years COMMENT 'Weighted Average Lease Term',
    avg_lease_size COMMENT 'Average lease square footage',
    occupancy_value COMMENT 'Total occupied rent value'
  )
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'Market-level performance metrics for portfolio analysis.'
  AS $$
    version: 1.1
    source: {CATALOG}.{SCHEMA}.silver_leases
    filter: tenant_name IS NOT NULL AND lease_end_date IS NOT NULL
    dimensions:
      - name: market
        expr: COALESCE(industry_sector, 'Unknown')
      - name: city
        expr: COALESCE(property_city, 'Unknown')
      - name: state
        expr: COALESCE(property_state, 'Unknown')
      - name: region
        expr: "CASE WHEN property_state IN ('CA', 'WA', 'OR', 'NV', 'AZ') THEN 'West' WHEN property_state IN ('TX', 'OK', 'NM', 'AR', 'LA') THEN 'Southwest' WHEN property_state IN ('NY', 'NJ', 'PA', 'CT', 'MA', 'NH', 'VT', 'ME', 'RI') THEN 'Northeast' WHEN property_state IN ('FL', 'GA', 'NC', 'SC', 'VA', 'TN', 'AL', 'MS') THEN 'Southeast' WHEN property_state IN ('IL', 'OH', 'MI', 'IN', 'WI', 'MN', 'IA', 'MO') THEN 'Midwest' WHEN property_state IN ('CO', 'UT', 'WY', 'MT', 'ID') THEN 'Mountain' ELSE 'Other' END"
    measures:
      - name: property_count
        expr: COUNT(DISTINCT property_id)
      - name: lease_count
        expr: COUNT(1)
      - name: total_sqft
        expr: CAST(SUM(square_footage) AS DOUBLE)
      - name: total_annual_rent
        expr: CAST(SUM(estimated_annual_rent) AS DOUBLE)
      - name: avg_rent_psf
        expr: CAST(AVG(base_rent_psf) AS DOUBLE)
      - name: min_rent_psf
        expr: CAST(MIN(base_rent_psf) AS DOUBLE)
      - name: max_rent_psf
        expr: CAST(MAX(base_rent_psf) AS DOUBLE)
      - name: walt_years
        expr: "CAST(SUM(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25 * estimated_annual_rent) / NULLIF(SUM(estimated_annual_rent), 0) AS DOUBLE)"
      - name: avg_lease_size
        expr: CAST(AVG(square_footage) AS DOUBLE)
      - name: occupancy_value
        expr: CAST(SUM(estimated_annual_rent) FILTER (WHERE DATEDIFF(lease_end_date, CURRENT_DATE()) > 0) AS DOUBLE)
  $$
""")
print("Created: market_performance_metrics (metric view)")

# COMMAND ----------

print("Schema setup complete!")
