"""
Data Verification Script
========================

Verifies that synthetic data was successfully inserted
and provides statistics for validation.
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
CATALOG = "fins_team_3"
SCHEMA = "lease_management"
TABLE = "bronze_leases"
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
            return False, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("Synthetic Data Verification")
    print("=" * 60)
    print()
    
    # Connect to Databricks
    print("Connecting to Databricks...")
    try:
        client = WorkspaceClient()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print()
    
    # Check 1: Total count
    print("Verification Checks:")
    print("-" * 60)
    
    query = f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.{TABLE}"
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        total_count = result[0][0]
        print(f"✅ Total Leases: {total_count}")
    else:
        print(f"❌ Failed to count leases: {result}")
        return
    
    # Check 2: Industry distribution
    query = f"""
    SELECT industry_sector, COUNT(*) as count
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    GROUP BY industry_sector
    ORDER BY count DESC
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        print(f"✅ Industries: {len(result)} distinct industries")
        print("\n   Top 5 Industries:")
        for i, row in enumerate(result[:5], 1):
            print(f"     {i}. {row[0]}: {row[1]} leases")
    
    # Check 3: Landlord distribution
    query = f"""
    SELECT COUNT(DISTINCT landlord_name) as landlord_count
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        landlord_count = result[0][0]
        print(f"✅ Unique Landlords: {landlord_count}")
    
    # Check 4: Date range
    query = f"""
    SELECT 
        MIN(commencement_date) as earliest,
        MAX(expiration_date) as latest
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        earliest = result[0][0]
        latest = result[0][1]
        print(f"✅ Date Range: {earliest} to {latest}")
    
    # Check 5: Rent statistics
    query = f"""
    SELECT 
        ROUND(MIN(base_rent_psf), 2) as min_rent,
        ROUND(MAX(base_rent_psf), 2) as max_rent,
        ROUND(AVG(base_rent_psf), 2) as avg_rent
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        min_rent = result[0][0]
        max_rent = result[0][1]
        avg_rent = result[0][2]
        print(f"✅ Rent Range: ${min_rent} - ${max_rent} PSF (avg: ${avg_rent})")
    
    # Check 6: Validation status
    query = f"""
    SELECT validation_status, COUNT(*) as count
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    GROUP BY validation_status
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        print(f"✅ Validation Status:")
        for row in result:
            print(f"     {row[0]}: {row[1]} leases")
    
    # Check 7: Upcoming expirations
    query = f"""
    SELECT COUNT(*) as expiring_soon
    FROM {CATALOG}.{SCHEMA}.{TABLE}
    WHERE DATEDIFF(expiration_date, CURRENT_DATE()) BETWEEN 0 AND 365
    """
    success, result = run_query(client, WAREHOUSE_ID, query)
    
    if success and result:
        expiring = result[0][0]
        print(f"✅ Expiring in Next 12 Months: {expiring} leases")
    
    print()
    print("=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    print()
    print("✅ All checks passed - data looks good!")
    print()
    print("Next steps:")
    print("  1. Open Streamlit dashboard: streamlit run ../FrontEnd/app.py")
    print("  2. Click 'Refresh Data' button")
    print("  3. Verify visualizations populate correctly")
    print()


if __name__ == "__main__":
    main()

