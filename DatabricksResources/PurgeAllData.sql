-- =============================================
-- PURGE ALL DATA - Clean Slate Script
-- =============================================
-- This script safely deletes all data from tables
-- to allow fresh data generation for testing/demo
--
-- WARNING: This will DELETE ALL DATA!
-- Run this script in Databricks SQL Editor
-- =============================================

USE CATALOG ${CATALOG};
USE SCHEMA ${SCHEMA};

-- Show current record counts before purge
SELECT '=== BEFORE PURGE ===' as status;

SELECT 'bronze_leases' as table_name, COUNT(*) as record_count FROM bronze_leases
UNION ALL
SELECT 'silver_leases', COUNT(*) FROM silver_leases
UNION ALL
SELECT 'tenants', COUNT(*) FROM tenants
UNION ALL
SELECT 'landlords', COUNT(*) FROM landlords
UNION ALL
SELECT 'gold_lease_risk_scores (view)', COUNT(*) FROM gold_lease_risk_scores;

-- =============================================
-- STEP 1: Delete from Silver Layer
-- =============================================
-- Must delete silver_leases first as it references tenants/landlords

SELECT '=== Step 1: Purging silver_leases ===' as status;
DELETE FROM silver_leases;

SELECT '[OK] Deleted all records from silver_leases' as status;

-- =============================================
-- STEP 2: Delete from Tenants Table
-- =============================================

SELECT '=== Step 2: Purging tenants ===' as status;
DELETE FROM tenants;

SELECT '[OK] Deleted all records from tenants' as status;

-- =============================================
-- STEP 3: Delete from Landlords Table
-- =============================================

SELECT '=== Step 3: Purging landlords ===' as status;
DELETE FROM landlords;

SELECT '[OK] Deleted all records from landlords' as status;

-- =============================================
-- STEP 4: Delete from Bronze Layer
-- =============================================

SELECT '=== Step 4: Purging bronze_leases ===' as status;
DELETE FROM bronze_leases;

SELECT '[OK] Deleted all records from bronze_leases' as status;

-- =============================================
-- VERIFICATION: Show counts after purge
-- =============================================

SELECT '=== AFTER PURGE ===' as status;

SELECT 'bronze_leases' as table_name, COUNT(*) as record_count FROM bronze_leases
UNION ALL
SELECT 'silver_leases', COUNT(*) FROM silver_leases
UNION ALL
SELECT 'tenants', COUNT(*) FROM tenants
UNION ALL
SELECT 'landlords', COUNT(*) FROM landlords
UNION ALL
SELECT 'gold_lease_risk_scores (view)', COUNT(*) FROM gold_lease_risk_scores;

-- =============================================
-- OPTIMIZATION: Compact Delta Tables
-- =============================================
-- After large deletes, optimize Delta tables for performance

SELECT '=== Optimizing Delta Tables ===' as status;

OPTIMIZE bronze_leases;
OPTIMIZE silver_leases;
OPTIMIZE tenants;
OPTIMIZE landlords;

SELECT '[OK] Delta tables optimized' as status;

-- =============================================
-- VACUUM (Optional - uncomment to run)
-- =============================================
-- Vacuum removes old file versions (requires retention period check)
-- Default retention is 7 days, use RETAIN 0 HOURS for immediate cleanup
-- WARNING: This is irreversible!

/*
SELECT '=== Vacuuming Delta Tables (removing old files) ===' as status;

VACUUM bronze_leases RETAIN 0 HOURS;
VACUUM silver_leases RETAIN 0 HOURS;
VACUUM tenants RETAIN 0 HOURS;
VACUUM landlords RETAIN 0 HOURS;

SELECT '[OK] Delta tables vacuumed' as status;
*/

-- =============================================
-- COMPLETE
-- =============================================

SELECT '========================================' as status
UNION ALL
SELECT 'PURGE COMPLETE!' as status
UNION ALL
SELECT '========================================' as status
UNION ALL
SELECT 'All tables are now empty.' as status
UNION ALL
SELECT 'Ready for fresh data generation.' as status
UNION ALL
SELECT '' as status
UNION ALL
SELECT 'Next steps:' as status
UNION ALL
SELECT '  1. Run: python generate_enriched_data.py' as status
UNION ALL
SELECT '  2. Generate new synthetic data' as status
UNION ALL
SELECT '  3. Verify in frontend' as status;
