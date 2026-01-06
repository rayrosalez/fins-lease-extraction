"""
Quick Setup Script for FrontEndV2 Backend
Run this to interactively create your .env file
"""
import os

def main():
    print("=" * 60)
    print("FrontEndV2 Backend Configuration")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("Please provide your Databricks configuration:")
    print()
    
    # Get configuration
    db_host = input("Databricks Host (e.g., https://your-workspace.cloud.databricks.com): ").strip()
    db_token = input("Databricks Personal Access Token: ").strip()
    warehouse_id = input("SQL Warehouse ID: ").strip()
    catalog = input("Catalog name [fins_team_3]: ").strip() or "fins_team_3"
    schema = input("Schema name [lease_management]: ").strip() or "lease_management"
    
    # Create .env file
    env_content = f"""# Databricks Configuration
DATABRICKS_HOST={db_host}
DATABRICKS_TOKEN={db_token}
DATABRICKS_WAREHOUSE_ID={warehouse_id}
DATABRICKS_CATALOG={catalog}
DATABRICKS_SCHEMA={schema}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print()
    print("✅ .env file created successfully!")
    print()
    print("Configuration:")
    print(f"  Host: {db_host}")
    print(f"  Warehouse ID: {warehouse_id}")
    print(f"  Catalog: {catalog}")
    print(f"  Schema: {schema}")
    print()
    print("You can now start the API server with: python api.py")

if __name__ == "__main__":
    main()

