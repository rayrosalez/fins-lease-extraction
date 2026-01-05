from flask import Flask, jsonify, request
from flask_cors import CORS
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
CATALOG = os.getenv('DATABRICKS_CATALOG', 'fins_team_3')
SCHEMA = os.getenv('DATABRICKS_SCHEMA', 'lease_management')
WAREHOUSE_ID = os.getenv('DATABRICKS_WAREHOUSE_ID')
VOLUME_NAME = os.getenv('DATABRICKS_VOLUME', 'raw_lease_docs')

# Print configuration on startup
print(f"\n{'='*60}")
print(f"API Configuration:")
print(f"CATALOG: {CATALOG}")
print(f"SCHEMA: {SCHEMA}")
print(f"WAREHOUSE_ID: {WAREHOUSE_ID if WAREHOUSE_ID else 'NOT SET'}")
print(f"VOLUME: {VOLUME_NAME}")
print(f"DATABRICKS_HOST: {os.getenv('DATABRICKS_HOST', 'NOT SET')}")
print(f"DATABRICKS_TOKEN: {'SET' if os.getenv('DATABRICKS_TOKEN') else 'NOT SET'}")
print(f"{'='*60}\n")

def get_client():
    """Get Databricks client"""
    try:
        client = WorkspaceClient()
        return client, None
    except Exception as e:
        return None, str(e)

def execute_query(query):
    """Execute SQL query and return results"""
    try:
        if not WAREHOUSE_ID:
            return None, "DATABRICKS_WAREHOUSE_ID environment variable is not set"
        
        client, error = get_client()
        if error:
            print(f"ERROR getting Databricks client: {error}")
            return None, error
        
        print(f"Executing query: {query[:100]}...")
        
        statement = client.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=query,
            wait_timeout="30s"
        )
        
        if statement.status.state == StatementState.SUCCEEDED:
            if statement.result and statement.result.data_array:
                print(f"Query succeeded, returned {len(statement.result.data_array)} rows")
                return statement.result.data_array, None
            print("Query succeeded but returned no data")
            return [], None
        else:
            error_msg = f"Query failed: {statement.status.state}"
            if statement.status.error:
                error_msg += f" - {statement.status.error.message}"
            print(f"ERROR: {error_msg}")
            return None, error_msg
    except Exception as e:
        error_msg = f"Exception executing query: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None, str(e)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/portfolio/kpis', methods=['GET'])
def get_portfolio_kpis():
    """Get overall portfolio KPIs from silver layer (verified leases only)"""
    try:
        query = f"""
        SELECT 
            COUNT(*) as total_leases,
            COUNT(DISTINCT COALESCE(property_id, 'Unknown')) as total_properties,
            COUNT(DISTINCT tenant_name) as total_tenants,
            COUNT(DISTINCT COALESCE(industry_sector, 'Unknown')) as markets_count,
            AVG(base_rent_psf) as avg_rent_psf,
            AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt,
            0 as total_exit_risk,
            0 as total_rofr,
            5.0 as avg_risk_score,
            SUM(CASE WHEN DATEDIFF(lease_end_date, CURRENT_DATE()) <= 365 AND DATEDIFF(lease_end_date, CURRENT_DATE()) >= 0 THEN 1 ELSE 0 END) as expiring_12_months
        FROM {CATALOG}.{SCHEMA}.silver_leases
        WHERE tenant_name IS NOT NULL
        """
        
        data, error = execute_query(query)
        if error:
            print(f"ERROR in get_portfolio_kpis: {error}")
            return jsonify({'error': error}), 500
        
        if data and len(data) > 0:
            row = data[0]
            kpis = {
                'total_leases': int(row[0]) if row[0] else 0,
                'total_properties': int(row[1]) if row[1] else 0,
                'total_tenants': int(row[2]) if row[2] else 0,
                'markets_count': int(row[3]) if row[3] else 0,
                'avg_rent_psf': float(row[4]) if row[4] else 0,
                'portfolio_walt': float(row[5]) if row[5] else 0,
                'total_exit_risk': int(row[6]) if row[6] else 0,
                'total_rofr': int(row[7]) if row[7] else 0,
                'avg_risk_score': float(row[8]) if row[8] else 0,
                'expiring_12_months': int(row[9]) if row[9] else 0
            }
            return jsonify(kpis)
        
        return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        error_msg = f"Exception in get_portfolio_kpis: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/leases', methods=['GET'])
