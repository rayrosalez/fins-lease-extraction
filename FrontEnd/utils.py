"""
Utility functions for Databricks interactions
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv
import os
import time
import random
from io import BytesIO

# Load environment variables from .env file
load_dotenv()


def get_databricks_client():
    """Initialize Databricks workspace client"""
    try:
        # The WorkspaceClient will automatically use DATABRICKS_HOST and DATABRICKS_TOKEN
        # from environment variables after load_dotenv() is called
        client = WorkspaceClient()
        return client, None
    except Exception as e:
        return None, str(e)


def upload_to_volume(client, file_bytes, file_name, volume_path):
    """Upload file to Databricks Volume with random 4-digit suffix"""
    try:
        # Split filename and extension
        name_parts = file_name.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, extension = name_parts
            # Append random 4-digit number to filename
            random_suffix = random.randint(1000, 9999)
            new_file_name = f"{base_name}_{random_suffix}.{extension}"
        else:
            # No extension found, just append to the end
            random_suffix = random.randint(1000, 9999)
            new_file_name = f"{file_name}_{random_suffix}"
        
        # Construct the full path in the volume
        full_path = f"{volume_path}/uploads/{new_file_name}"
        
        # Convert bytes to BytesIO object (file-like object)
        file_obj = BytesIO(file_bytes)
        
        # Upload the file using the Files API
        client.files.upload(
            file_path=full_path,
            contents=file_obj,
            overwrite=True
        )
        
        return True, full_path, None
    except Exception as e:
        return False, None, str(e)


def query_staging_table(client, warehouse_id, source_file_path, catalog, schema):
    """Query the bronze_pdf_parsed table for a specific file"""
    try:
        query = f"""
        SELECT source_file_path, json_string 
        FROM {catalog}.{schema}.bronze_pdf_parsed 
        WHERE source_file_path = '{source_file_path}'
        ORDER BY _metadata_load_timestamp DESC
        LIMIT 1
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                if len(statement.result.data_array) > 0:
                    row = statement.result.data_array[0]
                    return True, row[1] if len(row) > 1 else None, None
            return False, None, "No results found"
        else:
            return False, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, str(e)


