"""
Complete Data Generation Pipeline
==================================

This script:
1. Generates synthetic lease data
2. Inserts it into bronze_leases table
3. Automatically promotes VERIFIED records to silver_leases
4. Verifies the data is ready for the frontend

Author: AI Assistant
Date: January 2026
"""

from faker import Faker
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv()

# Initialize Faker
fake = Faker()

# Configuration
CATALOG = "fins_team_3"
SCHEMA = "lease_management"
TABLE = "bronze_leases"
WAREHOUSE_ID = "288a7ec183eea397"

# Import data pools from generate_synthetic_leases
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
    "Professional Services", "Restaurant", "Fitness", "Education",
    "Legal Services", "Marketing", "Consulting"
]

LEASE_TYPES = [
    "Triple Net (NNN)", "Modified Gross", "Full Service",
    "Absolute Net", "Percentage Lease"
]

LANDLORD_COMPANIES = [
    "Blackstone Property Partners", "Brookfield Asset Management", "Prologis Properties",
    "Equity Residential", "Boston Properties", "Vornado Realty Trust",
    "Simon Property Group", "Kimco Realty", "Digital Realty",
    "Alexandria Real Estate", "Crown Castle Properties", "Public Storage Holdings",
    "Welltower Inc", "Realty Income Corp", "Duke Realty"
]

MARKETS = {
    "San Francisco": {"min_rent": 55, "max_rent": 95, "sqft_range": (2000, 25000), "state": "California", "state_abbr": "CA", "zip_range": (94102, 94188)},
    "New York": {"min_rent": 60, "max_rent": 100, "sqft_range": (1500, 30000), "state": "New York", "state_abbr": "NY", "zip_range": (10001, 10282)},
    "Boston": {"min_rent": 45, "max_rent": 75, "sqft_range": (2000, 20000), "state": "Massachusetts", "state_abbr": "MA", "zip_range": (2108, 2298)},
    "Austin": {"min_rent": 35, "max_rent": 55, "sqft_range": (3000, 35000), "state": "Texas", "state_abbr": "TX", "zip_range": (78701, 78799)},
    "Seattle": {"min_rent": 40, "max_rent": 70, "sqft_range": (2500, 28000), "state": "Washington", "state_abbr": "WA", "zip_range": (98101, 98199)},
    "Los Angeles": {"min_rent": 38, "max_rent": 65, "sqft_range": (2000, 30000), "state": "California", "state_abbr": "CA", "zip_range": (90001, 90089)},
    "Chicago": {"min_rent": 32, "max_rent": 52, "sqft_range": (2500, 25000), "state": "Illinois", "state_abbr": "IL", "zip_range": (60601, 60661)},
    "Miami": {"min_rent": 35, "max_rent": 60, "sqft_range": (2000, 22000), "state": "Florida", "state_abbr": "FL", "zip_range": (33101, 33199)},
    "Denver": {"min_rent": 30, "max_rent": 50, "sqft_range": (3000, 26000), "state": "Colorado", "state_abbr": "CO", "zip_range": (80201, 80299)},
    "Dallas": {"min_rent": 28, "max_rent": 45, "sqft_range": (3500, 35000), "state": "Texas", "state_abbr": "TX", "zip_range": (75201, 75398)},
    "Atlanta": {"min_rent": 25, "max_rent": 42, "sqft_range": (3000, 30000), "state": "Georgia", "state_abbr": "GA", "zip_range": (30301, 30398)},
    "Phoenix": {"min_rent": 24, "max_rent": 40, "sqft_range": (3500, 32000), "state": "Arizona", "state_abbr": "AZ", "zip_range": (85001, 85099)}
}


def generate_company_name(industry):
    """Generate realistic company name based on industry"""
    tech_words = ["Tech", "Software", "Digital", "Cloud", "Data", "Cyber", "AI", "Quantum"]
    healthcare_words = ["Health", "Medical", "Care", "Wellness", "Life", "Bio", "Pharma"]
    finance_words = ["Capital", "Financial", "Investment", "Ventures", "Advisors", "Wealth"]
    retail_words = ["Retail", "Market", "Store", "Shop", "Goods", "Boutique"]
    suffixes = ["Inc", "LLC", "Corp", "Group", "Partners", "Solutions", "Services", "Enterprises"]
    
    if industry == "Technology":
        prefix = random.choice(tech_words)
    elif industry == "Healthcare":
        prefix = random.choice(healthcare_words)
    elif industry == "Finance":
        prefix = random.choice(finance_words)
    elif industry == "Retail":
        prefix = random.choice(retail_words)
    else:
        prefix = fake.company().split()[0]
    
    if random.random() < 0.3:
        return fake.company()
    else:
        middle = fake.last_name() if random.random() < 0.5 else ""
        suffix = random.choice(suffixes)
        return f"{prefix} {middle} {suffix}".strip().replace("  ", " ")