def get_all_leases():
    """Get all lease details from silver layer (verified leases only)"""
    query = f"""
    SELECT 
        lease_id,
        COALESCE(property_id, 'Unknown Property') as property_name,
        COALESCE(industry_sector, 'Unknown') as market,
        COALESCE(lease_type, 'Unknown') as asset_type,
        tenant_name,
        industry_sector,
        lease_start_date,
        lease_end_date,
        base_rent_psf,
        square_footage,
        estimated_annual_rent,
        annual_escalation_pct,
        validation_status,
        DATEDIFF(lease_end_date, CURRENT_DATE()) / 365.25 as years_remaining
    FROM {CATALOG}.{SCHEMA}.silver_leases
    WHERE tenant_name IS NOT NULL
    ORDER BY lease_end_date ASC
    """
    
    data, error = execute_query(query)
    if error:
        return jsonify({'error': error}), 500
    
    leases = []
    for row in data:
        leases.append({
            'id': row[0],
            'property_name': row[1],
            'market': row[2],
            'asset_type': row[3],
            'tenant_name': row[4],
            'industry': row[5],
            'commencement_date': row[6],
            'expiration_date': row[7],
            'base_rent_psf': float(row[8]) if row[8] else 0,
            'square_feet': float(row[9]) if row[9] else 0,
            'annual_rent': float(row[10]) if row[10] else 0,
            'escalation_pct': float(row[11]) if row[11] else 0,
            'status': row[12],
            'years_remaining': float(row[13]) if row[13] else 0
        })
    
    return jsonify(leases)

@app.route('/api/portfolio/recent', methods=['GET'])
def get_recent_extractions():
    """Get recent extractions from silver layer"""
    query = f"""
    SELECT 
        lease_id,
        CONCAT(tenant_name, '_lease.pdf') as filename,
        validation_status,
        base_rent_psf,
        verified_at
    FROM {CATALOG}.{SCHEMA}.silver_leases
    WHERE tenant_name IS NOT NULL
    ORDER BY verified_at DESC
    LIMIT 10
    """
    
    data, error = execute_query(query)
    if error:
        return jsonify({'error': error}), 500
    
    extractions = []
    for row in data:
        status_map = {
            'VERIFIED': 'Completed',
            'NEW': 'Processing',
            'PENDING': 'Processing',
            'REJECTED': 'Failed'
        }
        
        extractions.append({
            'id': row[0],
            'name': row[1],
            'status': status_map.get(row[2], 'Processing'),
            'accuracy': f"{float(row[3]) if row[3] else 0:.1f}%" if row[3] else '-',
            'date': row[4] if row[4] else 'Unknown'
        })
    
    return jsonify(extractions)

@app.route('/api/portfolio/market-summary', methods=['GET'])
def get_market_summary():
    """Get portfolio health by market from silver layer"""
    query = f"""
    SELECT 
        COALESCE(industry_sector, 'Unknown') as market,
        COUNT(*) as lease_count,
        ROUND(AVG(base_rent_psf), 2) as avg_rent_psf,
        ROUND(AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25), 2) as walt_years
    FROM {CATALOG}.{SCHEMA}.silver_leases
    WHERE lease_end_date IS NOT NULL
    GROUP BY industry_sector
    ORDER BY lease_count DESC
    """
    
    data, error = execute_query(query)
    if error:
        return jsonify({'error': error}), 500
    
    markets = []
    for row in data:
        markets.append({
            'market': row[0],
            'lease_count': int(row[1]) if row[1] else 0,
            'avg_rent_psf': float(row[2]) if row[2] else 0,
            'walt_years': float(row[3]) if row[3] else 0
        })
    
    return jsonify(markets)

