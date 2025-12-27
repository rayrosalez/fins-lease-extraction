USE CATALOG fins_team_3;
USE SCHEMA lease_management;

DROP TABLE IF EXISTS fins_team_3.lease_management.bronze_leases;

CREATE TABLE IF NOT EXISTS fins_team_3.lease_management.bronze_leases(
    extraction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    raw_source_row_id BIGINT,
    extracted_at TIMESTAMP,
    landlord_name STRING,
    tenant_name STRING,
    industry_sector STRING,
    suite_number STRING,
    lease_type STRING,
    commencement_date DATE,
    expiration_date DATE,
    term_months INT,
    rentable_square_feet DOUBLE,
    annual_base_rent DOUBLE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    renewal_notice_days INT,
    guarantor STRING,
    raw_json_payload STRING,
    is_fully_extracted BOOLEAN,
    validation_status STRING
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true, 'delta.feature.allowColumnDefaults'='supported');