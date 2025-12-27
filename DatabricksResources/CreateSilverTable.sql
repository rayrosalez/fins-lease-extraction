USE CATALOG fins_team_3;
USE SCHEMA lease_management;

--DROP TABLE IF EXISTS fins_team_3.lease_management.silver_leases;

CREATE TABLE IF NOT EXISTS silver_leases (
    -- Primary Key for the Portfolio
    lease_id STRING, -- Standardized ID (e.g., PROP_TENANT_SUITE)
    property_id STRING,
    
    -- Cleaned & Normalized Business Fields
    tenant_name STRING,
    industry_sector STRING, -- Normalized via AI or MCP (e.g., "Healthcare", "Retail")
    suite_id STRING,
    square_footage DOUBLE,
    lease_type STRING,
    lease_start_date DATE,
    lease_end_date DATE,
    base_rent_psf DOUBLE,
    annual_escalation_pct DOUBLE,
    
    -- Financial Calculations (Generated for Forecasting)
    estimated_annual_rent DOUBLE,
    next_escalation_date DATE,
    
    -- Audit & Governance (Crucial for PE Compliance)
    enhancement_source STRING,  -- 'AI_ONLY', 'AI_MCP', or 'USER_ENTRY'
    validation_status STRING,   -- 'PENDING', 'VERIFIED', 'OVERRIDDEN'
    verified_by STRING,         -- Email of the analyst
    verified_at TIMESTAMP,
    raw_document_path STRING,   -- Path to the PDF in Unity Catalog Volumes for RAG/Genie
    
    updated_at TIMESTAMP
) 
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true);