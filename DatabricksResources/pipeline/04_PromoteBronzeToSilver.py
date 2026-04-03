# Databricks notebook source
# MAGIC %md
# MAGIC # Step 4: Promote Bronze to Silver
# MAGIC Merges validated bronze records into the silver layer with computed fields and proper IDs.

# COMMAND ----------

dbutils.widgets.text("catalog", "ray_serverless_catalog", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

print(f"Catalog: {CATALOG}")
print(f"Schema:  {SCHEMA}")

# COMMAND ----------

import time as _time
_promote_start = _time.time()

spark.sql(f"""
MERGE INTO {CATALOG}.{SCHEMA}.silver_leases AS target
USING (
    SELECT
        CONCAT(
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(tenant_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as lease_id,

        CONCAT(
            'PROP_',
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as property_id,

        tenant_name,
        LOWER(REGEXP_REPLACE(COALESCE(tenant_name, ''), '[^a-zA-Z0-9]', '_')) as tenant_id,
        landlord_name,
        LOWER(REGEXP_REPLACE(COALESCE(landlord_name, ''), '[^a-zA-Z0-9]', '_')) as landlord_id,
        industry_sector,
        suite_number as suite_id,
        rentable_square_feet as square_footage,
        lease_type,
        commencement_date as lease_start_date,
        expiration_date as lease_end_date,
        base_rent_psf,
        annual_escalation_pct,

        property_address,
        property_street_address,
        property_city,
        property_state,
        property_zip_code,
        property_country,

        CASE
            WHEN rentable_square_feet IS NOT NULL AND base_rent_psf IS NOT NULL
            THEN rentable_square_feet * base_rent_psf
            WHEN annual_base_rent IS NOT NULL
            THEN annual_base_rent
            ELSE 0
        END as estimated_annual_rent,

        DATE_ADD(commencement_date, 365) as next_escalation_date,

        'AI_HUMAN_VERIFIED' as enhancement_source,
        'VERIFIED' as validation_status,
        'pipeline' as verified_by,
        CURRENT_TIMESTAMP() as verified_at,
        NULL as raw_document_path,
        uploaded_at,
        trace_id,
        CURRENT_TIMESTAMP() as updated_at

    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE validation_status IN ('VERIFIED', 'ENRICHED')
        AND tenant_name IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY landlord_name, tenant_name, suite_number
        ORDER BY uploaded_at DESC
    ) = 1
) AS source
ON target.lease_id = source.lease_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

# COMMAND ----------

results = spark.sql(f"""
SELECT 'Bronze (Total)' as layer, COUNT(*) as cnt FROM {CATALOG}.{SCHEMA}.bronze_leases WHERE tenant_name IS NOT NULL
UNION ALL
SELECT 'Bronze (VERIFIED/ENRICHED)', COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases WHERE validation_status IN ('VERIFIED','ENRICHED') AND tenant_name IS NOT NULL
UNION ALL
SELECT 'Bronze (NEW)', COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases WHERE validation_status = 'NEW' AND tenant_name IS NOT NULL
UNION ALL
SELECT 'Silver (Total)', COUNT(*) FROM {CATALOG}.{SCHEMA}.silver_leases
UNION ALL
SELECT 'Landlords', COUNT(*) FROM {CATALOG}.{SCHEMA}.landlords
UNION ALL
SELECT 'Tenants', COUNT(*) FROM {CATALOG}.{SCHEMA}.tenants
""")

print("Pipeline Summary:")
summary_data = results.collect()
for row in summary_data:
    print(f"  {row['layer']}: {row['cnt']}")

# Log promotion events per trace_id
_promote_duration = int((_time.time() - _promote_start) * 1000)
EVENTS_TABLE = f"{CATALOG}.{SCHEMA}.pipeline_events"
_promo_traces = spark.sql(f"""
    SELECT trace_id, COUNT(*) as cnt
    FROM {CATALOG}.{SCHEMA}.silver_leases
    WHERE trace_id IS NOT NULL
    GROUP BY trace_id
""").collect()
for row in _promo_traces:
    if row.trace_id:
        spark.sql(f"""
            INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, duration_ms, records_affected)
            VALUES ('{row.trace_id}', 'PROMOTE', 'COMPLETED', {_promote_duration}, {row.cnt})
        """)
