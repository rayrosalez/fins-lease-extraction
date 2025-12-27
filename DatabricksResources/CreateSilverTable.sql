USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Drop the existing silver table (since it's empty)
--DROP TABLE IF EXISTS silver_leases;

-- Recreate with the complete schema needed for auto-promotion
CREATE TABLE silver_leases (
    -- Primary Keys
    lease_id STRING COMMENT 'Unique lease identifier (landlord_tenant_suite)',
    property_id STRING COMMENT 'Property identifier (PROP_landlord_suite)',
    
    -- Core Business Fields
    tenant_name STRING,
    industry_sector STRING COMMENT 'Normalized industry (Healthcare, Retail, etc.)',
    suite_id STRING,
    square_footage DOUBLE,
    lease_type STRING,
    lease_start_date DATE,
    lease_end_date DATE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    
    -- Calculated/Enriched Fields
    estimated_annual_rent DOUBLE COMMENT 'Calculated: square_footage * base_rent_psf',
    next_escalation_date DATE COMMENT 'Next rent escalation date',
    
    -- Audit & Governance Fields
    enhancement_source STRING COMMENT 'AI_ONLY, AI_MCP, AI_HUMAN_VERIFIED, or USER_ENTRY',
    validation_status STRING COMMENT 'PENDING, VERIFIED, or OVERRIDDEN',
    verified_by STRING COMMENT 'User who verified the record',
    verified_at TIMESTAMP COMMENT 'When the record was verified',
    raw_document_path STRING COMMENT 'Path to source PDF in Unity Catalog Volumes',
    
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