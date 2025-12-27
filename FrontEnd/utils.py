"""
Utility functions for Databricks interactions
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv
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


def query_portfolio_health(client, warehouse_id, catalog, schema):
    """Query aggregated portfolio health by industry (since we don't have market in bronze)"""
    try:
        query = f"""
        SELECT 
            COALESCE(industry_sector, 'Unknown') as market,
            COUNT(*) as lease_count,
            ROUND(AVG(base_rent_psf), 2) as avg_rent_psf,
            ROUND(AVG(GREATEST(DATEDIFF(expiration_date, CURRENT_DATE()), 0) / 365.25), 2) as walt_years,
            0 as leases_with_exit_risk,
            0 as leases_blocking_new_deals,
            5.0 as avg_market_risk_index
        FROM {catalog}.{schema}.bronze_leases
        WHERE expiration_date IS NOT NULL
        GROUP BY industry_sector
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
    """Query detailed lease data from bronze_leases table"""
    try:
        query = f"""
        SELECT 
            'N/A' as file_path,
            COALESCE(landlord_name, 'Unknown Property') as property_name,
            COALESCE(industry_sector, 'Unknown') as market,
            COALESCE(lease_type, 'Unknown') as asset_type,
            tenant_name,
            industry_sector as industry,
            'N/A' as credit_rating,
            commencement_date,
            expiration_date,
            base_rent_psf,
            false as has_termination_option,
            false as has_rofr,
            CASE 
                WHEN annual_escalation_pct > 0 THEN 'Fixed'
                ELSE 'None'
            END as rent_escalation_type,
            5.0 as ai_risk_score,
            DATEDIFF(expiration_date, CURRENT_DATE()) / 365.25 as years_remaining
        FROM {catalog}.{schema}.bronze_leases
        WHERE tenant_name IS NOT NULL
        ORDER BY expiration_date ASC
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
    """Get overall portfolio KPIs from bronze_leases"""
    try:
        query = f"""
        SELECT 
            COUNT(*) as total_leases,
            COUNT(DISTINCT COALESCE(landlord_name, 'Unknown')) as total_properties,
            COUNT(DISTINCT tenant_name) as total_tenants,
            COUNT(DISTINCT COALESCE(industry_sector, 'Unknown')) as markets_count,
            AVG(base_rent_psf) as avg_rent_psf,
            AVG(GREATEST(DATEDIFF(expiration_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt,
            0 as total_exit_risk,
            0 as total_rofr,
            5.0 as avg_risk_score,
            SUM(CASE WHEN DATEDIFF(expiration_date, CURRENT_DATE()) <= 365 AND DATEDIFF(expiration_date, CURRENT_DATE()) >= 0 THEN 1 ELSE 0 END) as expiring_12_months
        FROM {catalog}.{schema}.bronze_leases
        WHERE tenant_name IS NOT NULL
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


def query_records_for_review(client, warehouse_id, catalog, schema):
    """Get records that need review (NEW or PENDING status)"""
    try:
        query = f"""
        SELECT 
            extraction_id,
            landlord_name,
            tenant_name,
            industry_sector,
            suite_number,
            lease_type,
            commencement_date,
            expiration_date,
            term_months,
            rentable_square_feet,
            annual_base_rent,
            base_rent_psf,
            annual_escalation_pct,
            renewal_notice_days,
            guarantor,
            validation_status
        FROM {catalog}.{schema}.bronze_leases
        WHERE validation_status IN ('NEW', 'PENDING')
        ORDER BY 
            CASE validation_status 
                WHEN 'NEW' THEN 1 
                WHEN 'PENDING' THEN 2 
            END,
            extraction_id ASC
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                columns = ['extraction_id', 'landlord_name', 'tenant_name', 'industry_sector', 
                          'suite_number', 'lease_type', 'commencement_date', 'expiration_date',
                          'term_months', 'rentable_square_feet', 'annual_base_rent', 'base_rent_psf',
                          'annual_escalation_pct', 'renewal_notice_days', 'guarantor', 'validation_status']
                return True, statement.result.data_array, columns, None
            return True, [], [], None  # No records to review
        else:
            return False, None, None, f"Query failed: {statement.status.state}"
            
    except Exception as e:
        return False, None, None, str(e)


def promote_to_silver_layer(client, warehouse_id, catalog, schema, bronze_record):
    """
    Promote a verified record from bronze to silver layer with enrichments
    
    Args:
        bronze_record: Dictionary containing the bronze record data
    """
    try:
        # First, query the silver table schema to see what columns exist
        describe_query = f"DESCRIBE TABLE {catalog}.{schema}.silver_leases"
        
        try:
            describe_stmt = client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=describe_query,
                wait_timeout="30s"
            )
            
            if describe_stmt.status.state == StatementState.SUCCEEDED and describe_stmt.result:
                available_columns = [row[0] for row in describe_stmt.result.data_array if row]
                print(f"DEBUG: Available silver columns: {available_columns}")
            else:
                # Fallback to basic columns if describe fails
                available_columns = ['lease_id', 'property_id', 'tenant_name', 'industry_sector', 'suite_id']
        except:
            # Fallback to basic columns
            available_columns = ['lease_id', 'property_id', 'tenant_name', 'industry_sector', 'suite_id']
        
        # Generate lease_id (unique identifier)
        tenant_clean = str(bronze_record['tenant_name']).replace(' ', '_').replace(',', '')[:20]
        landlord_clean = str(bronze_record['landlord_name']).replace(' ', '_').replace(',', '')[:20]
        suite_clean = str(bronze_record['suite_number']).replace(' ', '_')[:10]
        lease_id = f"{landlord_clean}_{tenant_clean}_{suite_clean}"
        
        # Generate property_id
        property_id = f"PROP_{landlord_clean}_{suite_clean}"
        
        # Calculate estimated annual rent
        sqft = float(bronze_record['rentable_square_feet']) if bronze_record['rentable_square_feet'] else 0
        rent_psf = float(bronze_record['base_rent_psf']) if bronze_record['base_rent_psf'] else 0
        estimated_annual_rent = sqft * rent_psf
        
        # Calculate next escalation date (1 year from start)
        from datetime import datetime, timedelta
        try:
            start_date = datetime.strptime(str(bronze_record['commencement_date']), '%Y-%m-%d')
            next_escalation = start_date + timedelta(days=365)
            next_escalation_str = next_escalation.strftime('%Y-%m-%d')
        except:
            next_escalation_str = bronze_record['commencement_date']
        
        # Escape SQL strings
        def escape_sql(value):
            if value is None:
                return "NULL"
            return str(value).replace("'", "''")
        
        # Build insert dynamically based on available columns
        columns = ['lease_id', 'property_id', 'tenant_name', 'industry_sector', 'suite_id']
        values = [
            f"'{escape_sql(lease_id)}'",
            f"'{escape_sql(property_id)}'",
            f"'{escape_sql(bronze_record['tenant_name'])}'",
            f"'{escape_sql(bronze_record['industry_sector'])}'",
            f"'{escape_sql(bronze_record['suite_number'])}'"
        ]
        
        # Add optional columns if they exist
        optional_mappings = {
            'square_footage': sqft,
            'lease_type': f"'{escape_sql(bronze_record['lease_type'])}'",
            'lease_start_date': f"'{bronze_record['commencement_date']}'",
            'lease_end_date': f"'{bronze_record['expiration_date']}'",
            'base_rent_psf': rent_psf,
            'annual_escalation_pct': float(bronze_record['annual_escalation_pct']) if bronze_record['annual_escalation_pct'] else 0,
            'estimated_annual_rent': estimated_annual_rent,
            'next_escalation_date': f"'{next_escalation_str}'",
            'enhancement_source': "'AI_HUMAN_VERIFIED'",
            'validation_status': "'VERIFIED'",
            'verified_by': "'system_user'",
            'verified_at': 'CURRENT_TIMESTAMP()',
            'raw_document_path': f"'bronze_extraction_{bronze_record['extraction_id']}'",
            'updated_at': 'CURRENT_TIMESTAMP()'
        }
        
        for col, val in optional_mappings.items():
            if col in available_columns:
                columns.append(col)
                values.append(str(val))
        
        # Build the insert query
        insert_query = f"""
        INSERT INTO {catalog}.{schema}.silver_leases (
            {', '.join(columns)}
        ) VALUES (
            {', '.join(values)}
        )
        """
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=insert_query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            return True, None
        else:
            error_msg = f"Silver insert failed: {statement.status.state}"
            if statement.status.error:
                error_msg += f" - {statement.status.error.message}"
            return False, error_msg
            
    except Exception as e:
        return False, str(e)

