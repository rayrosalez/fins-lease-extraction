# Databricks notebook source
# MAGIC %md
# MAGIC # Step 6: Extraction Drift Detection
# MAGIC Tracks weekly field fill rates and average confidence scores against historical baselines.
# MAGIC Alerts when extraction quality degrades beyond configurable thresholds.
# MAGIC Run weekly (or on-demand) to catch model degradation early.

# COMMAND ----------

dbutils.widgets.text("catalog", "REPLACE_WITH_YOUR_CATALOG", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")
dbutils.widgets.text("fill_rate_threshold", "80.0", "Min acceptable fill rate (%)")
dbutils.widgets.text("drift_pct_threshold", "10.0", "Max acceptable drop from baseline (%)")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
FILL_RATE_THRESHOLD = float(dbutils.widgets.get("fill_rate_threshold"))
DRIFT_PCT_THRESHOLD = float(dbutils.widgets.get("drift_pct_threshold"))

print(f"Catalog:              {CATALOG}")
print(f"Schema:               {SCHEMA}")
print(f"Fill rate threshold:  {FILL_RATE_THRESHOLD}%")
print(f"Drift threshold:      {DRIFT_PCT_THRESHOLD}% drop from baseline")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Snapshot Current Field Fill Rates

# COMMAND ----------

TRACKED_FIELDS = [
    "tenant_name", "landlord_name", "tenant_address", "landlord_address",
    "industry_sector", "suite_number", "lease_type",
    "commencement_date", "expiration_date", "term_months",
    "rentable_square_feet", "annual_base_rent", "base_rent_psf",
    "annual_escalation_pct", "renewal_notice_days", "guarantor",
    "property_city", "property_state", "property_zip_code"
]

# Build fill rate query dynamically
fill_cases = ",\n    ".join([
    f"ROUND(SUM(CASE WHEN {f} IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as {f}_fill"
    for f in TRACKED_FIELDS
])

current_fill = spark.sql(f"""
SELECT
    COUNT(*) as total_records,
    {fill_cases}
FROM {CATALOG}.{SCHEMA}.bronze_leases
WHERE validation_status != 'DELETED'
""").first()

print(f"Total bronze records: {current_fill.total_records}")
print("\nCurrent fill rates:")
for f in TRACKED_FIELDS:
    val = getattr(current_fill, f"{f}_fill")
    flag = " << BELOW THRESHOLD" if val is not None and val < FILL_RATE_THRESHOLD else ""
    print(f"  {f:25s} {val}%{flag}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Snapshot Average Field Confidence Scores

# COMMAND ----------

# Parse field_confidence JSON and compute averages
confidence_cases = ",\n    ".join([
    f"ROUND(AVG(CAST(get_json_object(field_confidence, '$.{f}') AS DOUBLE)), 3) as {f}_conf"
    for f in TRACKED_FIELDS
])

confidence_row = spark.sql(f"""
SELECT
    COUNT(*) as records_with_confidence,
    {confidence_cases}
FROM {CATALOG}.{SCHEMA}.bronze_leases
WHERE field_confidence IS NOT NULL AND validation_status != 'DELETED'
""").first()

print(f"Records with field_confidence: {confidence_row.records_with_confidence}")
print("\nAverage confidence scores:")
for f in TRACKED_FIELDS:
    val = getattr(confidence_row, f"{f}_conf")
    display_val = f"{val}" if val is not None else "N/A"
    print(f"  {f:25s} {display_val}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Save Weekly Baseline Snapshot

# COMMAND ----------

import json

BASELINES_TABLE = f"{CATALOG}.{SCHEMA}.extraction_drift_baselines"

# Insert one row per field with current fill rate and confidence
for f in TRACKED_FIELDS:
    fill_val = getattr(current_fill, f"{f}_fill") or 0.0
    conf_val = getattr(confidence_row, f"{f}_conf") if confidence_row.records_with_confidence > 0 else None
    conf_str = str(conf_val) if conf_val is not None else "NULL"

    spark.sql(f"""
        INSERT INTO {BASELINES_TABLE} (snapshot_date, field_name, fill_rate_pct, avg_confidence, record_count, created_at)
        VALUES (CURRENT_DATE(), '{f}', {fill_val}, {conf_str}, {current_fill.total_records}, CURRENT_TIMESTAMP())
    """)

print(f"Saved {len(TRACKED_FIELDS)} baseline snapshots for {current_fill.total_records} records.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Compare Against Previous Baselines (Drift Detection)

# COMMAND ----------

# Get the most recent prior baseline (before today)
prior_baselines = spark.sql(f"""
SELECT field_name, fill_rate_pct, avg_confidence, snapshot_date
FROM {BASELINES_TABLE}
WHERE snapshot_date = (
    SELECT MAX(snapshot_date) FROM {BASELINES_TABLE}
    WHERE snapshot_date < CURRENT_DATE()
)
""").collect()

if not prior_baselines:
    print("No prior baseline found — this is the first snapshot. Drift detection will activate next run.")
else:
    prior_map = {row.field_name: row for row in prior_baselines}
    prior_date = prior_baselines[0].snapshot_date

    print(f"Comparing against baseline from {prior_date}")
    print(f"{'Field':<25} {'Prev Fill':>10} {'Curr Fill':>10} {'Change':>8} {'Status'}")
    print("-" * 75)

    drift_alerts = []
    for f in TRACKED_FIELDS:
        curr_fill = getattr(current_fill, f"{f}_fill") or 0.0
        prev = prior_map.get(f)
        if prev and prev.fill_rate_pct is not None:
            prev_fill = prev.fill_rate_pct
            change = curr_fill - prev_fill
            status = "OK"
            if change < -DRIFT_PCT_THRESHOLD:
                status = "DRIFT ALERT"
                drift_alerts.append((f, prev_fill, curr_fill, change))
            elif curr_fill < FILL_RATE_THRESHOLD:
                status = "BELOW THRESHOLD"
            print(f"  {f:<25} {prev_fill:>9.1f}% {curr_fill:>9.1f}% {change:>+7.1f}%  {status}")
        else:
            print(f"  {f:<25} {'N/A':>10} {curr_fill:>9.1f}% {'':>8}  NEW FIELD")

    if drift_alerts:
        print(f"\n{'='*75}")
        print(f"DRIFT ALERTS: {len(drift_alerts)} field(s) dropped more than {DRIFT_PCT_THRESHOLD}%")
        for f, prev_fill, curr_fill, change in drift_alerts:
            print(f"  {f}: {prev_fill:.1f}% -> {curr_fill:.1f}% ({change:+.1f}%)")
    else:
        print(f"\nNo drift detected. All fields within {DRIFT_PCT_THRESHOLD}% of baseline.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Log Drift Check Event

# COMMAND ----------

EVENTS_TABLE = f"{CATALOG}.{SCHEMA}.pipeline_events"

drift_count = len(drift_alerts) if prior_baselines else 0
below_threshold = sum(1 for f in TRACKED_FIELDS if (getattr(current_fill, f"{f}_fill") or 0) < FILL_RATE_THRESHOLD)

event_metadata = json.dumps({
    "fields_tracked": len(TRACKED_FIELDS),
    "drift_alerts": drift_count,
    "below_threshold": below_threshold,
    "fill_rate_threshold": FILL_RATE_THRESHOLD,
    "drift_pct_threshold": DRIFT_PCT_THRESHOLD,
    "baseline_date": str(prior_baselines[0].snapshot_date) if prior_baselines else None,
    "total_records": current_fill.total_records,
})

spark.sql(f"""
    INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, records_affected, metadata)
    VALUES (NULL, 'DRIFT_CHECK',
            CASE WHEN {drift_count} > 0 THEN 'ALERT' ELSE 'COMPLETED' END,
            {current_fill.total_records},
            '{event_metadata}')
""")

print(f"\nDrift check logged to pipeline_events (alerts: {drift_count}, below threshold: {below_threshold}).")
