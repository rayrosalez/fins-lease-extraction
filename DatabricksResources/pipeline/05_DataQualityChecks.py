# Databricks notebook source
# MAGIC %md
# MAGIC # Step 5: Data Quality Checks
# MAGIC Scheduled notebook that monitors field fill rates, enrichment staleness, validation backlog, and token cost trends.
# MAGIC Run daily or on-demand to detect data quality issues proactively.

# COMMAND ----------

dbutils.widgets.text("catalog", "REPLACE_WITH_YOUR_CATALOG", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")

print(f"Catalog: {CATALOG}")
print(f"Schema:  {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Field Fill Rates (Silver Layer)

# COMMAND ----------

fill_rates = spark.sql(f"""
SELECT
  COUNT(*) as total_records,
  ROUND(SUM(CASE WHEN tenant_name IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as tenant_name_pct,
  ROUND(SUM(CASE WHEN landlord_name IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as landlord_name_pct,
  ROUND(SUM(CASE WHEN base_rent_psf IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as rent_psf_pct,
  ROUND(SUM(CASE WHEN property_city IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as city_pct,
  ROUND(SUM(CASE WHEN property_state IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as state_pct,
  ROUND(SUM(CASE WHEN lease_end_date IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as end_date_pct,
  ROUND(SUM(CASE WHEN lease_start_date IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as start_date_pct,
  ROUND(SUM(CASE WHEN industry_sector IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as industry_pct,
  ROUND(SUM(CASE WHEN estimated_annual_rent IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as est_rent_pct
FROM {CATALOG}.{SCHEMA}.silver_leases
""")

display(fill_rates)

# Alert on any field below 80% fill rate
row = fill_rates.first()
FILL_THRESHOLD = 80.0
alerts = []
field_map = {
    "tenant_name": row.tenant_name_pct,
    "landlord_name": row.landlord_name_pct,
    "base_rent_psf": row.rent_psf_pct,
    "property_city": row.city_pct,
    "property_state": row.state_pct,
    "lease_end_date": row.end_date_pct,
    "lease_start_date": row.start_date_pct,
    "industry_sector": row.industry_pct,
    "estimated_annual_rent": row.est_rent_pct,
}

for field, pct in field_map.items():
    if pct is not None and pct < FILL_THRESHOLD:
        alerts.append(f"  ALERT: {field} fill rate is {pct}% (below {FILL_THRESHOLD}% threshold)")

if alerts:
    print("FIELD FILL RATE ALERTS:")
    for a in alerts:
        print(a)
else:
    print(f"All field fill rates are above {FILL_THRESHOLD}% threshold.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Enrichment Staleness

# COMMAND ----------

stale_landlords = spark.sql(f"""
SELECT landlord_name, last_enriched_at,
       DATEDIFF(CURRENT_DATE(), last_enriched_at) as days_stale
FROM {CATALOG}.{SCHEMA}.landlords
WHERE DATEDIFF(CURRENT_DATE(), last_enriched_at) > 30
ORDER BY days_stale DESC
""")

stale_tenants = spark.sql(f"""
SELECT tenant_name, last_enriched_at,
       DATEDIFF(CURRENT_DATE(), last_enriched_at) as days_stale
FROM {CATALOG}.{SCHEMA}.tenants
WHERE DATEDIFF(CURRENT_DATE(), last_enriched_at) > 30
ORDER BY days_stale DESC
""")

stale_ll_count = stale_landlords.count()
stale_t_count = stale_tenants.count()
print(f"Stale landlords (>30 days): {stale_ll_count}")
print(f"Stale tenants (>30 days):   {stale_t_count}")

if stale_ll_count > 0:
    print("\nStale Landlords:")
    display(stale_landlords)

if stale_t_count > 0:
    print("\nStale Tenants:")
    display(stale_tenants)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validation Backlog

# COMMAND ----------

backlog = spark.sql(f"""
SELECT validation_status, COUNT(*) as cnt
FROM {CATALOG}.{SCHEMA}.bronze_leases
GROUP BY validation_status
ORDER BY cnt DESC
""")

display(backlog)

new_count = spark.sql(f"""
SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases
WHERE validation_status = 'NEW'
""").first()[0]

if new_count > 0:
    print(f"ALERT: {new_count} records awaiting human validation in bronze_leases")
else:
    print("No records pending validation.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Pipeline Failure Rate (Last 7 Days)

# COMMAND ----------

failures = spark.sql(f"""
SELECT
  stage,
  COUNT(*) as total_events,
  SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
  SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
  ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as failure_rate_pct
FROM {CATALOG}.{SCHEMA}.pipeline_events
WHERE created_at >= date_sub(current_timestamp(), 7)
GROUP BY stage
ORDER BY failure_rate_pct DESC
""")

display(failures)

high_failure = failures.filter("failure_rate_pct > 10").collect()
if high_failure:
    print("PIPELINE FAILURE ALERTS:")
    for row in high_failure:
        print(f"  ALERT: {row.stage} has {row.failure_rate_pct}% failure rate ({row.failed}/{row.total_events} events)")
else:
    print("All pipeline stages have failure rates below 10%.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Estimated Token Usage (Cost Tracking)

# COMMAND ----------

token_usage = spark.sql(f"""
SELECT
  stage,
  COUNT(*) as events,
  SUM(CAST(get_json_object(metadata, '$.est_input_tokens') AS INT)) as total_input_tokens,
  SUM(CAST(get_json_object(metadata, '$.est_output_tokens') AS INT)) as total_output_tokens,
  SUM(CAST(get_json_object(metadata, '$.est_total_tokens') AS INT)) as total_tokens
FROM {CATALOG}.{SCHEMA}.pipeline_events
WHERE metadata IS NOT NULL
  AND get_json_object(metadata, '$.est_total_tokens') IS NOT NULL
GROUP BY stage
ORDER BY total_tokens DESC
""")

display(token_usage)

total_tokens_row = spark.sql(f"""
SELECT
  SUM(CAST(get_json_object(metadata, '$.est_total_tokens') AS INT)) as total_tokens
FROM {CATALOG}.{SCHEMA}.pipeline_events
WHERE metadata IS NOT NULL
  AND get_json_object(metadata, '$.est_total_tokens') IS NOT NULL
""").first()

total = total_tokens_row.total_tokens if total_tokens_row.total_tokens else 0
print(f"Total estimated tokens used: {total:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Summary

# COMMAND ----------

import json

summary = {
    "total_silver_records": spark.sql(f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.silver_leases").first()[0],
    "total_bronze_records": spark.sql(f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases").first()[0],
    "pending_validation": new_count,
    "stale_landlords": stale_ll_count,
    "stale_tenants": stale_t_count,
    "field_fill_alerts": len(alerts),
    "pipeline_failure_alerts": len(high_failure),
    "total_est_tokens": total,
}

print("DATA QUALITY SUMMARY")
print("=" * 40)
for k, v in summary.items():
    print(f"  {k}: {v}")

# Log the quality check run as a pipeline event
spark.sql(f"""
    INSERT INTO {CATALOG}.{SCHEMA}.pipeline_events (trace_id, stage, status, records_affected, metadata)
    VALUES (NULL, 'DATA_QUALITY_CHECK', 'COMPLETED', {summary['total_silver_records']},
            '{json.dumps(summary)}')
""")
print("\nData quality check logged to pipeline_events.")
