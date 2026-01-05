USE CATALOG fins_team_3;
USE SCHEMA lease_management;

DROP TABLE IF EXISTS fins_team_3.lease_management.bronze_leases;

CREATE TABLE IF NOT EXISTS fins_team_3.lease_management.bronze_leases(
    extraction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    raw_source_row_id BIGINT,
    uploaded_at TIMESTAMP COMMENT 'Timestamp when file was uploaded to bronze layer',
    extracted_at TIMESTAMP COMMENT 'Timestamp when data was extracted',
    landlord_name STRING,
    landlord_address STRING COMMENT 'Full address of landlord',
    tenant_name STRING,
    tenant_address STRING COMMENT 'Full address of tenant',
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
    property_address STRING COMMENT 'Full property address',
    property_street_address STRING COMMENT 'Street address of the property',
    property_city STRING COMMENT 'City where property is located',
    property_state STRING COMMENT 'State where property is located',
    property_zip_code STRING COMMENT 'ZIP code of the property',
    property_country STRING COMMENT 'Country where property is located',
    raw_json_payload STRING,
    is_fully_extracted BOOLEAN,
    validation_status STRING
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true, 'delta.feature.allowColumnDefaults'='supported');