USE CATALOG ray_serverless_catalog;
USE SCHEMA lease_management;

-- Add field_confidence JSON column to bronze_leases for per-field extraction confidence scores
ALTER TABLE bronze_leases
  ADD COLUMN field_confidence STRING
  COMMENT 'JSON map of field names to confidence scores (0.0-1.0) based on extraction quality signals';

-- Create extraction_drift_baselines table for tracking weekly fill rate trends
CREATE TABLE IF NOT EXISTS extraction_drift_baselines (
  baseline_id BIGINT GENERATED ALWAYS AS IDENTITY,
  snapshot_date DATE,
  field_name STRING,
  fill_rate_pct DOUBLE,
  avg_confidence DOUBLE,
  record_count INT,
  created_at TIMESTAMP
) USING DELTA
COMMENT 'Weekly snapshots of field fill rates and confidence scores for drift detection';
