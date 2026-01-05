"""
Promote Verified Bronze Records to Silver Layer
================================================

Automatically promotes all VERIFIED bronze records to silver layer
so they appear in the frontend application.

Author: AI Assistant
Date: January 2026
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CATALOG = "fins_team_3"
SCHEMA = "lease_management"
WAREHOUSE_ID = "288a7ec183eea397"


def run_query(client, warehouse_id, query):
    """Execute a query and return results"""
    try:
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="50s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                return True, statement.result.data_array
            return True, []
        else:
            error_msg = f"Query failed: {statement.status.state}"
            if statement.status.error:
                error_msg += f" - {statement.status.error.message}"
            return False, error_msg
            
    except Exception as e:
        return False, str(e)


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("Bronze to Silver Promotion Script")
    print("=" * 60)
    print()
    
    # Initialize Databricks client
    print("Connecting to Databricks...")
    try:
        client = WorkspaceClient()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure DATABRICKS_HOST and DATABRICKS_TOKEN are set in your .env file")
        return
    
    print()
    
    # Check current counts
    print("Checking current record counts...")
    count_query = f"""
    SELECT 
        'Bronze (Total)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE tenant_name IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'Bronze (VERIFIED)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE validation_status = 'VERIFIED'
        AND tenant_name IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'Silver (Before)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.silver_leases
    """
    
    success, result = run_query(client, WAREHOUSE_ID, count_query)
    if success and result:
        print()
        print("Current Record Counts:")
        print("-" * 60)
        for row in result:
            print(f"  {row[0]}: {row[1]}")
        print()
    else:
        print(f"❌ Failed to check record counts: {result}")
        return
    
    # Promote VERIFIED records from bronze to silver
    print("Promoting VERIFIED bronze records to silver layer...")
    print()
    
    merge_query = f"""
    MERGE INTO {CATALOG}.{SCHEMA}.silver_leases AS target
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
            'synthetic_data_script' as verified_by,
            CURRENT_TIMESTAMP() as verified_at,
            NULL as raw_document_path,
            uploaded_at,
            CURRENT_TIMESTAMP() as updated_at,
            
            extraction_id
            
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE validation_status = 'VERIFIED'
            AND tenant_name IS NOT NULL
    ) AS source
    ON target.lease_id = source.lease_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
    
    success, result = run_query(client, WAREHOUSE_ID, merge_query)
    
    if success:
        print("✅ Successfully promoted VERIFIED records to silver layer")
    else:
        print(f"❌ Failed to promote records: {result}")
        return
    
    print()
    
    # Check final counts
    print("Checking final record counts...")
    final_count_query = f"""
    SELECT 
        'Bronze (Total)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE tenant_name IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'Bronze (VERIFIED)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.bronze_leases
    WHERE validation_status = 'VERIFIED'
        AND tenant_name IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'Silver (After)' as layer,
        COUNT(*) as record_count
    FROM {CATALOG}.{SCHEMA}.silver_leases
    """
    
    success, result = run_query(client, WAREHOUSE_ID, final_count_query)
    if success and result:
        print()
        print("Final Record Counts:")
        print("-" * 60)
        for row in result:
            print(f"  {row[0]}: {row[1]}")
        print()
    
    print("=" * 60)
    print("Promotion Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open your frontend application")
    print("  2. The dashboard should now show the synthetic data")
    print("  3. Verify visualizations and maps are populated")
    print()


if __name__ == "__main__":
    main()

