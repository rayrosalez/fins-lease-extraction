-- ============================================
-- Promote Bronze Records to Silver Layer
-- ============================================
-- This script promotes VERIFIED bronze records to silver
-- Run this in Databricks SQL Editor or Notebook

USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Option 1: Promote ALL bronze records (regardless of validation status)
-- Uncomment this section if you want to promote everything
/*
MERGE INTO silver_leases AS target
USING (
    SELECT 
        -- Generate unique identifiers
        CONCAT(
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(tenant_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as lease_id,
        
        CONCAT(
            'PROP_',
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as property_id,
        
        -- Core business fields
        tenant_name,
        LOWER(REGEXP_REPLACE(COALESCE(tenant_name, ''), '[^a-zA-Z0-9]', '_')) as tenant_id,
        landlord_name,
        LOWER(REGEXP_REPLACE(COALESCE(landlord_name, ''), '[^a-zA-Z0-9]', '_')) as landlord_id,
        industry_sector,
        suite_number as suite_id,
        rentable_square_feet as square_footage,
        lease_type,
        commencement_date as lease_start_date,
        expiration_date as lease_end_date,
        base_rent_psf,
        annual_escalation_pct,
        
        -- Property location fields
        property_address,
        property_street_address,
        property_city,
        property_state,
        property_zip_code,
        property_country,
        
        -- Calculate estimated annual rent
        CASE 
            WHEN rentable_square_feet IS NOT NULL AND base_rent_psf IS NOT NULL 
            THEN rentable_square_feet * base_rent_psf
            WHEN annual_base_rent IS NOT NULL 
            THEN annual_base_rent
            ELSE 0
        END as estimated_annual_rent,
        
        -- Next escalation date (add 1 year to commencement)
        DATE_ADD(commencement_date, 365) as next_escalation_date,
        
        -- Audit fields
        'AI_HUMAN_VERIFIED' as enhancement_source,
        'VERIFIED' as validation_status,
        'migration_script' as verified_by,
        CURRENT_TIMESTAMP() as verified_at,
        NULL as raw_document_path,
        uploaded_at,
        CURRENT_TIMESTAMP() as updated_at,
        
        extraction_id
        
    FROM bronze_leases
    WHERE tenant_name IS NOT NULL
) AS source
ON target.lease_id = source.lease_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
*/

-- Option 2: Promote ONLY VERIFIED bronze records
-- This is the safer option - only promotes records that users have validated
MERGE INTO silver_leases AS target
USING (
    SELECT 
        -- Generate unique identifiers
        CONCAT(
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(tenant_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as lease_id,
        
        CONCAT(
            'PROP_',
            REGEXP_REPLACE(COALESCE(landlord_name, 'Unknown'), '[^a-zA-Z0-9]', '_'),
            '_',
            REGEXP_REPLACE(COALESCE(suite_number, 'Unknown'), '[^a-zA-Z0-9]', '_')
        ) as property_id,
        
        -- Core business fields
        tenant_name,
        LOWER(REGEXP_REPLACE(COALESCE(tenant_name, ''), '[^a-zA-Z0-9]', '_')) as tenant_id,
        landlord_name,
        LOWER(REGEXP_REPLACE(COALESCE(landlord_name, ''), '[^a-zA-Z0-9]', '_')) as landlord_id,
        industry_sector,
        suite_number as suite_id,
        rentable_square_feet as square_footage,
        lease_type,
        commencement_date as lease_start_date,
        expiration_date as lease_end_date,
        base_rent_psf,
        annual_escalation_pct,
        
        -- Property location fields
        property_address,
        property_street_address,
        property_city,
        property_state,
        property_zip_code,
        property_country,
        
        -- Calculate estimated annual rent
        CASE 
            WHEN rentable_square_feet IS NOT NULL AND base_rent_psf IS NOT NULL 
            THEN rentable_square_feet * base_rent_psf
            WHEN annual_base_rent IS NOT NULL 
            THEN annual_base_rent
            ELSE 0
        END as estimated_annual_rent,
        
        -- Next escalation date (add 1 year to commencement)
        DATE_ADD(commencement_date, 365) as next_escalation_date,
        
        -- Audit fields
        'AI_HUMAN_VERIFIED' as enhancement_source,
        'VERIFIED' as validation_status,
        'migration_script' as verified_by,
        CURRENT_TIMESTAMP() as verified_at,
        NULL as raw_document_path,
        uploaded_at,
        CURRENT_TIMESTAMP() as updated_at,
        
        extraction_id
        
    FROM bronze_leases
    WHERE validation_status = 'VERIFIED'
        AND tenant_name IS NOT NULL
) AS source
ON target.lease_id = source.lease_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- Check the results
SELECT 
    'Bronze (Total)' as layer,
    COUNT(*) as record_count
FROM bronze_leases
WHERE tenant_name IS NOT NULL

UNION ALL

SELECT 
    'Bronze (VERIFIED)' as layer,
    COUNT(*) as record_count
FROM bronze_leases
WHERE validation_status = 'VERIFIED'
    AND tenant_name IS NOT NULL

UNION ALL

SELECT 
    'Bronze (NEW)' as layer,
    COUNT(*) as record_count
FROM bronze_leases
WHERE validation_status = 'NEW'
    AND tenant_name IS NOT NULL

UNION ALL

SELECT 
    'Silver (Total)' as layer,
    COUNT(*) as record_count
FROM silver_leases;