@app.route('/api/portfolio/location-summary', methods=['GET'])
def get_location_summary():
    """Get lease counts and data by location (city/state) from silver layer"""
    query = f"""
    SELECT 
        COALESCE(property_city, 'Unknown') as city,
        COALESCE(property_state, 'Unknown') as state,
        COUNT(*) as lease_count,
        SUM(square_footage) as total_sqft,
        AVG(base_rent_psf) as avg_rent_psf,
        SUM(estimated_annual_rent) as total_annual_rent
    FROM {CATALOG}.{SCHEMA}.silver_leases
    WHERE property_city IS NOT NULL
    GROUP BY property_city, property_state
    ORDER BY lease_count DESC
    """
    
    data, error = execute_query(query)
    if error:
        return jsonify({'error': error}), 500
    
    locations = []
    for row in data:
        locations.append({
            'city': row[0],
            'state': row[1],
            'lease_count': int(row[2]) if row[2] else 0,
            'total_sqft': float(row[3]) if row[3] else 0,
            'avg_rent_psf': float(row[4]) if row[4] else 0,
            'total_annual_rent': float(row[5]) if row[5] else 0
        })
    
    return jsonify(locations)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a lease document to Databricks volume"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Uploading file: {file.filename}")
        
        # Read file content
        file_content = file.read()
        print(f"File size: {len(file_content)} bytes")
        
        # Get Databricks client
        client, error = get_client()
        if error:
            return jsonify({'error': f'Databricks connection failed: {error}'}), 500
        
        # Upload to Databricks volume
        volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}"
        print(f"Volume path: {volume_path}")
        
        from utils import upload_to_volume
        success, file_path, error = upload_to_volume(
            client,
            file_content,
            file.filename,
            volume_path
        )
        
        if success:
            print(f"File uploaded successfully: {file_path}")
            return jsonify({
                'success': True,
                'file_path': file_path,
                'message': 'File uploaded successfully'
            })
        else:
            print(f"Upload failed: {error}")
            return jsonify({'error': error}), 500
            
    except Exception as e:
        error_msg = f"Exception in upload_file: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-processing/<path:file_path>', methods=['GET'])
def check_processing(file_path):
    """Check if a file has been processed to bronze layer"""
    try:
        # Extract just the filename from the full path
        filename = file_path.split('/')[-1]
        
        print(f"Checking processing status for file: {filename}")
        
        # First check raw_leases table to see if file was ingested
        raw_query = f"""
        SELECT 
            file_path,
            ingested_at
        FROM {CATALOG}.{SCHEMA}.raw_leases
        WHERE file_path LIKE '%{filename}%'
        LIMIT 1
        """
        
        raw_data, raw_error = execute_query(raw_query)
        
        if raw_error:
            print(f"Error checking raw_leases: {raw_error}")
            return jsonify({'processed': False, 'error': f'Error checking raw ingestion: {raw_error}'}), 500
        
        if not raw_data or len(raw_data) == 0:
            print(f"File not yet ingested to raw_leases")
            return jsonify({'processed': False, 'message': 'File not yet ingested'})
        
        # File found in raw_leases, now check if it's been extracted to bronze
        # Get the ingested_at timestamp from raw to match with uploaded_at in bronze
        raw_ingested_at = raw_data[0][1]  # ingested_at from raw_leases
        
        bronze_query = f"""
        SELECT 
            extraction_id,
            landlord_name,
            landlord_address,
            tenant_name,
            tenant_address,
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
            property_address,
            property_street_address,
            property_city,
            property_state,
            property_zip_code,
            property_country,
            validation_status,
            uploaded_at,
            extracted_at
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE uploaded_at = '{raw_ingested_at}'
        ORDER BY extracted_at DESC
        LIMIT 1
        """
        
        bronze_data, bronze_error = execute_query(bronze_query)
        
        if bronze_error:
            print(f"Error checking bronze_leases: {bronze_error}")
            return jsonify({'processed': False, 'error': f'Error checking extraction: {bronze_error}'}), 500
        
        if bronze_data and len(bronze_data) > 0:
            row = bronze_data[0]
            record = {
                'extraction_id': row[0],
                'landlord_name': row[1],
                'landlord_address': row[2],
                'tenant_name': row[3],
                'tenant_address': row[4],
                'industry_sector': row[5],
                'suite_number': row[6],
                'lease_type': row[7],
                'commencement_date': row[8],
                'expiration_date': row[9],
                'term_months': row[10],
                'rentable_square_feet': row[11],
                'annual_base_rent': row[12],
                'base_rent_psf': row[13],
                'annual_escalation_pct': row[14],
                'renewal_notice_days': row[15],
                'guarantor': row[16],
                'property_address': row[17],
                'property_street_address': row[18],
                'property_city': row[19],
                'property_state': row[20],
                'property_zip_code': row[21],
                'property_country': row[22],
                'validation_status': row[23]
            }
            print(f"Found bronze record for uploaded file: extraction_id={row[0]}")
            return jsonify({'processed': True, 'record': record})
        
        print(f"File ingested to raw but not yet extracted to bronze")
        return jsonify({'processed': False, 'message': 'File ingested but extraction not complete'})
        
    except Exception as e:
        error_msg = f"Exception in check_processing: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'processed': False, 'error': str(e)}), 500

