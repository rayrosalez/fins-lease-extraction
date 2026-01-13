"""
Script to create Landlord and Tenant tables in Databricks
"""
import os
from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

load_dotenv()

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
WAREHOUSE_ID = os.getenv('DATABRICKS_WAREHOUSE_ID')
CATALOG = os.getenv('DATABRICKS_CATALOG', 'fins_team_3')
SCHEMA = os.getenv('DATABRICKS_SCHEMA', 'lease_management')


def execute_sql(client, statement, description):
    """Execute a SQL statement using Databricks SDK"""
    print(f"\n{'='*60}")
    print(f"Executing: {description}")
    print('='*60)
    
    try:
        response = client.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=statement,
            wait_timeout="30s"
        )
        
        if response.status.state == StatementState.SUCCEEDED:
            print(f"✅ SUCCESS: {description}")
            return True
        else:
            print(f"❌ FAILED: {response.status.state}")
            if response.status.error:
                print(f"   Error: {response.status.error.message}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("Creating Landlord and Tenant tables in Databricks...")
    print(f"Host: {DATABRICKS_HOST}")
    print(f"Warehouse: {WAREHOUSE_ID}")
    print(f"Catalog: {CATALOG}")
    print(f"Schema: {SCHEMA}")
    
    # Initialize client
    client = WorkspaceClient(
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN
    )
    
    # Create Landlords table
    landlords_sql = f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.landlords (
        landlord_id STRING NOT NULL COMMENT 'Unique identifier for landlord (derived from name)',
        landlord_name STRING COMMENT 'Legal name of the landlord/property owner',
        landlord_address STRING COMMENT 'Primary business address',
        company_type STRING COMMENT 'REIT, Private, Public, etc.',
        stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
        market_cap DOUBLE COMMENT 'Market capitalization in USD',
        total_assets DOUBLE COMMENT 'Total assets under management in USD',
        credit_rating STRING COMMENT 'Credit rating (e.g., AAA, BBB+)',
        credit_rating_agency STRING COMMENT 'Rating agency (S&P, Moodys, Fitch)',
        annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
        net_operating_income DOUBLE COMMENT 'NOI in USD',
        debt_to_equity_ratio DOUBLE COMMENT 'D/E ratio',
        total_properties INT COMMENT 'Total number of properties owned',
        total_square_footage DOUBLE COMMENT 'Total portfolio square footage',
        primary_property_types STRING COMMENT 'Main property types (Office, Retail, Industrial)',
        geographic_focus STRING COMMENT 'Primary geographic markets',
        financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
        bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
        recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE based on recent news',
        enrichment_source STRING COMMENT 'AI_CLAUDE, MANUAL, API',
        enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
        last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
        source_urls STRING COMMENT 'JSON array of source URLs used for enrichment',
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        CONSTRAINT landlords_pk PRIMARY KEY (landlord_id)
    )
    USING DELTA
    COMMENT 'Landlord master table with financial profiles enriched via AI'
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """
    
    execute_sql(client, landlords_sql, "Create landlords table")
    
    # Create Tenants table
    tenants_sql = f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.tenants (
        tenant_id STRING NOT NULL COMMENT 'Unique identifier for tenant (derived from name)',
        tenant_name STRING COMMENT 'Legal name of the tenant',
        tenant_address STRING COMMENT 'Headquarters or primary business address',
        industry_sector STRING COMMENT 'Primary industry sector',
        company_type STRING COMMENT 'Public, Private, Subsidiary, Non-profit',
        parent_company STRING COMMENT 'Parent company if subsidiary',
        stock_ticker STRING COMMENT 'Stock ticker if publicly traded',
        founding_year INT COMMENT 'Year company was founded',
        employee_count INT COMMENT 'Approximate number of employees',
        headquarters_location STRING COMMENT 'HQ city and state',
        market_cap DOUBLE COMMENT 'Market capitalization in USD (if public)',
        annual_revenue DOUBLE COMMENT 'Annual revenue in USD',
        net_income DOUBLE COMMENT 'Net income in USD',
        revenue_growth_pct DOUBLE COMMENT 'Year-over-year revenue growth %',
        profit_margin_pct DOUBLE COMMENT 'Profit margin percentage',
        credit_rating STRING COMMENT 'Credit rating (e.g., AAA, BBB+)',
        credit_rating_agency STRING COMMENT 'Rating agency (S&P, Moodys, Fitch)',
        duns_number STRING COMMENT 'D&B DUNS number',
        payment_history_score DOUBLE COMMENT 'Payment history score (1-100)',
        financial_health_score DOUBLE COMMENT 'Computed financial health score (1-10)',
        bankruptcy_risk STRING COMMENT 'LOW, MEDIUM, HIGH',
        industry_risk STRING COMMENT 'LOW, MEDIUM, HIGH based on sector volatility',
        recent_news_sentiment STRING COMMENT 'POSITIVE, NEUTRAL, NEGATIVE based on recent news',
        litigation_flag BOOLEAN COMMENT 'True if significant ongoing litigation found',
        locations_count INT COMMENT 'Number of business locations',
        years_in_business INT COMMENT 'Years the company has been operating',
        enrichment_source STRING COMMENT 'AI_CLAUDE, MANUAL, API',
        enrichment_confidence DOUBLE COMMENT 'Confidence score of enrichment (0-1)',
        last_enriched_at TIMESTAMP COMMENT 'When data was last enriched',
        source_urls STRING COMMENT 'JSON array of source URLs used for enrichment',
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        CONSTRAINT tenants_pk PRIMARY KEY (tenant_id)
    )
    USING DELTA
    COMMENT 'Tenant master table with financial profiles enriched via AI'
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """
    
    execute_sql(client, tenants_sql, "Create tenants table")
    
    print("\n" + "="*60)
    print("Table creation complete!")
    print("="*60)

if __name__ == "__main__":
    main()
