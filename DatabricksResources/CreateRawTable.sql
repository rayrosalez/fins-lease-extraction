USE CATALOG ${CATALOG};
USE SCHEMA ${SCHEMA};

--DROP TABLE IF EXISTS ${CATALOG}.${SCHEMA}.raw_leases;

CREATE TABLE IF NOT EXISTS raw_leases (
    file_path STRING,
    raw_parsed_json STRING,
    ingested_at TIMESTAMP
) TBLPROPERTIES (delta.enableChangeDataFeed = true);