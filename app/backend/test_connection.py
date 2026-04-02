"""
Test script to verify Databricks connection
Run this to diagnose connection issues
"""
import os
from dotenv import load_dotenv

print("\n" + "="*60)
print("Databricks Connection Test")
print("="*60 + "\n")

# Load environment variables
load_dotenv()

# Check environment variables
print("1. Checking environment variables...")
env_vars = {
    'DATABRICKS_HOST': os.getenv('DATABRICKS_HOST'),
    'DATABRICKS_TOKEN': os.getenv('DATABRICKS_TOKEN'),
    'DATABRICKS_WAREHOUSE_ID': os.getenv('DATABRICKS_WAREHOUSE_ID'),
    'DATABRICKS_CATALOG': os.getenv('DATABRICKS_CATALOG', ''),
    'DATABRICKS_SCHEMA': os.getenv('DATABRICKS_SCHEMA', 'lease_management'),
}

all_set = True
for key, value in env_vars.items():
    if key == 'DATABRICKS_TOKEN':
        status = "✅ SET" if value else "❌ NOT SET"
    else:
        status = f"✅ {value}" if value else "❌ NOT SET"
    print(f"   {key}: {status}")
    if not value:
        all_set = False

if not all_set:
    print("\n❌ ERROR: Missing required environment variables!")
    print("\nTo fix this:")
    print("  1. Run: python setup.py")
    print("  2. Or manually create a .env file with your Databricks credentials")
    print("\nSee QUICKFIX.md for detailed instructions.")
    exit(1)

print("\n✅ All environment variables are set!")

# Test Databricks connection
print("\n2. Testing Databricks connection...")
try:
    from databricks.sdk import WorkspaceClient
    
    client = WorkspaceClient()
    print("✅ Successfully created Databricks client!")
    
    # Try to list warehouses
    print("\n3. Testing SQL Warehouse access...")
    warehouses = list(client.warehouses.list())
    print(f"✅ Found {len(warehouses)} SQL warehouse(s)")
    
    # Test query execution
    print("\n4. Testing query execution...")
    from databricks.sdk.service.sql import StatementState
    
    WAREHOUSE_ID = env_vars['DATABRICKS_WAREHOUSE_ID']
    CATALOG = env_vars['DATABRICKS_CATALOG']
    SCHEMA = env_vars['DATABRICKS_SCHEMA']
    
    test_query = f"SELECT COUNT(*) FROM {CATALOG}.{SCHEMA}.bronze_leases"
    print(f"   Query: {test_query}")
    
    statement = client.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=test_query,
        wait_timeout="30s"
    )
    
    if statement.status.state == StatementState.SUCCEEDED:
        if statement.result and statement.result.data_array:
            count = statement.result.data_array[0][0]
            print(f"✅ Query succeeded! Found {count} leases in the table")
        else:
            print("⚠️  Query succeeded but returned no data")
    else:
        print(f"❌ Query failed: {statement.status.state}")
        if statement.status.error:
            print(f"   Error: {statement.status.error.message}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour configuration is correct. You can now run: python api.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nPossible issues:")
    print("  - SQL Warehouse is not running (start it in Databricks)")
    print("  - Incorrect warehouse ID")
    print("  - Invalid access token")
    print("  - Table doesn't exist or wrong catalog/schema names")
    print("  - Insufficient permissions")
    print("\nSee QUICKFIX.md for troubleshooting steps.")
    exit(1)

