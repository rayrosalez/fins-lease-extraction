from pyspark.sql.functions import col, expr, current_timestamp
from pyspark.sql import SparkSession

# --- 1. Configuration ---
# Update these to match your environment setup
CATALOG = "${CATALOG}"
SCHEMA = "lease_management"
VOLUME_NAME = "raw_lease_docs"

# Paths
INPUT_VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/uploads/"
CHECKPOINT_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/pipeline_checkpoints/raw_ingestion_checkpoint/"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.raw_leases"

# --- 2. Initialize Table with Change Data Feed ---
# Enabling CDF allows Job 2 (Bronze) to only process the "new" rows incrementally.
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
        file_path STRING,
        raw_parsed_json STRING,
        ingested_at TIMESTAMP
    ) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# --- 3. The Streaming Ingestion Pipeline ---
print(f"Starting ingestion from {INPUT_VOLUME_PATH}...")

raw_stream_df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "binaryFile") # Reads the PDF as a byte array
    .load(INPUT_VOLUME_PATH)
)

# Parse logic: 
# We use ai_parse_document which is the native 2025 way to digitize PDFs.
# Note: Requires Databricks Runtime 17.1+ or Serverless compute.
parsed_df = raw_stream_df.select(
    col("path").alias("file_path"),
    # version 2.0 returns tables in HTML and uses the efficient VARIANT type
    expr("ai_parse_document(content, map('version', '2.0'))").alias("raw_parsed_json"),
    current_timestamp().alias("ingested_at")
)

# --- 4. Write to Raw Table ---
query = (
    parsed_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", CHECKPOINT_PATH)
    .option("mergeSchema", "true")  # Enable schema evolution for table updates
    # trigger(availableNow=True) makes it behave like a batch job for cost savings
    .trigger(availableNow=True) 
    .toTable(TARGET_TABLE)
)

query.awaitTermination()
print(f"Ingestion complete. Documents are now in {TARGET_TABLE}")