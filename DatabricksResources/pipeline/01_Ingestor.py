# Databricks notebook source
# MAGIC %md
# MAGIC # Step 1: Raw Ingestion
# MAGIC Auto Loader streams PDFs from the Unity Catalog volume, parses them with `ai_parse_document`, and writes to the `raw_leases` table.

# COMMAND ----------

dbutils.widgets.text("catalog", "ray_serverless_catalog", "UC Catalog")
dbutils.widgets.text("schema", "lease_management", "UC Schema")
dbutils.widgets.text("volume", "raw_lease_docs", "UC Volume")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
VOLUME = dbutils.widgets.get("volume")

INPUT_VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/uploads/"
CHECKPOINT_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/pipeline_checkpoints/raw_ingestion_checkpoint/"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.raw_leases"

print(f"Catalog:    {CATALOG}")
print(f"Schema:     {SCHEMA}")
print(f"Volume:     {VOLUME}")
print(f"Input path: {INPUT_VOLUME_PATH}")
print(f"Target:     {TARGET_TABLE}")

# COMMAND ----------

from pyspark.sql.functions import col, expr, current_timestamp, element_at, split

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
        file_path STRING,
        raw_parsed_json STRING,
        ingested_at TIMESTAMP,
        trace_id STRING COMMENT 'UUID correlation ID for end-to-end pipeline tracing'
    ) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Ensure upload_trace_map exists for trace_id lookups
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.upload_trace_map (
        file_path STRING,
        trace_id STRING,
        uploaded_at TIMESTAMP
    ) USING DELTA TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# COMMAND ----------

print(f"Starting ingestion from {INPUT_VOLUME_PATH}...")

raw_stream_df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "binaryFile")
    .load(INPUT_VOLUME_PATH)
)

# Load trace_id mappings from upload_trace_map (stream-static join on filename)
trace_map_df = (
    spark.table(f"{CATALOG}.{SCHEMA}.upload_trace_map")
    .withColumn("trace_filename", element_at(split(col("file_path"), "/"), -1))
    .select("trace_filename", "trace_id")
)

parsed_df = (
    raw_stream_df.select(
        col("path").alias("file_path"),
        element_at(split(col("path"), "/"), -1).alias("stream_filename"),
        expr("ai_parse_document(content, map('version', '2.0'))").alias("raw_parsed_json"),
        current_timestamp().alias("ingested_at")
    )
    .join(trace_map_df, col("stream_filename") == col("trace_filename"), "left")
    .select("file_path", "raw_parsed_json", "ingested_at", "trace_id")
)

# COMMAND ----------

query = (
    parsed_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")
    .trigger(availableNow=True)
    .toTable(TARGET_TABLE)
)

query.awaitTermination()

# Log pipeline events for each ingested document
import time as _time
EVENTS_TABLE = f"{CATALOG}.{SCHEMA}.pipeline_events"
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {EVENTS_TABLE} (
        event_id BIGINT GENERATED ALWAYS AS IDENTITY,
        trace_id STRING, stage STRING, status STRING,
        duration_ms LONG, records_affected INT,
        error_message STRING, metadata STRING,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    ) USING DELTA TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

ingested_traces = spark.sql(f"""
    SELECT trace_id, COUNT(*) as cnt
    FROM {TARGET_TABLE}
    WHERE trace_id IS NOT NULL
    GROUP BY trace_id
""").collect()

for row in ingested_traces:
    if row.trace_id:
        spark.sql(f"""
            INSERT INTO {EVENTS_TABLE} (trace_id, stage, status, records_affected)
            VALUES ('{row.trace_id}', 'INGEST', 'COMPLETED', {row.cnt})
        """)

print(f"Ingestion complete. Documents are now in {TARGET_TABLE}")