def generate_lease_dates():
    """Generate realistic lease start and end dates"""
    years_back = random.randint(1, 8)
    start_date = datetime.now() - timedelta(days=years_back * 365 + random.randint(0, 364))
    term_years = random.choice([3, 5, 7, 10])
    term_months = term_years * 12
    end_date = start_date + timedelta(days=term_years * 365)
    return start_date.date(), end_date.date(), term_months


def generate_address(city, state, state_abbr, zip_range):
    """Generate a realistic street address"""
    street_number = random.randint(100, 9999)
    street_names = [
        "Main Street", "Market Street", "Broadway", "Park Avenue", "Madison Avenue",
        "Oak Street", "Maple Avenue", "Washington Boulevard", "Lincoln Way", "Commerce Drive",
        "Business Parkway", "Tech Boulevard", "Innovation Drive", "Corporate Plaza"
    ]
    street = random.choice(street_names)
    zip_code = str(random.randint(zip_range[0], zip_range[1]))
    
    return {
        "street_address": f"{street_number} {street}",
        "city": city,
        "state": state,
        "state_abbr": state_abbr,
        "zip_code": zip_code,
        "full_address": f"{street_number} {street}, {city}, {state_abbr} {zip_code}"
    }


def generate_synthetic_lease(lease_id):
    """Generate a single synthetic lease record"""
    market = random.choice(list(MARKETS.keys()))
    market_data = MARKETS[market]
    commencement_date, expiration_date, term_months = generate_lease_dates()
    uploaded_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    industry = random.choice(INDUSTRIES)
    tenant_name = generate_company_name(industry)
    landlord_name = random.choice(LANDLORD_COMPANIES)
    
    property_location = generate_address(market, market_data["state"], market_data["state_abbr"], market_data["zip_range"])
    landlord_city = random.choice(list(MARKETS.keys()))
    landlord_market = MARKETS[landlord_city]
    landlord_location = generate_address(landlord_city, landlord_market["state"], landlord_market["state_abbr"], landlord_market["zip_range"])
    
    if random.random() < 0.7:
        tenant_location = property_location
    else:
        tenant_city = random.choice(list(MARKETS.keys()))
        tenant_market = MARKETS[tenant_city]
        tenant_location = generate_address(tenant_city, tenant_market["state"], tenant_market["state_abbr"], tenant_market["zip_range"])
    
    sqft_min, sqft_max = market_data["sqft_range"]
    square_feet = random.randint(sqft_min, sqft_max)
    square_feet = round(square_feet / 100) * 100
    base_rent_psf = random.uniform(market_data["min_rent"], market_data["max_rent"])
    base_rent_psf = round(base_rent_psf, 2)
    annual_base_rent = base_rent_psf * square_feet
    annual_escalation_pct = random.choice([0, 2, 2.5, 3, 3.5, 4])
    suite_number = f"{random.choice(['Suite', 'Unit', 'Space'])} {random.randint(100, 999)}"
    lease_type = random.choice(LEASE_TYPES)
    renewal_notice_days = random.choice([90, 120, 180])
    guarantor = fake.name() if random.random() < 0.3 else None
    validation_status = random.choice(["VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED", "PENDING"])
    extracted_at = uploaded_at + timedelta(minutes=random.randint(1, 10))
    raw_json = f'{{"tenant": "{tenant_name}", "landlord": "{landlord_name}", "industry": "{industry}", "sqft": {square_feet}, "location": "{property_location["city"]}, {property_location["state_abbr"]}"}}'
    
    return {
        "uploaded_at": uploaded_at,
        "extracted_at": extracted_at,
        "landlord_name": landlord_name,
        "landlord_address": landlord_location["full_address"],
        "tenant_name": tenant_name,
        "tenant_address": tenant_location["full_address"],
        "industry_sector": industry,
        "suite_number": suite_number,
        "lease_type": lease_type,
        "commencement_date": commencement_date,
        "expiration_date": expiration_date,
        "term_months": term_months,
        "rentable_square_feet": float(square_feet),
        "annual_base_rent": float(annual_base_rent),
        "base_rent_psf": float(base_rent_psf),
        "annual_escalation_pct": float(annual_escalation_pct),
        "renewal_notice_days": renewal_notice_days,
        "guarantor": guarantor,
        "property_address": property_location["full_address"],
        "property_street_address": property_location["street_address"],
        "property_city": property_location["city"],
        "property_state": property_location["state_abbr"],
        "property_zip_code": property_location["zip_code"],
        "property_country": "United States",
        "raw_json_payload": raw_json,
        "is_fully_extracted": True,
        "validation_status": validation_status
    }


