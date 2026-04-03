USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Drop the existing silver table (since it's empty)
--DROP TABLE IF EXISTS silver_leases;

-- Recreate with the complete schema needed for auto-promotion
CREATE TABLE IF NOT EXISTS silver_leases (
    -- Primary Keys
    lease_id STRING COMMENT 'Unique lease identifier (landlord_tenant_suite)',
    property_id STRING COMMENT 'Property identifier (PROP_landlord_suite)',
    
    -- Core Business Fields
    tenant_name STRING,
    tenant_id STRING COMMENT 'Foreign key to tenants table (derived from tenant_name)',
    landlord_name STRING COMMENT 'Name of the landlord/property owner',
    landlord_id STRING COMMENT 'Foreign key to landlords table (derived from landlord_name)',
    industry_sector STRING COMMENT 'Normalized industry (Healthcare, Retail, etc.)',
    suite_id STRING,
    square_footage DOUBLE,
    lease_type STRING,
    lease_start_date DATE,
    lease_end_date DATE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    
    -- Property Location Fields
    property_address STRING COMMENT 'Full property address',
    property_street_address STRING COMMENT 'Street address of the property',
    property_city STRING COMMENT 'City where property is located',
    property_state STRING COMMENT 'State where property is located',
    property_zip_code STRING COMMENT 'ZIP code of the property',
    property_country STRING COMMENT 'Country where property is located',
    
    -- Calculated/Enriched Fields
    estimated_annual_rent DOUBLE COMMENT 'Calculated: square_footage * base_rent_psf',
    next_escalation_date DATE COMMENT 'Next rent escalation date',
    
    -- Audit & Governance Fields
    enhancement_source STRING COMMENT 'AI_ONLY, AI_MCP, AI_HUMAN_VERIFIED, or USER_ENTRY',
    validation_status STRING COMMENT 'PENDING, VERIFIED, or OVERRIDDEN',
    verified_by STRING COMMENT 'User who verified the record',
    verified_at TIMESTAMP COMMENT 'When the record was verified',
    raw_document_path STRING COMMENT 'Path to source PDF in Unity Catalog Volumes',
    uploaded_at TIMESTAMP COMMENT 'When the document was originally uploaded',
    
    -- Traceability
    trace_id STRING COMMENT 'UUID correlation ID inherited from bronze_leases',

    -- Metadata
    updated_at TIMESTAMP COMMENT 'Last update timestamp'
) 
USING DELTA
COMMENT 'Silver layer: Verified and enriched lease data ready for analytics'
TBLPROPERTIES (
    delta.enableChangeDataFeed = true,
    delta.autoOptimize.optimizeWrite = true,
    delta.autoOptimize.autoCompact = true
);