@app.route('/api/validate-record', methods=['POST'])
def validate_record():
    """Validate and update a bronze layer record, then promote to silver"""
    try:
        data = request.json
        extraction_id = data.get('extraction_id')
        updates = data.get('updates', {})
        
        if not extraction_id:
            return jsonify({'error': 'extraction_id is required'}), 400
        
        print(f"Validating record {extraction_id} with updates: {updates}")
        
        # Build update query for bronze layer
        set_clauses = []
        for field, value in updates.items():
            if value is not None and value != '':
                if isinstance(value, str):
                    # Escape single quotes for SQL
                    escaped_value = value.replace("'", "''")
                    set_clauses.append(f"{field} = '{escaped_value}'")
                else:
                    set_clauses.append(f"{field} = {value}")
        
        # Always mark as verified
        set_clauses.append("validation_status = 'VERIFIED'")
        
        # Update bronze layer
        update_query = f"""
        UPDATE {CATALOG}.{SCHEMA}.bronze_leases
        SET {', '.join(set_clauses)}
        WHERE extraction_id = {extraction_id}
        """
        
        print(f"Updating bronze layer: {update_query}")
        _, update_error = execute_query(update_query)
        
        if update_error:
            print(f"ERROR updating bronze layer: {update_error}")
            return jsonify({'error': f'Failed to update bronze layer: {update_error}'}), 500
        
        # Now promote to silver layer
        # First get the updated record from bronze
        select_query = f"""
        SELECT 
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
            property_address,
            property_street_address,
            property_city,
            property_state,
            property_zip_code,
            property_country,
            uploaded_at
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE extraction_id = {extraction_id}
        """
        
        bronze_data, select_error = execute_query(select_query)
        
        if select_error or not bronze_data or len(bronze_data) == 0:
            print(f"ERROR retrieving updated bronze record: {select_error}")
            return jsonify({'error': 'Failed to retrieve updated record'}), 500
        
        row = bronze_data[0]
        
        # Create unique IDs for silver layer
        landlord = row[0] or 'Unknown'
        tenant = row[1] or 'Unknown'
        suite = row[3] or 'Unknown'
        lease_id = f"{landlord}_{tenant}_{suite}".replace(' ', '_').replace("'", "")
        property_id = f"PROP_{landlord}_{suite}".replace(' ', '_').replace("'", "")
        
        # Calculate estimated annual rent
        square_footage = float(row[8]) if row[8] else 0
        base_rent_psf = float(row[10]) if row[10] else 0
        estimated_annual_rent = square_footage * base_rent_psf if square_footage and base_rent_psf else (float(row[9]) if row[9] else 0)
        
        # Get location fields
        property_address = row[14] if len(row) > 14 else None
        property_street_address = row[15] if len(row) > 15 else None
        property_city = row[16] if len(row) > 16 else None
        property_state = row[17] if len(row) > 17 else None
        property_zip_code = row[18] if len(row) > 18 else None
        property_country = row[19] if len(row) > 19 else None
        uploaded_at = row[20] if len(row) > 20 else None
        
        # Prepare values for silver insert
        def sql_safe_value(val):
            if val is None or val == '':
                return 'NULL'
            if isinstance(val, str):
                escaped = val.replace("'", "''")
                return f"'{escaped}'"
            return str(val)
        
        # Insert or merge into silver layer
        silver_insert = f"""
        MERGE INTO {CATALOG}.{SCHEMA}.silver_leases AS target
        USING (
            SELECT 
                {sql_safe_value(lease_id)} as lease_id,
                {sql_safe_value(property_id)} as property_id,
                {sql_safe_value(row[1])} as tenant_name,
                {sql_safe_value(row[2])} as industry_sector,
                {sql_safe_value(row[3])} as suite_id,
                {row[8] if row[8] else 'NULL'} as square_footage,
                {sql_safe_value(row[4])} as lease_type,
                {sql_safe_value(row[5])} as lease_start_date,
                {sql_safe_value(row[6])} as lease_end_date,
                {row[10] if row[10] else 'NULL'} as base_rent_psf,
                {row[11] if row[11] else 'NULL'} as annual_escalation_pct,
                {sql_safe_value(property_address)} as property_address,
                {sql_safe_value(property_street_address)} as property_street_address,
                {sql_safe_value(property_city)} as property_city,
                {sql_safe_value(property_state)} as property_state,
                {sql_safe_value(property_zip_code)} as property_zip_code,
                {sql_safe_value(property_country)} as property_country,
                {estimated_annual_rent} as estimated_annual_rent,
                NULL as next_escalation_date,
                'AI_HUMAN_VERIFIED' as enhancement_source,
                'VERIFIED' as validation_status,
                'web_user' as verified_by,
                CURRENT_TIMESTAMP() as verified_at,
                NULL as raw_document_path,
                {sql_safe_value(uploaded_at)} as uploaded_at,
                CURRENT_TIMESTAMP() as updated_at
        ) AS source
        ON target.lease_id = source.lease_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        """
        
        print(f"Promoting to silver layer...")
        _, silver_error = execute_query(silver_insert)
        
        if silver_error:
            print(f"ERROR promoting to silver layer: {silver_error}")
            return jsonify({
                'success': True,
                'message': 'Record validated in bronze layer but failed to promote to silver',
                'warning': silver_error
            })
        
        print(f"Successfully validated and promoted record {extraction_id} to silver layer")
        return jsonify({
            'success': True,
            'message': 'Record validated and promoted to silver layer successfully'
        })
        
    except Exception as e:
        error_msg = f"Exception in validate_record: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/new', methods=['GET'])