def generate_values_clause(lease):
    """Generate just the VALUES clause for a lease"""
    def escape_sql(value):
        if value is None:
            return "NULL"
        return str(value).replace("'", "''")
    
    guarantor_value = f"'{escape_sql(lease['guarantor'])}'" if lease['guarantor'] else "NULL"
    uploaded_at_value = f"'{lease['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')}'"
    extracted_at_value = f"'{lease['extracted_at'].strftime('%Y-%m-%d %H:%M:%S')}'"
    
    values = f"""(
        {uploaded_at_value},
        {extracted_at_value},
        '{escape_sql(lease['landlord_name'])}',
        '{escape_sql(lease['landlord_address'])}',
        '{escape_sql(lease['tenant_name'])}',
        '{escape_sql(lease['tenant_address'])}',
        '{escape_sql(lease['industry_sector'])}',
        '{escape_sql(lease['suite_number'])}',
        '{escape_sql(lease['lease_type'])}',
        '{lease['commencement_date']}',
        '{lease['expiration_date']}',
        {lease['term_months']},
        {lease['rentable_square_feet']},
        {lease['annual_base_rent']},
        {lease['base_rent_psf']},
        {lease['annual_escalation_pct']},
        {lease['renewal_notice_days']},
        {guarantor_value},
        '{escape_sql(lease['property_address'])}',
        '{escape_sql(lease['property_street_address'])}',
        '{escape_sql(lease['property_city'])}',
        '{escape_sql(lease['property_state'])}',
        '{escape_sql(lease['property_zip_code'])}',
        '{escape_sql(lease['property_country'])}',
        '{escape_sql(lease['raw_json_payload'])}',
        {'TRUE' if lease['is_fully_extracted'] else 'FALSE'},
        '{escape_sql(lease['validation_status'])}'
    )"""
    
    return values


def generate_batch_insert_statement(leases, catalog, schema, table):
    """Generate a single INSERT statement with multiple VALUES for a batch"""
    values_clauses = [generate_values_clause(lease) for lease in leases]
    
    sql = f"""INSERT INTO {catalog}.{schema}.{table} (
        uploaded_at, extracted_at, landlord_name, landlord_address, tenant_name, tenant_address,
        industry_sector, suite_number, lease_type, commencement_date, expiration_date,
        term_months, rentable_square_feet, annual_base_rent, base_rent_psf,
        annual_escalation_pct, renewal_notice_days, guarantor,
        property_address, property_street_address, property_city, property_state,
        property_zip_code, property_country,
        raw_json_payload, is_fully_extracted, validation_status
    ) VALUES
{','.join(values_clauses)}"""
    
    return sql


def insert_leases_batch(client, warehouse_id, leases, catalog, schema, table):
    """Insert a batch of leases using a single INSERT with multiple VALUES"""
    combined_sql = generate_batch_insert_statement(leases, catalog, schema, table)
    
    try:
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=combined_sql,
            wait_timeout="50s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            return True, None
        else:
            error_msg = f"Statement failed: {statement.status.state}"
            if statement.status.error:
                error_msg += f" - {statement.status.error.message}"
            return False, error_msg
            
    except Exception as e:
        return False, str(e)


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


