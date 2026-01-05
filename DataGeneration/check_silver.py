"""
Quick Check Script - Verify Data in Silver Table
=================================================

Quick script to check if data successfully made it to the silver_leases table
(the table that the frontend reads from).

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
            wait_timeout="30s"
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
    print("Quick Check - Silver Table Status")
    print("=" * 60)
    print()
    
    # Connect to Databricks
    print("Connecting to Databricks...")
    try:
        client = WorkspaceClient()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure DATABRICKS_HOST and DATABRICKS_TOKEN are set")
        return
    
    print()
    print("Checking silver_leases table...")
    print("-" * 60)
    
    # Quick count query
    query = f"""
    SELECT COUNT(*) as total_leases
    FROM {CATALOG}.{SCHEMA}.silver_leases
    """
    
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        total = result[0][0]
        print(f"\n✅ Total leases in silver_leases: {total}")
        
        if total == 0:
            print("\n⚠️  No data found in silver_leases!")
            print("\nPossible reasons:")
            print("  1. Haven't run data generation yet")
            print("  2. Ran generate_synthetic_leases.py but not promote_to_silver.py")
            print("  3. All bronze records are PENDING (not VERIFIED)")
            print("\n💡 Solution: Run generate_and_promote.py to generate and promote data")
        else:
            print("\n✅ Data is ready for frontend!")
            print("\nYou can now:")
            print("  1. Open http://localhost:3000")
            print("  2. View the dashboard with real data")
            print("  3. Test all features")
            
            # Get some sample info
            sample_query = f"""
            SELECT 
                COUNT(DISTINCT industry_sector) as industries,
                COUNT(DISTINCT property_city) as cities,
                ROUND(AVG(base_rent_psf), 2) as avg_rent
            FROM {CATALOG}.{SCHEMA}.silver_leases
            """
            
            success2, result2 = run_query(client, WAREHOUSE_ID, sample_query)
            if success2 and result2:
                print(f"\n📊 Data Summary:")
                print(f"  - Industries: {result2[0][0]}")
                print(f"  - Cities: {result2[0][1]}")
                print(f"  - Avg Rent PSF: ${result2[0][2]}")
    else:
        print(f"\n❌ Failed to check table: {result}")
        print("\nMake sure:")
        print("  1. SQL Warehouse is running")
        print("  2. silver_leases table exists")
        print("  3. You have SELECT permissions")
    
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

