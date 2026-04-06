# Databricks notebook source
# MAGIC %md
# MAGIC # Step 2: Structure Extraction
# MAGIC Reads raw parsed documents and uses Claude to extract structured lease fields into the `bronze_leases` table.

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

sql = f"""
INSERT INTO {CATALOG}.{SCHEMA}.bronze_leases (
  uploaded_at, landlord_name, landlord_address, tenant_name, tenant_address,
  industry_sector, suite_number, lease_type, commencement_date, expiration_date,
  term_months, rentable_square_feet, annual_base_rent, base_rent_psf,
  annual_escalation_pct, renewal_notice_days, guarantor,
  property_address, property_street_address, property_city, property_state,
  property_zip_code, property_country,
  raw_json_payload, is_fully_extracted, validation_status,
  trace_id
)
WITH agent_raw_output AS (
  SELECT
    raw.file_path,
    raw.raw_parsed_json AS input,
    raw.ingested_at AS source_uploaded_at,
    raw.trace_id AS source_trace_id,
    ai_query(
      '{ENDPOINT}',
      CONCAT(
        'You are a lease extraction AI. Extract the following fields from this parsed lease document as a JSON object. ',
        'Return ONLY valid JSON with these exact keys: ',
        '{{"landlord": {{"name": "...", "address": "..."}}, ',
        '"tenant": {{"name": "...", "address": "...", "industry_sector": "..."}}, ',
        '"property_location": {{"full_address": "...", "street_address": "...", "city": "...", "state": "...", "zip_code": "...", "country": "..."}}, ',
        '"lease_details": {{"suite_number": "...", "lease_type": "...", "commencement_date": "YYYY-MM-DD", "expiration_date": "YYYY-MM-DD", "term_months": 0, "rentable_square_feet": 0}}, ',
        '"financial_terms": {{"annual_base_rent": 0, "monthly_base_rent": 0.0, "base_rent_psf": 0.0, "annual_escalation_pct": 0, "additional_rent_estimate": 0.0, "pro_rata_share": 0.0, "security_deposit": 0}}, ',
        '"risk_and_options": {{"renewal_options": "...", "renewal_notice_days": 0, "termination_rights": "...", "guarantor": "..."}}}}',
        '\\n\\nDocument content:\\n',
        CAST(raw.raw_parsed_json AS STRING)
      ),
      failOnError => false
    ) AS response
  FROM {CATALOG}.{SCHEMA}.raw_leases raw
  WHERE NOT EXISTS (
    SELECT 1
    FROM {CATALOG}.{SCHEMA}.bronze_leases bronze
    WHERE bronze.uploaded_at = raw.ingested_at
  )
  LIMIT 20
),
parsed_results AS (
  SELECT
    source_uploaded_at,
    source_trace_id,
    from_json(
      REGEXP_REPLACE(REGEXP_REPLACE(CAST(response.result AS STRING), '^```(?:json)?\\\\s*', ''), '\\\\s*```$', ''),
      '
      landlord STRUCT<name: STRING, address: STRING>,
      tenant STRUCT<name: STRING, address: STRING, industry_sector: STRING>,
      property_location STRUCT<full_address: STRING, street_address: STRING, city: STRING, state: STRING, zip_code: STRING, country: STRING>,
      lease_details STRUCT<suite_number: STRING, lease_type: STRING, commencement_date: DATE, expiration_date: DATE, term_months: INT, rentable_square_feet: INT>,
      financial_terms STRUCT<annual_base_rent: INT, monthly_base_rent: DOUBLE, base_rent_psf: DOUBLE, annual_escalation_pct: INT, additional_rent_estimate: DOUBLE, pro_rata_share: DOUBLE, security_deposit: INT>,
      risk_and_options STRUCT<renewal_options: STRING, renewal_notice_days: INT, termination_rights: STRING, guarantor: STRING>
      '
    ) as r,
    REGEXP_REPLACE(REGEXP_REPLACE(CAST(response.result AS STRING), '^```(?:json)?\\\\s*', ''), '\\\\s*```$', '') as raw_json
  FROM agent_raw_output
  WHERE response.errorMessage IS NULL
)
SELECT
  source_uploaded_at,
  r.landlord.name,
  r.landlord.address,
  r.tenant.name,
  r.tenant.address,
  r.tenant.industry_sector,
  r.lease_details.suite_number,
  r.lease_details.lease_type,
  r.lease_details.commencement_date,
  r.lease_details.expiration_date,
  r.lease_details.term_months,
  r.lease_details.rentable_square_feet,
  r.financial_terms.annual_base_rent,
  r.financial_terms.base_rent_psf,
  r.financial_terms.annual_escalation_pct,
  r.risk_and_options.renewal_notice_days,
  r.risk_and_options.guarantor,
  r.property_location.full_address,
  r.property_location.street_address,
  r.property_location.city,
  r.property_location.state,
  r.property_location.zip_code,
  r.property_location.country,
  raw_json,
  CASE
    WHEN r.tenant.name IS NULL OR r.financial_terms.annual_base_rent IS NULL THEN FALSE
    ELSE TRUE
  END as is_fully_extracted,
  'NEW' as validation_status,
  source_trace_id as trace_id
FROM parsed_results
"""

import time as _time
_struct_start = _time.time()
result = spark.sql(sql)
_struct_duration = int((_time.time() - _struct_start) * 1000)
print(f"Structuring complete. Rows inserted: {{result.first()[0] if result.first() else 'check bronze_leases'}}")

# COMMAND ----------

count = spark.sql(f"SELECT COUNT(*) as cnt FROM {CATALOG}.{SCHEMA}.bronze_leases").first()["cnt"]
print(f"Total bronze_leases records: {count}")

# COMMAND ----------

# Log pipeline events with token estimates for structured records
EVENTS_TABLE = f"{CATALOG}.{SCHEMA}.pipeline_events"

# Estimate tokens from input/output text (approx 4 chars per token)
_token_stats = spark.sql(f"""
    SELECT
        trace_id,
        COUNT(*) as cnt,
        SUM(CAST(LENGTH(raw_json_payload) / 4 AS INT)) as est_output_tokens,
        SUM(CAST(LENGTH(raw_json_payload) / 4 AS INT)) + 500 as est_total_tokens
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE trace_id IS NOT NULL AND validation_status = 'NEW'
    GROUP BY trace_id
""").collect()

# Also get input sizes from raw_leases for input token estimates
_input_stats = spark.sql(f"""
    SELECT
        trace_id,
        SUM(CAST(LENGTH(CAST(raw_parsed_json AS STRING)) / 4 AS INT)) as est_input_tokens
    FROM {CATALOG}.{SCHEMA}.raw_leases
    WHERE trace_id IS NOT NULL
    GROUP BY trace_id
""").collect()
_input_map = {r.trace_id: r.est_input_tokens for r in _input_stats if r.trace_id}

for row in _token_stats:
    if row.trace_id:
        est_input = _input_map.get(row.trace_id, 0) or 0
        est_output = row.est_output_tokens or 0
        import json as _json
        metadata = _json.dumps({
            "endpoint": ENDPOINT,
            "est_input_tokens": est_input,
            "est_output_tokens": est_output,
            "est_total_tokens": est_input + est_output,
            "token_estimation_method": "char_length_div_4"
        })
        spark.sql(f"""
            INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, duration_ms, records_affected, metadata)
            VALUES ('{row.trace_id}', 'STRUCTURE', 'COMPLETED', {_struct_duration}, {row.cnt},
                    '{metadata}')
        """)