def promote_to_silver(client, warehouse_id):
    """Promote VERIFIED bronze records to silver layer"""
    print("\n" + "=" * 60)
    print("Step 3: Promoting to Silver Layer")
    print("=" * 60)
    print()
    
    merge_query = f"""
    MERGE INTO {CATALOG}.{SCHEMA}.silver_leases AS target
    USING (
        SELECT 
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
            tenant_name,
            industry_sector,
            suite_number as suite_id,
            rentable_square_feet as square_footage,
            lease_type,
            commencement_date as lease_start_date,
            expiration_date as lease_end_date,
            base_rent_psf,
            annual_escalation_pct,
            property_address,
            property_street_address,
            property_city,
            property_state,
            property_zip_code,
            property_country,
            CASE 
                WHEN rentable_square_feet IS NOT NULL AND base_rent_psf IS NOT NULL 
                THEN rentable_square_feet * base_rent_psf
                WHEN annual_base_rent IS NOT NULL 
                THEN annual_base_rent
                ELSE 0
            END as estimated_annual_rent,
            DATE_ADD(commencement_date, 365) as next_escalation_date,
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
    
    print("Promoting VERIFIED records from bronze to silver...")
    success, result = run_query(client, warehouse_id, merge_query)
    
    if success:
        print("✅ Successfully promoted records to silver layer")
        return True
    else:
        print(f"❌ Failed to promote records: {result}")
        return False


def main():
    """Main execution function"""
    print("=" * 60)
    print("Complete Data Generation Pipeline")
    print("=" * 60)
    print()
    
    # Get number of leases to generate
    if len(sys.argv) > 1:
        try:
            num_leases = int(sys.argv[1])
        except:
            num_leases = 100
    else:
        num_leases = int(input("How many synthetic leases to generate? (recommended 50-200): ") or "100")
    
    batch_size = 10
    
    print(f"\nGenerating {num_leases} synthetic leases...")
    print()
    
    # Step 1: Connect to Databricks
    print("=" * 60)
    print("Step 1: Connecting to Databricks")
    print("=" * 60)
    print()
    
    try:
        client = WorkspaceClient()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure DATABRICKS_HOST and DATABRICKS_TOKEN are set in your .env file")
        return
    
    # Step 2: Generate and insert leases
    print("\n" + "=" * 60)
    print("Step 2: Generating and Inserting Leases")
    print("=" * 60)
    print()
    
    print(f"Generating {num_leases} lease records...")
    all_leases = []
    for i in range(num_leases):
        lease = generate_synthetic_lease(i + 1)
        all_leases.append(lease)
        
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{num_leases}...")
    
    print(f"✅ Generated {num_leases} lease records")
    print()
    
    print(f"Inserting leases into {CATALOG}.{SCHEMA}.{TABLE} (batch size: {batch_size})...")
    print()
    
    successful = 0
    failed = 0
    
    for i in range(0, len(all_leases), batch_size):
        batch = all_leases[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(all_leases) + batch_size - 1) // batch_size
        
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} leases)...", end=" ")
        
        success, error = insert_leases_batch(client, WAREHOUSE_ID, batch, CATALOG, SCHEMA, TABLE)
        
        if success:
            successful += len(batch)
            print("✅")
        else:
            failed += len(batch)
            print(f"❌ Error: {error}")
        
        time.sleep(0.5)
    
    print()
    print(f"✅ Successfully inserted: {successful} leases to bronze layer")
    if failed > 0:
        print(f"❌ Failed: {failed} leases")
    
    # Step 3: Promote to silver
    if successful > 0:
        if promote_to_silver(client, WAREHOUSE_ID):
            # Step 4: Verify final counts
            print("\n" + "=" * 60)
            print("Step 4: Verification")
            print("=" * 60)
            print()
            
            verify_query = f"""
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
                'Silver (Total)' as layer,
                COUNT(*) as record_count
            FROM {CATALOG}.{SCHEMA}.silver_leases
            """
            
            success, result = run_query(client, WAREHOUSE_ID, verify_query)
            if success and result:
                print("Final Record Counts:")
                print("-" * 60)
                for row in result:
                    print(f"  {row[0]}: {row[1]}")
                print()
    
    print("=" * 60)
    print("✅ Pipeline Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open your frontend application at http://localhost:3000")
    print("  2. The dashboard should now show the synthetic data")
    print("  3. Check the map, portfolio stats, and charts")
    print()


if __name__ == "__main__":
    main()

