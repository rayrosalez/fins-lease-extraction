USE CATALOG fins_team_3;
USE SCHEMA lease_management;

CREATE TABLE IF NOT EXISTS upload_trace_map (
    file_path STRING COMMENT 'Full volume path of the uploaded file',
    trace_id STRING COMMENT 'UUID correlation ID generated at upload time',
    uploaded_at TIMESTAMP COMMENT 'When the file was uploaded'
)
USING DELTA
COMMENT 'Maps uploaded file paths to trace IDs for end-to-end pipeline correlation'
TBLPROPERTIES (delta.enableChangeDataFeed = true);
