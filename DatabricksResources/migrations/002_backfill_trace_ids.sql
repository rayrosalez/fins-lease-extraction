-- Migration 002: Backfill trace_ids for existing records that have NULL trace_id
-- Groups by uploaded_at so each upload batch gets a single shared trace_id
-- Safe to re-run: only touches rows where trace_id IS NULL

USE CATALOG ${CATALOG};
USE SCHEMA ${SCHEMA};

-- Backfill bronze_leases: one trace_id per extraction_id
MERGE INTO bronze_leases AS target
USING (
  SELECT extraction_id, UUID() as new_trace_id
  FROM bronze_leases
  WHERE trace_id IS NULL
) AS source
ON target.extraction_id = source.extraction_id
WHEN MATCHED AND target.trace_id IS NULL THEN UPDATE SET target.trace_id = source.new_trace_id;

-- Backfill silver_leases: inherit trace_id from matching bronze record
MERGE INTO silver_leases AS s
USING (
  SELECT tenant_name, landlord_name, suite_number, trace_id
  FROM bronze_leases
  WHERE trace_id IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (PARTITION BY tenant_name, landlord_name, suite_number ORDER BY uploaded_at DESC) = 1
) AS b
ON s.tenant_name = b.tenant_name
  AND s.landlord_name = b.landlord_name
  AND COALESCE(s.suite_id, '') = COALESCE(b.suite_number, '')
WHEN MATCHED AND s.trace_id IS NULL THEN UPDATE SET s.trace_id = b.trace_id;