def get_new_records():
    """Get all records with validation_status = 'NEW'"""
    try:
        query = f"""
        SELECT 
            extraction_id,
            landlord_name,
            landlord_address,
            tenant_name,
            tenant_address,
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
            property_address,
            property_street_address,
            property_city,
            property_state,
            property_zip_code,
            property_country,
            validation_status,
            uploaded_at,
            extracted_at
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE validation_status = 'NEW'
        ORDER BY extracted_at DESC
        """
        
        data, error = execute_query(query)
        if error:
            print(f"ERROR in get_new_records: {error}")
            return jsonify({'error': error}), 500
        
        records = []
        for row in data:
            records.append({
                'extraction_id': row[0],
                'landlord_name': row[1],
                'landlord_address': row[2],
                'tenant_name': row[3],
                'tenant_address': row[4],
                'industry_sector': row[5],
                'suite_number': row[6],
                'lease_type': row[7],
                'commencement_date': row[8],
                'expiration_date': row[9],
                'term_months': row[10],
                'rentable_square_feet': row[11],
                'annual_base_rent': row[12],
                'base_rent_psf': row[13],
                'annual_escalation_pct': row[14],
                'renewal_notice_days': row[15],
                'guarantor': row[16],
                'property_address': row[17],
                'property_street_address': row[18],
                'property_city': row[19],
                'property_state': row[20],
                'property_zip_code': row[21],
                'property_country': row[22],
                'validation_status': row[23],
                'uploaded_at': row[24],
                'extracted_at': row[25]
            })
        
        return jsonify(records)
        
    except Exception as e:
        error_msg = f"Exception in get_new_records: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/validate-multiple', methods=['POST'])
