# Databricks notebook source
# MAGIC %md
# MAGIC # Step 3: Landlord & Tenant Enrichment
# MAGIC Uses Claude to enrich landlord and tenant records with financial profiles, then marks bronze records as enriched.

# COMMAND ----------

dbutils.widgets.text("catalog", "REPLACE_WITH_YOUR_CATALOG", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")
dbutils.widgets.text("serving_endpoint", "databricks-claude-sonnet-4-5", "Serving Endpoint")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
ENDPOINT = dbutils.widgets.get("serving_endpoint")

print(f"Catalog:  {CATALOG}")
print(f"Schema:   {SCHEMA}")
print(f"Endpoint: {ENDPOINT}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Landlord Enrichment

# COMMAND ----------

landlord_sql = f"""
MERGE INTO {CATALOG}.{SCHEMA}.landlords AS target
USING (
  WITH new_landlords AS (
    SELECT DISTINCT
      REPLACE(REPLACE(LOWER(landlord_name), ' ', '_'), ',', '') AS landlord_id,
      landlord_name,
      landlord_address
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE landlord_name IS NOT NULL
      AND landlord_name NOT IN (SELECT landlord_name FROM {CATALOG}.{SCHEMA}.landlords)
  ),
  landlord_enrichment AS (
    SELECT
      landlord_id,
      landlord_name,
      landlord_address,
      ai_query(
        '{ENDPOINT}',
        CONCAT(
          'You are a commercial real estate research analyst. Given this landlord/property owner, return a JSON object with their financial profile. ',
          'Landlord: ', landlord_name,
          '. Address: ', COALESCE(landlord_address, 'Unknown'),
          '. Return ONLY valid JSON with these exact keys: ',
          '{{"company_type": "REIT/Private/Public", "stock_ticker": "or null", "market_cap": 0.0, "total_assets": 0.0, ',
          '"credit_rating": "AAA/AA/A/BBB/BB/B or null", "credit_rating_agency": "S&P/Moodys/Fitch or null", ',
          '"annual_revenue": 0.0, "net_operating_income": 0.0, "debt_to_equity_ratio": 0.0, ',
          '"total_properties": 0, "total_square_footage": 0.0, "primary_property_types": "Office/Retail/Industrial/Mixed", ',
          '"geographic_focus": "region", "financial_health_score": 7.5, "bankruptcy_risk": "LOW/MEDIUM/HIGH", ',
          '"recent_news_sentiment": "POSITIVE/NEUTRAL/NEGATIVE"}}'
        ),
        failOnError => false
      ) AS enrichment_response
    FROM new_landlords
  ),
  parsed AS (
    SELECT
      landlord_id, landlord_name, landlord_address,
      from_json(
        CAST(enrichment_response.result AS STRING),
        'company_type STRING, stock_ticker STRING, market_cap DOUBLE, total_assets DOUBLE,
         credit_rating STRING, credit_rating_agency STRING, annual_revenue DOUBLE,
         net_operating_income DOUBLE, debt_to_equity_ratio DOUBLE, total_properties INT,
         total_square_footage DOUBLE, primary_property_types STRING, geographic_focus STRING,
         financial_health_score DOUBLE, bankruptcy_risk STRING, recent_news_sentiment STRING'
      ) AS e
    FROM landlord_enrichment
    WHERE enrichment_response.errorMessage IS NULL
  )
  SELECT
    landlord_id, landlord_name, landlord_address,
    e.company_type, e.stock_ticker, e.market_cap, e.total_assets,
    e.credit_rating, e.credit_rating_agency, e.annual_revenue,
    e.net_operating_income, e.debt_to_equity_ratio, e.total_properties,
    e.total_square_footage, e.primary_property_types, e.geographic_focus,
    e.financial_health_score, e.bankruptcy_risk, e.recent_news_sentiment,
    'AI_CLAUDE' AS enrichment_source,
    0.80 AS enrichment_confidence,
    CURRENT_TIMESTAMP() AS last_enriched_at,
    NULL AS source_urls,
    CURRENT_TIMESTAMP() AS created_at,
    CURRENT_TIMESTAMP() AS updated_at
  FROM parsed
) AS source
ON target.landlord_id = source.landlord_id
WHEN MATCHED THEN UPDATE SET
  target.company_type = source.company_type, target.stock_ticker = source.stock_ticker,
  target.market_cap = source.market_cap, target.total_assets = source.total_assets,
  target.credit_rating = source.credit_rating, target.credit_rating_agency = source.credit_rating_agency,
  target.annual_revenue = source.annual_revenue, target.net_operating_income = source.net_operating_income,
  target.debt_to_equity_ratio = source.debt_to_equity_ratio, target.total_properties = source.total_properties,
  target.total_square_footage = source.total_square_footage, target.primary_property_types = source.primary_property_types,
  target.geographic_focus = source.geographic_focus, target.financial_health_score = source.financial_health_score,
  target.bankruptcy_risk = source.bankruptcy_risk, target.recent_news_sentiment = source.recent_news_sentiment,
  target.enrichment_source = source.enrichment_source, target.enrichment_confidence = source.enrichment_confidence,
  target.last_enriched_at = source.last_enriched_at, target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT *
"""

import time as _time
EVENTS_TABLE = f"{CATALOG}.{SCHEMA}.pipeline_events"

_ll_start = _time.time()
spark.sql(landlord_sql)
_ll_duration = int((_time.time() - _ll_start) * 1000)
ll_count = spark.sql(f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.landlords").first()[0]
print(f"Landlord enrichment complete. Total landlords: {ll_count}")

# Log enrichment events per trace_id
_ll_traces = spark.sql(f"""
    SELECT DISTINCT b.trace_id
    FROM {CATALOG}.{SCHEMA}.bronze_leases b
    JOIN {CATALOG}.{SCHEMA}.landlords l
      ON REPLACE(REPLACE(LOWER(b.landlord_name), ' ', '_'), ',', '') = l.landlord_id
    WHERE b.trace_id IS NOT NULL
""").collect()
for row in _ll_traces:
    if row.trace_id:
        spark.sql(f"""
            INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, duration_ms, metadata)
            VALUES ('{row.trace_id}', 'ENRICH_LANDLORD', 'COMPLETED', {_ll_duration},
                    '{{"enrichment_source": "AI_CLAUDE", "confidence": 0.80}}')
        """)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tenant Enrichment

# COMMAND ----------

tenant_sql = f"""
MERGE INTO {CATALOG}.{SCHEMA}.tenants AS target
USING (
  WITH new_tenants AS (
    SELECT DISTINCT
      REPLACE(REPLACE(LOWER(tenant_name), ' ', '_'), ',', '') AS tenant_id,
      tenant_name,
      tenant_address,
      industry_sector
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE tenant_name IS NOT NULL
      AND tenant_name NOT IN (SELECT tenant_name FROM {CATALOG}.{SCHEMA}.tenants)
  ),
  tenant_enrichment AS (
    SELECT
      tenant_id, tenant_name, tenant_address, industry_sector,
      ai_query(
        '{ENDPOINT}',
        CONCAT(
          'You are a financial research analyst. Given this commercial tenant, return a JSON object with their financial profile. ',
          'Tenant: ', tenant_name,
          '. Industry: ', COALESCE(industry_sector, 'Unknown'),
          '. Address: ', COALESCE(tenant_address, 'Unknown'),
          '. Return ONLY valid JSON with these exact keys: ',
          '{{"company_type": "Public/Private/Subsidiary", "parent_company": "or null", "stock_ticker": "or null", ',
          '"founding_year": 2000, "employee_count": 0, "headquarters_location": "City, State", ',
          '"market_cap": 0.0, "annual_revenue": 0.0, "net_income": 0.0, ',
          '"revenue_growth_pct": 0.0, "profit_margin_pct": 0.0, ',
          '"credit_rating": "AAA/AA/A/BBB/BB/B or null", "credit_rating_agency": "S&P/Moodys/Fitch or null", ',
          '"duns_number": "or null", "payment_history_score": 85.0, ',
          '"financial_health_score": 7.5, "bankruptcy_risk": "LOW/MEDIUM/HIGH", ',
          '"industry_risk": "LOW/MEDIUM/HIGH", "recent_news_sentiment": "POSITIVE/NEUTRAL/NEGATIVE", ',
          '"litigation_flag": false, "locations_count": 0, "years_in_business": 0}}'
        ),
        failOnError => false
      ) AS enrichment_response
    FROM new_tenants
  ),
  parsed AS (
    SELECT
      tenant_id, tenant_name, tenant_address, industry_sector,
      from_json(
        CAST(enrichment_response.result AS STRING),
        'company_type STRING, parent_company STRING, stock_ticker STRING, founding_year INT,
         employee_count INT, headquarters_location STRING, market_cap DOUBLE, annual_revenue DOUBLE,
         net_income DOUBLE, revenue_growth_pct DOUBLE, profit_margin_pct DOUBLE,
         credit_rating STRING, credit_rating_agency STRING, duns_number STRING,
         payment_history_score DOUBLE, financial_health_score DOUBLE, bankruptcy_risk STRING,
         industry_risk STRING, recent_news_sentiment STRING, litigation_flag BOOLEAN,
         locations_count INT, years_in_business INT'
      ) AS e
    FROM tenant_enrichment
    WHERE enrichment_response.errorMessage IS NULL
  )
  SELECT
    tenant_id, tenant_name, tenant_address, industry_sector,
    e.company_type, e.parent_company, e.stock_ticker, e.founding_year,
    e.employee_count, e.headquarters_location, e.market_cap, e.annual_revenue,
    e.net_income, e.revenue_growth_pct, e.profit_margin_pct,
    e.credit_rating, e.credit_rating_agency, e.duns_number,
    e.payment_history_score, e.financial_health_score, e.bankruptcy_risk,
    e.industry_risk, e.recent_news_sentiment, e.litigation_flag,
    e.locations_count, e.years_in_business,
    'AI_CLAUDE' AS enrichment_source,
    0.80 AS enrichment_confidence,
    CURRENT_TIMESTAMP() AS last_enriched_at,
    NULL AS source_urls,
    CURRENT_TIMESTAMP() AS created_at,
    CURRENT_TIMESTAMP() AS updated_at
  FROM parsed
) AS source
ON target.tenant_id = source.tenant_id
WHEN MATCHED THEN UPDATE SET
  target.company_type = source.company_type, target.parent_company = source.parent_company,
  target.stock_ticker = source.stock_ticker, target.founding_year = source.founding_year,
  target.employee_count = source.employee_count, target.headquarters_location = source.headquarters_location,
  target.market_cap = source.market_cap, target.annual_revenue = source.annual_revenue,
  target.net_income = source.net_income, target.revenue_growth_pct = source.revenue_growth_pct,
  target.profit_margin_pct = source.profit_margin_pct, target.credit_rating = source.credit_rating,
  target.credit_rating_agency = source.credit_rating_agency, target.duns_number = source.duns_number,
  target.payment_history_score = source.payment_history_score, target.financial_health_score = source.financial_health_score,
  target.bankruptcy_risk = source.bankruptcy_risk, target.industry_risk = source.industry_risk,
  target.recent_news_sentiment = source.recent_news_sentiment, target.litigation_flag = source.litigation_flag,
  target.locations_count = source.locations_count, target.years_in_business = source.years_in_business,
  target.enrichment_source = source.enrichment_source, target.enrichment_confidence = source.enrichment_confidence,
  target.last_enriched_at = source.last_enriched_at, target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT *
"""

_t_start = _time.time()
spark.sql(tenant_sql)
_t_duration = int((_time.time() - _t_start) * 1000)
t_count = spark.sql(f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.tenants").first()[0]
print(f"Tenant enrichment complete. Total tenants: {t_count}")

# Log tenant enrichment events per trace_id
_t_traces = spark.sql(f"""
    SELECT DISTINCT b.trace_id
    FROM {CATALOG}.{SCHEMA}.bronze_leases b
    JOIN {CATALOG}.{SCHEMA}.tenants t
      ON REPLACE(REPLACE(LOWER(b.tenant_name), ' ', '_'), ',', '') = t.tenant_id
    WHERE b.trace_id IS NOT NULL
""").collect()
for row in _t_traces:
    if row.trace_id:
        spark.sql(f"""
            INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, duration_ms, metadata)
            VALUES ('{row.trace_id}', 'ENRICH_TENANT', 'COMPLETED', {_t_duration},
                    '{{"enrichment_source": "AI_CLAUDE", "confidence": 0.80}}')
        """)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Update Bronze Status

# COMMAND ----------

spark.sql(f"""
UPDATE {CATALOG}.{SCHEMA}.bronze_leases bl
SET validation_status = CASE
    WHEN validation_status = 'NEW' THEN 'ENRICHED'
    ELSE validation_status
  END
WHERE EXISTS (
  SELECT 1 FROM {CATALOG}.{SCHEMA}.landlords l
  WHERE REPLACE(REPLACE(LOWER(bl.landlord_name), ' ', '_'), ',', '') = l.landlord_id
)
AND EXISTS (
  SELECT 1 FROM {CATALOG}.{SCHEMA}.tenants t
  WHERE REPLACE(REPLACE(LOWER(bl.tenant_name), ' ', '_'), ',', '') = t.tenant_id
)
""")

enriched = spark.sql(f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases WHERE validation_status = 'ENRICHED'").first()[0]
print(f"Bronze records marked as ENRICHED: {enriched}")
