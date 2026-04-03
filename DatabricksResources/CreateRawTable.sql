USE CATALOG fins_team_3;
USE SCHEMA lease_management;

--DROP TABLE IF EXISTS fins_team_3.lease_management.raw_leases;

CREATE TABLE IF NOT EXISTS raw_leases (
    file_path STRING,
    raw_parsed_json STRING,
    ingested_at TIMESTAMP,
    trace_id STRING COMMENT 'UUID correlation ID for end-to-end pipeline tracing'
) TBLPROPERTIES (delta.enableChangeDataFeed = true);