def validate_multiple_records():
    """Validate multiple records and promote them to silver layer"""
    try:
        data = request.json
        records = data.get('records', [])
        
        if not records or len(records) == 0:
            return jsonify({'error': 'No records provided'}), 400
        
        print(f"Validating {len(records)} records")
        
        success_count = 0
        failed_records = []
        
        for record in records:
            extraction_id = record.get('extraction_id')
            updates = record.get('updates', {})
            
            try:
                # Build update query for bronze layer
                set_clauses = []
                for field, value in updates.items():
                    if value is not None and value != '':
                        if isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            set_clauses.append(f"{field} = '{escaped_value}'")
                        else:
                            set_clauses.append(f"{field} = {value}")
                
                # Always mark as verified
                set_clauses.append("validation_status = 'VERIFIED'")
                
                # Update bronze layer
                if set_clauses:
                    update_query = f"""
                    UPDATE {CATALOG}.{SCHEMA}.bronze_leases
                    SET {', '.join(set_clauses)}
                    WHERE extraction_id = {extraction_id}
                    """
                    
                    _, update_error = execute_query(update_query)
                    
                    if update_error:
                        print(f"ERROR updating bronze layer for {extraction_id}: {update_error}")
                        failed_records.append({'extraction_id': extraction_id, 'error': update_error})
                        continue
                else:
                    # Just mark as verified
                    update_query = f"""
                    UPDATE {CATALOG}.{SCHEMA}.bronze_leases
                    SET validation_status = 'VERIFIED'
                    WHERE extraction_id = {extraction_id}
                    """
                    _, update_error = execute_query(update_query)
                    if update_error:
                        print(f"ERROR updating bronze layer for {extraction_id}: {update_error}")
                        failed_records.append({'extraction_id': extraction_id, 'error': update_error})
                        continue
                
                # Get the updated record from bronze
                select_query = f"""
                SELECT 
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
                    property_address,
                    property_street_address,
                    property_city,
                    property_state,
                    property_zip_code,
                    property_country,
                    uploaded_at
                FROM {CATALOG}.{SCHEMA}.bronze_leases
                WHERE extraction_id = {extraction_id}
                """
                
                bronze_data, select_error = execute_query(select_query)
                
                if select_error or not bronze_data or len(bronze_data) == 0:
                    print(f"ERROR retrieving updated bronze record for {extraction_id}: {select_error}")
                    failed_records.append({'extraction_id': extraction_id, 'error': 'Failed to retrieve updated record'})
                    continue
                
                row = bronze_data[0]
                
                # Create unique IDs for silver layer
                landlord = row[0] or 'Unknown'
                tenant = row[1] or 'Unknown'
                suite = row[3] or 'Unknown'
                lease_id = f"{landlord}_{tenant}_{suite}".replace(' ', '_').replace("'", "")
                property_id = f"PROP_{landlord}_{suite}".replace(' ', '_').replace("'", "")
                
                # Calculate estimated annual rent
                square_footage = float(row[8]) if row[8] else 0
                base_rent_psf = float(row[10]) if row[10] else 0
                estimated_annual_rent = square_footage * base_rent_psf if square_footage and base_rent_psf else (float(row[9]) if row[9] else 0)
                
                # Get location fields
                property_address = row[14] if len(row) > 14 else None
                property_street_address = row[15] if len(row) > 15 else None
                property_city = row[16] if len(row) > 16 else None
                property_state = row[17] if len(row) > 17 else None
                property_zip_code = row[18] if len(row) > 18 else None
                property_country = row[19] if len(row) > 19 else None
                uploaded_at = row[20] if len(row) > 20 else None
                
                # Prepare values for silver insert
                def sql_safe_value(val):
                    if val is None or val == '':
                        return 'NULL'
                    if isinstance(val, str):
                        escaped = val.replace("'", "''")
                        return f"'{escaped}'"
                    return str(val)
                
                # Insert or merge into silver layer
                silver_insert = f"""
                MERGE INTO {CATALOG}.{SCHEMA}.silver_leases AS target
                USING (
                    SELECT 
                        {sql_safe_value(lease_id)} as lease_id,
                        {sql_safe_value(property_id)} as property_id,
                        {sql_safe_value(row[1])} as tenant_name,
                        {sql_safe_value(row[2])} as industry_sector,
                        {sql_safe_value(row[3])} as suite_id,
                        {row[8] if row[8] else 'NULL'} as square_footage,
                        {sql_safe_value(row[4])} as lease_type,
                        {sql_safe_value(row[5])} as lease_start_date,
                        {sql_safe_value(row[6])} as lease_end_date,
                        {row[10] if row[10] else 'NULL'} as base_rent_psf,
                        {row[11] if row[11] else 'NULL'} as annual_escalation_pct,
                        {sql_safe_value(property_address)} as property_address,
                        {sql_safe_value(property_street_address)} as property_street_address,
                        {sql_safe_value(property_city)} as property_city,
                        {sql_safe_value(property_state)} as property_state,
                        {sql_safe_value(property_zip_code)} as property_zip_code,
                        {sql_safe_value(property_country)} as property_country,
                        {estimated_annual_rent} as estimated_annual_rent,
                        NULL as next_escalation_date,
                        'AI_HUMAN_VERIFIED' as enhancement_source,
                        'VERIFIED' as validation_status,
                        'web_user' as verified_by,
                        CURRENT_TIMESTAMP() as verified_at,
                        NULL as raw_document_path,
                        {sql_safe_value(uploaded_at)} as uploaded_at,
                        CURRENT_TIMESTAMP() as updated_at
                ) AS source
                ON target.lease_id = source.lease_id
                WHEN MATCHED THEN UPDATE SET *
                WHEN NOT MATCHED THEN INSERT *
                """
                
                _, silver_error = execute_query(silver_insert)
                
                if silver_error:
                    print(f"ERROR promoting to silver layer for {extraction_id}: {silver_error}")
                    failed_records.append({'extraction_id': extraction_id, 'error': f'Silver promotion failed: {silver_error}'})
                    continue
                
                success_count += 1
                print(f"Successfully validated and promoted record {extraction_id}")
                
            except Exception as e:
                error_msg = f"Exception processing record {extraction_id}: {str(e)}"
                print(error_msg)
                failed_records.append({'extraction_id': extraction_id, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'validated_count': success_count,
            'failed_count': len(failed_records),
            'failed_records': failed_records
        })
        
    except Exception as e:
        error_msg = f"Exception in validate_multiple_records: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/query', methods=['POST'])
