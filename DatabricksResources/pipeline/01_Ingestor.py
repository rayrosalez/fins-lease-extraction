# Databricks notebook source
# MAGIC %md
# MAGIC # Step 1: Raw Ingestion
# MAGIC Auto Loader streams PDFs from the Unity Catalog volume, parses them with `ai_parse_document`, and writes to the `raw_leases` table.

# COMMAND ----------

dbutils.widgets.text("catalog", "REPLACE_WITH_YOUR_CATALOG", "UC Catalog")
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

from pyspark.sql.functions import col, expr, current_timestamp

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
        file_path STRING,
        raw_parsed_json STRING,
        ingested_at TIMESTAMP
    ) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# COMMAND ----------

print(f"Starting ingestion from {INPUT_VOLUME_PATH}...")

raw_stream_df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "binaryFile")
    .load(INPUT_VOLUME_PATH)
)

parsed_df = raw_stream_df.select(
    col("path").alias("file_path"),
    expr("ai_parse_document(content, map('version', '2.0'))").alias("raw_parsed_json"),
    current_timestamp().alias("ingested_at")
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
print(f"Ingestion complete. Documents are now in {TARGET_TABLE}")