def query_most_recent_row(client, warehouse_id, catalog, schema):
    """Query the most recent row from bronze_pdf_parsed table"""
    try:
        query = f"""
        SELECT source_file_path, json_string 
        FROM {catalog}.{schema}.bronze_pdf_parsed 
        ORDER BY upload_timestamp DESC
        LIMIT 1
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                if len(statement.result.data_array) > 0:
                    row = statement.result.data_array[0]
                    source_path = row[0] if len(row) > 0 else None
                    json_string = row[1] if len(row) > 1 else None
                    return True, source_path, json_string, None
            return False, None, None, "No results found in table"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def poll_for_results(client, warehouse_id, source_file_path, catalog, schema, max_attempts=20, delay=5):
    """Poll the staging table until results appear or timeout"""
    for attempt in range(max_attempts):
        success, result, error = query_staging_table(
            client, warehouse_id, source_file_path, catalog, schema
        )
        
        if success and result:
            return True, result, None
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    return False, None, "Timeout: Job did not complete within expected time"


def query_silver_table(client, warehouse_id, catalog, schema):
    """Query all lease data from silver table"""
    try:
        query = f"""
        SELECT * 
        FROM {catalog}.{schema}.silver_lease_abstracts
        ORDER BY commencement_date DESC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                # Get column names
                columns = [col.name for col in statement.result.manifest.schema.columns] if statement.result.manifest else []
                return True, statement.result.data_array, columns, None
            return False, None, None, "No results found in silver table"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_lease_summary(client, warehouse_id, catalog, schema):
    """Get summary statistics from silver table"""
    try:
        query = f"""
        SELECT 
            COUNT(*) as total_leases,
            SUM(annual_base_rent) as total_annual_rent,
            AVG(annual_base_rent) as avg_annual_rent,
            SUM(rentable_square_feet) as total_sqft,
            AVG(rentable_square_feet) as avg_sqft,
            AVG(lease_term_months) as avg_lease_term_months,
            COUNT(DISTINCT property_address) as unique_properties,
            SUM(CASE WHEN expiration_date < CURRENT_DATE() THEN 1 ELSE 0 END) as expired_leases,
            SUM(CASE WHEN DATEDIFF(expiration_date, CURRENT_DATE()) BETWEEN 0 AND 180 THEN 1 ELSE 0 END) as expiring_soon
        FROM {catalog}.{schema}.silver_lease_abstracts
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array and len(statement.result.data_array) > 0:
                row = statement.result.data_array[0]
                
                # Helper function to safely convert to float or int
                def to_number(value, as_int=False):
                    if value is None:
                        return 0
                    try:
                        num = float(value)
                        return int(num) if as_int else num
                    except (ValueError, TypeError):
                        return 0
                
                summary = {
                    'total_leases': to_number(row[0], as_int=True),
                    'total_annual_rent': to_number(row[1]),
                    'avg_annual_rent': to_number(row[2]),
                    'total_sqft': to_number(row[3]),
                    'avg_sqft': to_number(row[4]),
                    'avg_lease_term_months': to_number(row[5]),
                    'unique_properties': to_number(row[6], as_int=True),
                    'expired_leases': to_number(row[7], as_int=True),
                    'expiring_soon': to_number(row[8], as_int=True)
                }
                return True, summary, None
            return False, None, "No data in silver table"
        else:
            return False, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, str(e)


def query_leases_by_tenant(client, warehouse_id, catalog, schema):
    """Get lease data grouped by tenant"""
    try:
        query = f"""
        SELECT 
            tenant_name,
            tenant_industry,
            COUNT(*) as lease_count,
            SUM(annual_base_rent) as total_rent,
            SUM(rentable_square_feet) as total_sqft,
            MIN(commencement_date) as earliest_lease,
            MAX(expiration_date) as latest_expiration
        FROM {catalog}.{schema}.silver_lease_abstracts
        GROUP BY tenant_name, tenant_industry
        ORDER BY total_rent DESC
        LIMIT 20
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['tenant_name', 'tenant_industry', 'lease_count', 'total_rent', 'total_sqft', 'earliest_lease', 'latest_expiration']
                return True, statement.result.data_array, columns, None
            return False, None, None, "No results found"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_expiring_leases(client, warehouse_id, catalog, schema, days=180):
    """Get leases expiring within specified days"""
    try:
        query = f"""
        SELECT 
            tenant_name,
            property_address,
            expiration_date,
            DATEDIFF(expiration_date, CURRENT_DATE()) as days_until_expiration,
            annual_base_rent,
            rentable_square_feet,
            tenant_credit_rating
        FROM {catalog}.{schema}.silver_lease_abstracts
        WHERE expiration_date >= CURRENT_DATE()
        AND DATEDIFF(expiration_date, CURRENT_DATE()) <= {days}
        ORDER BY expiration_date ASC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['tenant_name', 'property_address', 'expiration_date', 'days_until_expiration', 'annual_base_rent', 'rentable_square_feet', 'tenant_credit_rating']
                return True, statement.result.data_array, columns, None
            return False, None, None, "No expiring leases found"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_property_rollup(client, warehouse_id, catalog, schema):
    """Get lease data rolled up by property"""
    try:
        query = f"""
        SELECT 
            property_address,
            COUNT(*) as tenant_count,
            SUM(annual_base_rent) as property_revenue,
            SUM(rentable_square_feet) as total_leased_sqft,
            AVG(annual_base_rent / rentable_square_feet) as avg_rent_per_sqft,
            MIN(expiration_date) as next_expiration,
            landlord_name
        FROM {catalog}.{schema}.silver_lease_abstracts
        GROUP BY property_address, landlord_name
        ORDER BY property_revenue DESC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['property_address', 'tenant_count', 'property_revenue', 'total_leased_sqft', 'avg_rent_per_sqft', 'next_expiration', 'landlord_name']
                return True, statement.result.data_array, columns, None
            return False, None, None, "No results found"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_portfolio_health(client, warehouse_id, catalog, schema):
    """Query the gold_portfolio_health aggregated table"""
    try:
        query = f"""
        SELECT 
            market,
            lease_count,
            avg_rent_psf,
            walt_years,
            leases_with_exit_risk,
            leases_blocking_new_deals,
            avg_market_risk_index
        FROM {catalog}.{schema}.gold_portfolio_health
        ORDER BY lease_count DESC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['market', 'lease_count', 'avg_rent_psf', 'walt_years', 'leases_with_exit_risk', 'leases_blocking_new_deals', 'avg_market_risk_index']
                return True, statement.result.data_array, columns, None
            return False, None, None, "No results found"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_fact_lease_details(client, warehouse_id, catalog, schema):
    """Query detailed fact_lease data with enrichments"""
    try:
        query = f"""
        SELECT 
            l.file_path,
            l.property_name,
            p.market,
            p.asset_type,
            l.tenant_name,
            l.industry,
            t.credit_rating,
            l.commencement_date,
            l.expiration_date,
            l.base_rent_psf,
            l.has_termination_option,
            l.has_rofr,
            l.rent_escalation_type,
            l.ai_risk_score,
            DATEDIFF(l.expiration_date, CURRENT_DATE()) / 365.25 as years_remaining
        FROM {catalog}.{schema}.fact_lease l
        LEFT JOIN {catalog}.{schema}.dim_property p ON l.property_name = p.property_name
        LEFT JOIN {catalog}.{schema}.dim_tenant t ON l.tenant_name = t.tenant_name
        ORDER BY l.expiration_date ASC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['file_path', 'property_name', 'market', 'asset_type', 'tenant_name', 'industry', 
                          'credit_rating', 'commencement_date', 'expiration_date', 'base_rent_psf',
                          'has_termination_option', 'has_rofr', 'rent_escalation_type', 'ai_risk_score', 'years_remaining']
                return True, statement.result.data_array, columns, None
            return False, None, None, "No results found"
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def query_portfolio_kpis(client, warehouse_id, catalog, schema):
    """Get overall portfolio KPIs"""
    try:
        query = f"""
        SELECT 
            COUNT(*) as total_leases,
            COUNT(DISTINCT l.property_name) as total_properties,
            COUNT(DISTINCT l.tenant_name) as total_tenants,
            COUNT(DISTINCT p.market) as markets_count,
            AVG(l.base_rent_psf) as avg_rent_psf,
            AVG(GREATEST(DATEDIFF(l.expiration_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt,
            SUM(CASE WHEN l.has_termination_option = true THEN 1 ELSE 0 END) as total_exit_risk,
            SUM(CASE WHEN l.has_rofr = true THEN 1 ELSE 0 END) as total_rofr,
            AVG(l.ai_risk_score) as avg_risk_score,
            SUM(CASE WHEN DATEDIFF(l.expiration_date, CURRENT_DATE()) <= 365 THEN 1 ELSE 0 END) as expiring_12_months
        FROM {catalog}.{schema}.fact_lease l
        LEFT JOIN {catalog}.{schema}.dim_property p ON l.property_name = p.property_name
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array and len(statement.result.data_array) > 0:
                row = statement.result.data_array[0]
                
                def to_number(value, as_int=False):
                    if value is None:
                        return 0
                    try:
                        num = float(value)
                        return int(num) if as_int else num
                    except (ValueError, TypeError):
                        return 0
                
                kpis = {
                    'total_leases': to_number(row[0], as_int=True),
                    'total_properties': to_number(row[1], as_int=True),
                    'total_tenants': to_number(row[2], as_int=True),
                    'markets_count': to_number(row[3], as_int=True),
                    'avg_rent_psf': to_number(row[4]),
                    'portfolio_walt': to_number(row[5]),
                    'total_exit_risk': to_number(row[6], as_int=True),
                    'total_rofr': to_number(row[7], as_int=True),
                    'avg_risk_score': to_number(row[8]),
                    'expiring_12_months': to_number(row[9], as_int=True)
                }
                return True, kpis, None
            return False, None, "No data available"
        else:
            return False, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, str(e)