def chat_query():
    """Process natural language queries about lease data"""
    try:
        data = request.json
        query = data.get('query', '').lower()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        print(f"Processing chat query: {query}")
        
        # Simple keyword-based query routing
        response = None
        query_data = None
        
        # Total value / revenue queries
        if any(word in query for word in ['total value', 'total revenue', 'total rent', 'portfolio value']):
            sql = f"""
            SELECT 
                COUNT(*) as total_leases,
                SUM(estimated_annual_rent) as total_annual_rent,
                AVG(base_rent_psf) as avg_rent_psf,
                SUM(square_footage) as total_sqft
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE estimated_annual_rent IS NOT NULL
            """
            data, error = execute_query(sql)
            if not error and data:
                row = data[0]
                total_rent = float(row[1]) if row[1] else 0
                response = f"Your portfolio has {int(row[0])} active leases with a total annual rent of ${total_rent:,.2f}. The average rent is ${float(row[2]) if row[2] else 0:.2f} per square foot across {float(row[3]) if row[3] else 0:,.0f} total square feet."
                query_data = {
                    'total_leases': int(row[0]),
                    'total_annual_rent': total_rent,
                    'avg_rent_psf': float(row[2]) if row[2] else 0,
                    'total_sqft': float(row[3]) if row[3] else 0
                }
        
        # Expiring leases
        elif any(word in query for word in ['expiring', 'expiration', 'expire', 'ending']):
            months = 12
            if '6 month' in query:
                months = 6
            elif '12 month' in query or 'year' in query:
                months = 12
            elif '24 month' in query or '2 year' in query:
                months = 24
            
            sql = f"""
            SELECT 
                tenant_name,
                lease_end_date,
                estimated_annual_rent,
                DATEDIFF(lease_end_date, CURRENT_DATE()) as days_until_expiration
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE lease_end_date IS NOT NULL
                AND DATEDIFF(lease_end_date, CURRENT_DATE()) BETWEEN 0 AND {months * 30}
            ORDER BY lease_end_date ASC
            LIMIT 10
            """
            data, error = execute_query(sql)
            if not error and data:
                if len(data) == 0:
                    response = f"Good news! There are no leases expiring in the next {months} months."
                else:
                    leases = []
                    for row in data:
                        leases.append({
                            'tenant': row[0],
                            'expiration_date': row[1],
                            'annual_rent': float(row[2]) if row[2] else 0,
                            'days_remaining': int(row[3]) if row[3] else 0
                        })
                    response = f"There are {len(data)} leases expiring in the next {months} months. The first to expire is {data[0][0]} on {data[0][1]}, followed by {data[1][0] if len(data) > 1 else 'others'}."
                    query_data = leases
        
        # Highest square footage / largest tenants
        elif any(word in query for word in ['highest square', 'largest tenant', 'biggest', 'most space']):
            sql = f"""
            SELECT 
                tenant_name,
                square_footage,
                estimated_annual_rent,
                base_rent_psf
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE square_footage IS NOT NULL
            ORDER BY square_footage DESC
            LIMIT 5
            """
            data, error = execute_query(sql)
            if not error and data:
                tenants = []
                for row in data:
                    tenants.append({
                        'tenant': row[0],
                        'square_feet': float(row[1]) if row[1] else 0,
                        'annual_rent': float(row[2]) if row[2] else 0,
                        'rent_psf': float(row[3]) if row[3] else 0
                    })
                top_tenant = data[0]
                response = f"The tenant with the highest square footage is {top_tenant[0]} with {float(top_tenant[1]):,.0f} square feet, paying ${float(top_tenant[2]):,.2f} annually. Here are the top 5 tenants by space."
                query_data = tenants
        
        # Average rent by industry
        elif any(word in query for word in ['average rent', 'rent by industry', 'industry sector', 'by market']):
            sql = f"""
            SELECT 
                COALESCE(industry_sector, 'Unknown') as industry,
                COUNT(*) as lease_count,
                AVG(base_rent_psf) as avg_rent_psf,
                AVG(estimated_annual_rent) as avg_annual_rent
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE base_rent_psf IS NOT NULL
            GROUP BY industry_sector
            ORDER BY avg_rent_psf DESC
            """
            data, error = execute_query(sql)
            if not error and data:
                industries = []
                for row in data:
                    industries.append({
                        'industry': row[0],
                        'lease_count': int(row[1]),
                        'avg_rent_psf': float(row[2]) if row[2] else 0,
                        'avg_annual_rent': float(row[3]) if row[3] else 0
                    })
                response = f"I found {len(data)} different industry sectors in your portfolio. The highest average rent is in {data[0][0]} at ${float(data[0][2]):.2f} per square foot, with {int(data[0][1])} leases."
                query_data = industries
        
        # List all tenants
        elif any(word in query for word in ['list tenant', 'all tenant', 'show tenant', 'who are']):
            sql = f"""
            SELECT 
                tenant_name,
                industry_sector,
                estimated_annual_rent,
                lease_end_date
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE tenant_name IS NOT NULL
            ORDER BY estimated_annual_rent DESC
            LIMIT 10
            """
            data, error = execute_query(sql)
            if not error and data:
                tenants = []
                for row in data:
                    tenants.append({
                        'tenant': row[0],
                        'industry': row[1],
                        'annual_rent': float(row[2]) if row[2] else 0,
                        'expiration_date': row[3]
                    })
                response = f"You have {len(tenants)} tenants in your portfolio (showing top 10 by rent). The largest is {data[0][0]} in the {data[0][1]} sector, paying ${float(data[0][2]):,.2f} annually."
                query_data = tenants
        
        # Default response
        else:
            response = "I can help you with questions about:\n\n" + \
                      "• Total portfolio value and revenue\n" + \
                      "• Leases expiring soon (next 6, 12, or 24 months)\n" + \
                      "• Tenants with the highest square footage\n" + \
                      "• Average rent by industry sector\n" + \
                      "• List of all tenants\n\n" + \
                      "Try asking something like 'What is the total value of all active leases?' or 'Show me leases expiring in the next 12 months.'"
        
        return jsonify({
            'response': response,
            'data': query_data
        })
        
    except Exception as e:
        error_msg = f"Exception in chat_query: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

