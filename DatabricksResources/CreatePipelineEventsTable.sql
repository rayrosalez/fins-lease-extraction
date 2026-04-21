USE CATALOG ${CATALOG};
USE SCHEMA ${SCHEMA};

CREATE TABLE IF NOT EXISTS pipeline_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY,
    trace_id STRING COMMENT 'UUID correlation ID linking to upload_trace_map',
    stage STRING COMMENT 'Pipeline stage: UPLOAD, INGEST, STRUCTURE, ENRICH_LANDLORD, ENRICH_TENANT, PROMOTE',
    status STRING COMMENT 'Event status: STARTED, COMPLETED, FAILED, RETRIED',
    duration_ms LONG COMMENT 'Stage execution duration in milliseconds',
    records_affected INT COMMENT 'Number of records processed in this stage',
    error_message STRING COMMENT 'Error details if status is FAILED',
    metadata STRING COMMENT 'JSON blob for stage-specific metrics (tokens, field counts, model info)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When this event was recorded'
)
USING DELTA
COMMENT 'Audit log of all pipeline stage executions for monitoring and traceability'
TBLPROPERTIES (
    delta.enableChangeDataFeed = true,
    delta.autoOptimize.optimizeWrite = true
);
