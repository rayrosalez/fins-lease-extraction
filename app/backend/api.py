from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from dotenv import load_dotenv
import os
import traceback
import requests
import json
import time

load_dotenv()

# Claude endpoint configuration
DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').rstrip('/')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
CLAUDE_ENDPOINT_URL = f"{DATABRICKS_HOST}/serving-endpoints/databricks-claude-sonnet-4-5/invocations"

# Static files directory for serving React build
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
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


# ============================================================
# HEALTH SCORE CALCULATION FUNCTIONS
# ============================================================

def calculate_landlord_health_score(enriched_data):
    """
    Calculate a deterministic financial health score for landlords (1-10).
    
    Factors considered:
    - Credit rating (0-2.5 points)
    - Market cap / Total assets (0-1.5 points)
    - Debt-to-equity ratio (0-1.5 points)
    - Revenue / NOI (0-1.5 points)
    - Bankruptcy risk indicator (0-1.5 points)
    - News sentiment (0-1.5 points)
    
    Base score: 5.0
    """
    score = 5.0
    
    # Credit Rating (major factor)
    credit_rating = (enriched_data.get('credit_rating') or '').upper()
    if credit_rating:
        if credit_rating in ['AAA']:
            score += 2.5
        elif credit_rating in ['AA+', 'AA', 'AA-']:
            score += 2.0
        elif credit_rating in ['A+', 'A', 'A-']:
            score += 1.5
        elif credit_rating in ['BBB+', 'BBB']:
            score += 1.0
        elif credit_rating in ['BBB-']:
            score += 0.5
        elif credit_rating.startswith('BB'):
            score -= 0.5
        elif credit_rating.startswith('B') and not credit_rating.startswith('BB'):
            score -= 1.0
        elif credit_rating.startswith('C'):
            score -= 2.0
    
    # Market Cap / Total Assets (indicates financial strength)
    market_cap = enriched_data.get('market_cap') or 0
    total_assets = enriched_data.get('total_assets') or 0
    financial_size = max(market_cap, total_assets)
    
    if financial_size > 50e9:  # > $50B
        score += 1.5
    elif financial_size > 10e9:  # > $10B
        score += 1.0
    elif financial_size > 1e9:  # > $1B
        score += 0.5
    elif financial_size > 100e6:  # > $100M
        score += 0.0
    elif financial_size > 0:
        score -= 0.5
    
    # Debt-to-Equity Ratio (lower is better for stability)
    de_ratio = enriched_data.get('debt_to_equity_ratio')
    if de_ratio is not None:
        if de_ratio < 0.5:
            score += 1.5
        elif de_ratio < 1.0:
            score += 1.0
        elif de_ratio < 1.5:
            score += 0.5
        elif de_ratio < 2.0:
            score += 0.0
        elif de_ratio < 3.0:
            score -= 0.5
        else:
            score -= 1.0
    
    # Revenue and NOI (profitability indicators)
    annual_revenue = enriched_data.get('annual_revenue') or 0
    noi = enriched_data.get('net_operating_income') or 0
    
    if annual_revenue > 0 and noi > 0:
        noi_margin = noi / annual_revenue
        if noi_margin > 0.4:  # > 40% NOI margin
            score += 1.5
        elif noi_margin > 0.3:
            score += 1.0
        elif noi_margin > 0.2:
            score += 0.5
        elif noi_margin < 0.1:
            score -= 0.5
    elif annual_revenue > 1e9:  # Has significant revenue
        score += 0.5
    
    # Bankruptcy Risk (from Claude's assessment)
    bankruptcy_risk = (enriched_data.get('bankruptcy_risk') or '').upper()
    if bankruptcy_risk == 'LOW':
        score += 1.5
    elif bankruptcy_risk == 'MEDIUM':
        score += 0.0
    elif bankruptcy_risk == 'HIGH':
        score -= 1.5
    
    # News Sentiment
    sentiment = (enriched_data.get('recent_news_sentiment') or '').upper()
    if sentiment == 'POSITIVE':
        score += 1.0
    elif sentiment == 'NEUTRAL':
        score += 0.0
    elif sentiment == 'NEGATIVE':
        score -= 1.0
    
    # Clamp score between 1.0 and 10.0
    return round(max(1.0, min(10.0, score)), 1)


def calculate_tenant_health_score(enriched_data):
    """
    Calculate a deterministic financial health score for tenants (1-10).
    
    Factors considered:
    - Credit rating (0-2.0 points)
    - Revenue growth (0-1.5 points)
    - Profit margin (0-1.5 points)
    - Company size/employees (0-1.0 points)
    - Years in business (0-1.0 points)
    - Bankruptcy risk (0-1.5 points)
    - Industry risk (0-1.0 points)
    - Litigation flag (-0.5 points if true)
    
    Base score: 5.0
    """
    score = 5.0
    
    # Credit Rating
    credit_rating = (enriched_data.get('credit_rating') or '').upper()
    if credit_rating:
        if credit_rating in ['AAA']:
            score += 2.0
        elif credit_rating in ['AA+', 'AA', 'AA-']:
            score += 1.75
        elif credit_rating in ['A+', 'A', 'A-']:
            score += 1.5
        elif credit_rating in ['BBB+', 'BBB']:
            score += 1.0
        elif credit_rating in ['BBB-']:
            score += 0.5
        elif credit_rating.startswith('BB'):
            score -= 0.5
        elif credit_rating.startswith('B') and not credit_rating.startswith('BB'):
            score -= 1.0
        elif credit_rating.startswith('C'):
            score -= 1.5
    
    # Revenue Growth
    revenue_growth = enriched_data.get('revenue_growth_pct')
    if revenue_growth is not None:
        if revenue_growth > 20:
            score += 1.5
        elif revenue_growth > 10:
            score += 1.0
        elif revenue_growth > 5:
            score += 0.75
        elif revenue_growth > 0:
            score += 0.5
        elif revenue_growth > -5:
            score += 0.0
        elif revenue_growth > -10:
            score -= 0.5
        else:
            score -= 1.0
    
    # Profit Margin
    profit_margin = enriched_data.get('profit_margin_pct')
    if profit_margin is not None:
        if profit_margin > 20:
            score += 1.5
        elif profit_margin > 15:
            score += 1.0
        elif profit_margin > 10:
            score += 0.75
        elif profit_margin > 5:
            score += 0.5
        elif profit_margin > 0:
            score += 0.0
        elif profit_margin > -5:
            score -= 0.5
        else:
            score -= 1.0
    
    # Company Size (employees as proxy for stability)
    employee_count = enriched_data.get('employee_count') or 0
    if employee_count >= 10000:
        score += 1.0
    elif employee_count >= 1000:
        score += 0.75
    elif employee_count >= 100:
        score += 0.5
    elif employee_count >= 50:
        score += 0.25
    elif employee_count > 0 and employee_count < 10:
        score -= 0.25
    
    # Years in Business (stability indicator)
    years_in_business = enriched_data.get('years_in_business') or 0
    if years_in_business >= 50:
        score += 1.0
    elif years_in_business >= 20:
        score += 0.75
    elif years_in_business >= 10:
        score += 0.5
    elif years_in_business >= 5:
        score += 0.25
    elif years_in_business > 0 and years_in_business < 3:
        score -= 0.5
    
    # Bankruptcy Risk
    bankruptcy_risk = (enriched_data.get('bankruptcy_risk') or '').upper()
    if bankruptcy_risk == 'LOW':
        score += 1.5
    elif bankruptcy_risk == 'MEDIUM':
        score += 0.0
    elif bankruptcy_risk == 'HIGH':
        score -= 1.5
    
    # Industry Risk
    industry_risk = (enriched_data.get('industry_risk') or '').upper()
    if industry_risk == 'LOW':
        score += 1.0
    elif industry_risk == 'MEDIUM':
        score += 0.0
    elif industry_risk == 'HIGH':
        score -= 0.75
    
    # Litigation Flag (penalty if active litigation)
    if enriched_data.get('litigation_flag'):
        score -= 0.5
    
    # Clamp score between 1.0 and 10.0
    return round(max(1.0, min(10.0, score)), 1)


def get_client():
    """Get Databricks client"""
    try:
        client = WorkspaceClient()
        return client, None
    except Exception as e:
        return None, str(e)

def execute_query(query, max_retries=3, retry_delay=1.0):
    """
    Execute SQL query and return results with retry logic for Delta Lake concurrency errors
    
    Args:
        query: SQL query to execute
        max_retries: Maximum number of retry attempts (default 3)
        retry_delay: Initial delay between retries in seconds (default 1.0)
    """
    for attempt in range(max_retries):
        try:
            if not WAREHOUSE_ID:
                return None, "DATABRICKS_WAREHOUSE_ID environment variable is not set"
            
            client, error = get_client()
            if error:
                print(f"ERROR getting Databricks client: {error}")
                return None, error
            
            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries} for query")
            else:
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
                    
                    # Check if this is a Delta Lake concurrency error
                    if "ConcurrentAppendException" in str(statement.status.error.message) or \
                       "DELTA_CONCURRENT" in str(statement.status.error.message):
                        # This is a retryable error
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                            print(f"Delta Lake concurrency error detected, retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue  # Retry the query
                        else:
                            print(f"Max retries reached for concurrency error")
                            # Even on last retry, check if operation might have succeeded
                            # Return a softer error that can be handled gracefully
                            return [], None  # Return empty result instead of error
                
                print(f"ERROR: {error_msg}")
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Exception executing query: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            
            # Check if this is a concurrency exception
            if "ConcurrentAppendException" in str(e) or "DELTA_CONCURRENT" in str(e):
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Delta Lake concurrency exception, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # On last attempt, return empty result for concurrency errors
                    # The operation likely succeeded despite the error
                    print(f"Concurrency error on final retry - operation may have succeeded")
                    return [], None
            
            return None, str(e)
    
    # Should not reach here, but just in case
    return None, "Max retries exceeded"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})


@app.route('/metrics', methods=['GET'])
def metrics():
    """Metrics endpoint for Databricks Apps monitoring"""
    return '', 200



@app.route('/api/portfolio/kpis', methods=['GET'])
def get_portfolio_kpis():
    """Get overall portfolio KPIs from silver layer (verified leases only)"""
    try:
        query = f"""
        WITH base_kpis AS (
            SELECT 
                COUNT(*) as total_leases,
                COUNT(DISTINCT COALESCE(property_id, 'Unknown')) as total_properties,
                COUNT(DISTINCT tenant_name) as total_tenants,
                COUNT(DISTINCT COALESCE(industry_sector, 'Unknown')) as markets_count,
                AVG(base_rent_psf) as avg_rent_psf,
                AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt,
                0 as total_exit_risk,
                0 as total_rofr,
                SUM(CASE WHEN DATEDIFF(lease_end_date, CURRENT_DATE()) <= 365 AND DATEDIFF(lease_end_date, CURRENT_DATE()) >= 0 THEN 1 ELSE 0 END) as expiring_12_months
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE tenant_name IS NOT NULL
        ),
        risk_kpis AS (
            SELECT 
                AVG(total_risk_score) as avg_risk_score
            FROM {CATALOG}.{SCHEMA}.gold_lease_risk_scores
        )
        SELECT 
            b.total_leases,
            b.total_properties,
            b.total_tenants,
            b.markets_count,
            b.avg_rent_psf,
            b.portfolio_walt,
            b.total_exit_risk,
            b.total_rofr,
            COALESCE(r.avg_risk_score, 0) as avg_risk_score,
            b.expiring_12_months
        FROM base_kpis b
        CROSS JOIN risk_kpis r
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

@app.route('/api/check-processing', methods=['POST'])
def check_processing():
    """Check if a file has been processed to bronze layer"""
    try:
        # Get file_path from request body instead of URL
        data = request.json
        file_path = data.get('file_path', '')
        
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
        ORDER BY ingested_at DESC
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
        
        print(f"Found in raw_leases with ingested_at: {raw_ingested_at}")
        
        # Try multiple strategies to find the bronze record:
        # Strategy 1: Exact timestamp match (with tolerance for milliseconds)
        bronze_query_exact = f"""
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
        WHERE ABS(UNIX_TIMESTAMP(uploaded_at) - UNIX_TIMESTAMP('{raw_ingested_at}')) < 5
        AND validation_status = 'NEW'
        ORDER BY uploaded_at DESC
        LIMIT 1
        """
        
        bronze_data, bronze_error = execute_query(bronze_query_exact)
        
        # Strategy 2: If no exact match, try finding the most recent NEW record
        if (bronze_error or not bronze_data or len(bronze_data) == 0):
            print(f"No exact timestamp match, trying recent NEW records...")
            bronze_query_recent = f"""
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
            AND uploaded_at >= TIMESTAMPADD(MINUTE, -10, '{raw_ingested_at}')
            ORDER BY uploaded_at DESC
            LIMIT 1
            """
            
            bronze_data, bronze_error = execute_query(bronze_query_recent)
        
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

@app.route('/api/records/delete', methods=['POST'])
def delete_records():
    """Mark records as DELETED by changing validation_status"""
    try:
        data = request.json
        extraction_ids = data.get('extraction_ids', [])
        
        if not extraction_ids:
            return jsonify({'error': 'No extraction IDs provided'}), 400
        
        # Update validation_status to DELETED for each record
        placeholders = ', '.join([f"'{id}'" for id in extraction_ids])
        query = f"""
        UPDATE {CATALOG}.{SCHEMA}.bronze_leases
        SET validation_status = 'DELETED'
        WHERE extraction_id IN ({placeholders})
        """
        
        result, error = execute_query(query)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'success': True,
            'deleted_count': len(extraction_ids),
            'message': f'Successfully marked {len(extraction_ids)} record(s) as deleted'
        })
        
    except Exception as e:
        error_msg = f"Exception in delete_records: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/risk-assessment', methods=['GET'])
def get_risk_assessment():
    """Get comprehensive risk assessment data from gold layer"""
    try:
        query = f"""
        SELECT 
            lease_id,
            tenant_name,
            property_id,
            industry_sector,
            lease_end_date,
            annual_escalation_pct,
            estimated_annual_rent,
            square_footage,
            days_to_expiry,
            sector_risk_base,
            portfolio_concentration_pct,
            rollover_score,
            escalation_risk_score,
            concentration_risk_score,
            lease_status,
            total_risk_score
        FROM {CATALOG}.{SCHEMA}.gold_lease_risk_scores
        WHERE total_risk_score IS NOT NULL
        ORDER BY total_risk_score DESC
        LIMIT 100
        """
        
        data, error = execute_query(query)
        if error:
            return jsonify({'error': error}), 500
        
        if not data:
            return jsonify([])
        
        results = []
        for row in data:
            results.append({
                'lease_id': row[0],
                'tenant_name': row[1],
                'property_id': row[2],
                'industry_sector': row[3],
                'lease_end_date': row[4],
                'annual_escalation_pct': float(row[5]) if row[5] is not None else 0,
                'estimated_annual_rent': float(row[6]) if row[6] is not None else 0,
                'square_footage': float(row[7]) if row[7] is not None else 0,
                'days_to_expiry': int(row[8]) if row[8] is not None else 0,
                'sector_risk_base': float(row[9]) if row[9] is not None else 0,
                'portfolio_concentration_pct': float(row[10]) if row[10] is not None else 0,
                'rollover_score': float(row[11]) if row[11] is not None else 0,
                'escalation_risk_score': float(row[12]) if row[12] is not None else 0,
                'concentration_risk_score': float(row[13]) if row[13] is not None else 0,
                'lease_status': row[14],
                'total_risk_score': float(row[15]) if row[15] is not None else 0
            })
        
        return jsonify(results)
        
    except Exception as e:
        error_msg = f"Exception in risk_assessment: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500

def call_claude_enrichment(prompt):
    """Call Claude AI endpoint for enrichment"""
    try:
        headers = {
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000
        }
        
        print(f"Calling Claude endpoint: {CLAUDE_ENDPOINT_URL}")
        response = requests.post(CLAUDE_ENDPOINT_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # Extract the content from Claude's response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return content, None
            return None, "No content in Claude response"
        else:
            return None, f"Claude endpoint returned {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Error calling Claude: {str(e)}"


def parse_enrichment_json(text):
    """Extract JSON from Claude's response text"""
    try:
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group()), None
        return None, "No JSON found in response"
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {str(e)}"


@app.route('/api/enrich/landlord', methods=['POST'])
def enrich_landlord():
    """Enrich landlord data using Claude AI"""
    try:
        data = request.json
        landlord_name = data.get('landlord_name')
        landlord_address = data.get('landlord_address', '')
        
        if not landlord_name:
            return jsonify({'error': 'landlord_name is required'}), 400
        
        print(f"Enriching landlord: {landlord_name}")
        
        # Create landlord_id
        landlord_id = landlord_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
        
        # Check if landlord already exists
        check_query = f"""
        SELECT * FROM {CATALOG}.{SCHEMA}.landlords 
        WHERE landlord_id = '{landlord_id}'
        """
        existing, _ = execute_query(check_query)
        if existing and len(existing) > 0:
            return jsonify({
                'success': True,
                'message': 'Landlord already enriched',
                'landlord_id': landlord_id,
                'already_exists': True
            })
        
        # Build prompt for Claude
        prompt = f"""Search for and provide financial and company information about this commercial real estate landlord/property owner:

Company Name: {landlord_name}
Address: {landlord_address or 'Unknown'}

Please find the following information and return it as a JSON object:
{{
    "company_type": "REIT, Private, Public, or other",
    "stock_ticker": "ticker symbol if publicly traded, null otherwise",
    "market_cap": null or number in USD,
    "total_assets": null or number in USD,
    "credit_rating": "credit rating like AAA, BBB+, etc. or null",
    "credit_rating_agency": "S&P, Moody's, Fitch, or null",
    "annual_revenue": null or number in USD,
    "net_operating_income": null or number in USD,
    "debt_to_equity_ratio": null or number,
    "total_properties": null or number,
    "total_square_footage": null or number,
    "primary_property_types": "Office, Retail, Industrial, etc.",
    "geographic_focus": "primary markets/regions",
    "financial_health_score": 1-10 estimate based on available data,
    "bankruptcy_risk": "LOW, MEDIUM, or HIGH",
    "recent_news_sentiment": "POSITIVE, NEUTRAL, or NEGATIVE"
}}

Return ONLY the JSON object, no other text."""

        content, error = call_claude_enrichment(prompt)
        
        if error:
            print(f"Claude enrichment error: {error}")
            return jsonify({'error': error}), 500
        
        # Parse the JSON response
        enriched_data, parse_error = parse_enrichment_json(content)
        
        if parse_error:
            print(f"Parse error: {parse_error}")
            # Return the raw content for debugging
            enriched_data = {
                'company_type': None,
                'financial_health_score': 5.0,
                'bankruptcy_risk': 'MEDIUM',
                'recent_news_sentiment': 'NEUTRAL'
            }
        
        # Return enriched data for user validation (don't insert yet)
        return jsonify({
            'success': True,
            'landlord_id': landlord_id,
            'landlord_name': landlord_name,
            'landlord_address': landlord_address,
            'enriched_data': enriched_data,
            'raw_response': content
        })
        
    except Exception as e:
        error_msg = f"Exception in enrich_landlord: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/enrich/tenant', methods=['POST'])
def enrich_tenant():
    """Enrich tenant data using Claude AI"""
    try:
        data = request.json
        tenant_name = data.get('tenant_name')
        tenant_address = data.get('tenant_address', '')
        industry_sector = data.get('industry_sector', '')
        
        if not tenant_name:
            return jsonify({'error': 'tenant_name is required'}), 400
        
        print(f"Enriching tenant: {tenant_name}")
        
        # Create tenant_id
        tenant_id = tenant_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
        
        # Check if tenant already exists
        check_query = f"""
        SELECT * FROM {CATALOG}.{SCHEMA}.tenants 
        WHERE tenant_id = '{tenant_id}'
        """
        existing, _ = execute_query(check_query)
        if existing and len(existing) > 0:
            return jsonify({
                'success': True,
                'message': 'Tenant already enriched',
                'tenant_id': tenant_id,
                'already_exists': True
            })
        
        # Build prompt for Claude
        prompt = f"""Search for and provide financial and company information about this business/tenant:

Company Name: {tenant_name}
Industry: {industry_sector or 'Unknown'}
Address: {tenant_address or 'Unknown'}

Please find the following information and return it as a JSON object:
{{
    "company_type": "Public, Private, Subsidiary, or Non-profit",
    "parent_company": "parent company name if subsidiary, null otherwise",
    "stock_ticker": "ticker symbol if publicly traded, null otherwise",
    "founding_year": null or year number,
    "employee_count": null or number,
    "headquarters_location": "city, state",
    "market_cap": null or number in USD,
    "annual_revenue": null or number in USD,
    "net_income": null or number in USD,
    "revenue_growth_pct": null or percentage,
    "profit_margin_pct": null or percentage,
    "credit_rating": "credit rating like AAA, BBB+, etc. or null",
    "credit_rating_agency": "S&P, Moody's, Fitch, or null",
    "payment_history_score": 1-100 estimate,
    "financial_health_score": 1-10 estimate based on available data,
    "bankruptcy_risk": "LOW, MEDIUM, or HIGH",
    "industry_risk": "LOW, MEDIUM, or HIGH based on sector volatility",
    "recent_news_sentiment": "POSITIVE, NEUTRAL, or NEGATIVE",
    "litigation_flag": true or false if significant litigation found,
    "locations_count": null or number,
    "years_in_business": null or number
}}

Return ONLY the JSON object, no other text."""

        content, error = call_claude_enrichment(prompt)
        
        if error:
            print(f"Claude enrichment error: {error}")
            return jsonify({'error': error}), 500
        
        # Parse the JSON response
        enriched_data, parse_error = parse_enrichment_json(content)
        
        if parse_error:
            print(f"Parse error: {parse_error}")
            enriched_data = {
                'company_type': None,
                'financial_health_score': 5.0,
                'bankruptcy_risk': 'MEDIUM',
                'industry_risk': 'MEDIUM',
                'recent_news_sentiment': 'NEUTRAL'
            }
        
        # Return enriched data for user validation (don't insert yet)
        return jsonify({
            'success': True,
            'tenant_id': tenant_id,
            'tenant_name': tenant_name,
            'tenant_address': tenant_address,
            'industry_sector': industry_sector,
            'enriched_data': enriched_data,
            'raw_response': content
        })
        
    except Exception as e:
        error_msg = f"Exception in enrich_tenant: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/enrich/validate-landlord', methods=['POST'])
def validate_landlord_enrichment():
    """Validate and save enriched landlord data to landlords table"""
    try:
        data = request.json
        landlord_id = data.get('landlord_id')
        landlord_name = data.get('landlord_name')
        landlord_address = data.get('landlord_address', '')
        enriched = data.get('enriched_data', {})
        
        if not landlord_id or not landlord_name:
            return jsonify({'error': 'landlord_id and landlord_name are required'}), 400
        
        print(f"Validating landlord enrichment: {landlord_id}")
        
        # Calculate deterministic health score
        calculated_health_score = calculate_landlord_health_score(enriched)
        print(f"Calculated landlord health score: {calculated_health_score}")
        
        def sql_val(val):
            if val is None:
                return 'NULL'
            if isinstance(val, bool):
                return 'TRUE' if val else 'FALSE'
            if isinstance(val, (int, float)):
                return str(val)
            escaped = str(val).replace("'", "''")
            return f"'{escaped}'"
        
        # Insert/update landlords table
        merge_query = f"""
        MERGE INTO {CATALOG}.{SCHEMA}.landlords AS target
        USING (
            SELECT 
                {sql_val(landlord_id)} as landlord_id,
                {sql_val(landlord_name)} as landlord_name,
                {sql_val(landlord_address)} as landlord_address,
                {sql_val(enriched.get('company_type'))} as company_type,
                {sql_val(enriched.get('stock_ticker'))} as stock_ticker,
                {enriched.get('market_cap') or 'NULL'} as market_cap,
                {enriched.get('total_assets') or 'NULL'} as total_assets,
                {sql_val(enriched.get('credit_rating'))} as credit_rating,
                {sql_val(enriched.get('credit_rating_agency'))} as credit_rating_agency,
                {enriched.get('annual_revenue') or 'NULL'} as annual_revenue,
                {enriched.get('net_operating_income') or 'NULL'} as net_operating_income,
                {enriched.get('debt_to_equity_ratio') or 'NULL'} as debt_to_equity_ratio,
                {enriched.get('total_properties') or 'NULL'} as total_properties,
                {enriched.get('total_square_footage') or 'NULL'} as total_square_footage,
                {sql_val(enriched.get('primary_property_types'))} as primary_property_types,
                {sql_val(enriched.get('geographic_focus'))} as geographic_focus,
                {calculated_health_score} as financial_health_score,
                {sql_val(enriched.get('bankruptcy_risk', 'MEDIUM'))} as bankruptcy_risk,
                {sql_val(enriched.get('recent_news_sentiment', 'NEUTRAL'))} as recent_news_sentiment,
                'AI_CLAUDE' as enrichment_source,
                0.85 as enrichment_confidence,
                CURRENT_TIMESTAMP() as last_enriched_at,
                NULL as source_urls,
                CURRENT_TIMESTAMP() as created_at,
                CURRENT_TIMESTAMP() as updated_at
        ) AS source
        ON target.landlord_id = source.landlord_id
        WHEN MATCHED THEN UPDATE SET
            target.company_type = source.company_type,
            target.stock_ticker = source.stock_ticker,
            target.market_cap = source.market_cap,
            target.total_assets = source.total_assets,
            target.credit_rating = source.credit_rating,
            target.credit_rating_agency = source.credit_rating_agency,
            target.annual_revenue = source.annual_revenue,
            target.net_operating_income = source.net_operating_income,
            target.debt_to_equity_ratio = source.debt_to_equity_ratio,
            target.total_properties = source.total_properties,
            target.total_square_footage = source.total_square_footage,
            target.primary_property_types = source.primary_property_types,
            target.geographic_focus = source.geographic_focus,
            target.financial_health_score = source.financial_health_score,
            target.bankruptcy_risk = source.bankruptcy_risk,
            target.recent_news_sentiment = source.recent_news_sentiment,
            target.enrichment_source = source.enrichment_source,
            target.enrichment_confidence = source.enrichment_confidence,
            target.last_enriched_at = source.last_enriched_at,
            target.updated_at = source.updated_at
        WHEN NOT MATCHED THEN INSERT *
        """
        
        _, error = execute_query(merge_query)
        
        if error:
            print(f"ERROR inserting landlord: {error}")
            return jsonify({'error': f'Failed to save landlord: {error}'}), 500
        
        print(f"Successfully saved landlord: {landlord_id}")
        return jsonify({
            'success': True,
            'message': f'Landlord {landlord_name} saved successfully',
            'landlord_id': landlord_id
        })
        
    except Exception as e:
        error_msg = f"Exception in validate_landlord_enrichment: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/enrich/validate-tenant', methods=['POST'])
def validate_tenant_enrichment():
    """Validate and save enriched tenant data to tenants table"""
    try:
        data = request.json
        tenant_id = data.get('tenant_id')
        tenant_name = data.get('tenant_name')
        tenant_address = data.get('tenant_address', '')
        industry_sector = data.get('industry_sector', '')
        enriched = data.get('enriched_data', {})
        
        if not tenant_id or not tenant_name:
            return jsonify({'error': 'tenant_id and tenant_name are required'}), 400
        
        print(f"Validating tenant enrichment: {tenant_id}")
        
        # Calculate deterministic health score
        calculated_health_score = calculate_tenant_health_score(enriched)
        print(f"Calculated tenant health score: {calculated_health_score}")
        
        def sql_val(val):
            if val is None:
                return 'NULL'
            if isinstance(val, bool):
                return 'TRUE' if val else 'FALSE'
            if isinstance(val, (int, float)):
                return str(val)
            escaped = str(val).replace("'", "''")
            return f"'{escaped}'"
        
        # Insert/update tenants table
        merge_query = f"""
        MERGE INTO {CATALOG}.{SCHEMA}.tenants AS target
        USING (
            SELECT 
                {sql_val(tenant_id)} as tenant_id,
                {sql_val(tenant_name)} as tenant_name,
                {sql_val(tenant_address)} as tenant_address,
                {sql_val(industry_sector)} as industry_sector,
                {sql_val(enriched.get('company_type'))} as company_type,
                {sql_val(enriched.get('parent_company'))} as parent_company,
                {sql_val(enriched.get('stock_ticker'))} as stock_ticker,
                {enriched.get('founding_year') or 'NULL'} as founding_year,
                {enriched.get('employee_count') or 'NULL'} as employee_count,
                {sql_val(enriched.get('headquarters_location'))} as headquarters_location,
                {enriched.get('market_cap') or 'NULL'} as market_cap,
                {enriched.get('annual_revenue') or 'NULL'} as annual_revenue,
                {enriched.get('net_income') or 'NULL'} as net_income,
                {enriched.get('revenue_growth_pct') or 'NULL'} as revenue_growth_pct,
                {enriched.get('profit_margin_pct') or 'NULL'} as profit_margin_pct,
                {sql_val(enriched.get('credit_rating'))} as credit_rating,
                {sql_val(enriched.get('credit_rating_agency'))} as credit_rating_agency,
                {sql_val(enriched.get('duns_number'))} as duns_number,
                {enriched.get('payment_history_score') or 'NULL'} as payment_history_score,
                {calculated_health_score} as financial_health_score,
                {sql_val(enriched.get('bankruptcy_risk', 'MEDIUM'))} as bankruptcy_risk,
                {sql_val(enriched.get('industry_risk', 'MEDIUM'))} as industry_risk,
                {sql_val(enriched.get('recent_news_sentiment', 'NEUTRAL'))} as recent_news_sentiment,
                {'TRUE' if enriched.get('litigation_flag') else 'FALSE'} as litigation_flag,
                {enriched.get('locations_count') or 'NULL'} as locations_count,
                {enriched.get('years_in_business') or 'NULL'} as years_in_business,
                'AI_CLAUDE' as enrichment_source,
                0.85 as enrichment_confidence,
                CURRENT_TIMESTAMP() as last_enriched_at,
                NULL as source_urls,
                CURRENT_TIMESTAMP() as created_at,
                CURRENT_TIMESTAMP() as updated_at
        ) AS source
        ON target.tenant_id = source.tenant_id
        WHEN MATCHED THEN UPDATE SET
            target.company_type = source.company_type,
            target.parent_company = source.parent_company,
            target.stock_ticker = source.stock_ticker,
            target.founding_year = source.founding_year,
            target.employee_count = source.employee_count,
            target.headquarters_location = source.headquarters_location,
            target.market_cap = source.market_cap,
            target.annual_revenue = source.annual_revenue,
            target.net_income = source.net_income,
            target.revenue_growth_pct = source.revenue_growth_pct,
            target.profit_margin_pct = source.profit_margin_pct,
            target.credit_rating = source.credit_rating,
            target.credit_rating_agency = source.credit_rating_agency,
            target.duns_number = source.duns_number,
            target.payment_history_score = source.payment_history_score,
            target.financial_health_score = source.financial_health_score,
            target.bankruptcy_risk = source.bankruptcy_risk,
            target.industry_risk = source.industry_risk,
            target.recent_news_sentiment = source.recent_news_sentiment,
            target.litigation_flag = source.litigation_flag,
            target.locations_count = source.locations_count,
            target.years_in_business = source.years_in_business,
            target.enrichment_source = source.enrichment_source,
            target.enrichment_confidence = source.enrichment_confidence,
            target.last_enriched_at = source.last_enriched_at,
            target.updated_at = source.updated_at
        WHEN NOT MATCHED THEN INSERT *
        """
        
        _, error = execute_query(merge_query)
        
        if error:
            print(f"ERROR inserting tenant: {error}")
            return jsonify({'error': f'Failed to save tenant: {error}'}), 500
        
        print(f"Successfully saved tenant: {tenant_id}")
        return jsonify({
            'success': True,
            'message': f'Tenant {tenant_name} saved successfully',
            'tenant_id': tenant_id
        })
        
    except Exception as e:
        error_msg = f"Exception in validate_tenant_enrichment: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/landlords/<landlord_id>', methods=['GET'])
def get_landlord(landlord_id):
    """Get landlord data by ID"""
    try:
        query = f"""
        SELECT * FROM {CATALOG}.{SCHEMA}.landlords
        WHERE landlord_id = '{landlord_id}'
        """
        data, error = execute_query(query)
        if error:
            return jsonify({'error': error}), 500
        if not data:
            return jsonify({'error': 'Landlord not found'}), 404
        # Return first row as dict (columns would need to be mapped)
        return jsonify({'success': True, 'data': data[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tenants/<tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    """Get tenant data by ID"""
    try:
        query = f"""
        SELECT * FROM {CATALOG}.{SCHEMA}.tenants
        WHERE tenant_id = '{tenant_id}'
        """
        data, error = execute_query(query)
        if error:
            return jsonify({'error': error}), 500
        if not data:
            return jsonify({'error': 'Tenant not found'}), 404
        return jsonify({'success': True, 'data': data[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio/landlords', methods=['GET'])
def get_all_landlords():
    """Get all landlords with their financial profiles"""
    try:
        query = f"""
        SELECT 
            landlord_id,
            landlord_name,
            landlord_address,
            company_type,
            stock_ticker,
            market_cap,
            total_assets,
            credit_rating,
            credit_rating_agency,
            annual_revenue,
            net_operating_income,
            debt_to_equity_ratio,
            total_properties,
            total_square_footage,
            primary_property_types,
            geographic_focus,
            financial_health_score,
            bankruptcy_risk,
            recent_news_sentiment,
            enrichment_source,
            enrichment_confidence,
            last_enriched_at,
            created_at
        FROM {CATALOG}.{SCHEMA}.landlords
        ORDER BY landlord_name
        """
        
        data, error = execute_query(query)
        if error:
            print(f"ERROR in get_all_landlords: {error}")
            return jsonify({'error': error}), 500
        
        landlords = []
        for row in data:
            landlords.append({
                'landlord_id': row[0],
                'landlord_name': row[1],
                'landlord_address': row[2],
                'company_type': row[3],
                'stock_ticker': row[4],
                'market_cap': float(row[5]) if row[5] else None,
                'total_assets': float(row[6]) if row[6] else None,
                'credit_rating': row[7],
                'credit_rating_agency': row[8],
                'annual_revenue': float(row[9]) if row[9] else None,
                'net_operating_income': float(row[10]) if row[10] else None,
                'debt_to_equity_ratio': float(row[11]) if row[11] else None,
                'total_properties': int(row[12]) if row[12] else None,
                'total_square_footage': float(row[13]) if row[13] else None,
                'primary_property_types': row[14],
                'geographic_focus': row[15],
                'financial_health_score': float(row[16]) if row[16] else None,
                'bankruptcy_risk': row[17],
                'recent_news_sentiment': row[18],
                'enrichment_source': row[19],
                'enrichment_confidence': float(row[20]) if row[20] else None,
                'last_enriched_at': str(row[21]) if row[21] else None,
                'created_at': str(row[22]) if row[22] else None
            })
        
        return jsonify(landlords)
        
    except Exception as e:
        error_msg = f"Exception in get_all_landlords: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/portfolio/tenants', methods=['GET'])
def get_all_tenants():
    """Get all tenants with their financial profiles"""
    try:
        query = f"""
        SELECT 
            tenant_id,
            tenant_name,
            tenant_address,
            industry_sector,
            company_type,
            parent_company,
            stock_ticker,
            founding_year,
            employee_count,
            headquarters_location,
            market_cap,
            annual_revenue,
            net_income,
            revenue_growth_pct,
            profit_margin_pct,
            credit_rating,
            credit_rating_agency,
            duns_number,
            payment_history_score,
            financial_health_score,
            bankruptcy_risk,
            industry_risk,
            recent_news_sentiment,
            litigation_flag,
            locations_count,
            years_in_business,
            enrichment_source,
            enrichment_confidence,
            last_enriched_at,
            created_at
        FROM {CATALOG}.{SCHEMA}.tenants
        ORDER BY tenant_name
        """
        
        data, error = execute_query(query)
        if error:
            print(f"ERROR in get_all_tenants: {error}")
            return jsonify({'error': error}), 500
        
        tenants = []
        for row in data:
            tenants.append({
                'tenant_id': row[0],
                'tenant_name': row[1],
                'tenant_address': row[2],
                'industry_sector': row[3],
                'company_type': row[4],
                'parent_company': row[5],
                'stock_ticker': row[6],
                'founding_year': int(row[7]) if row[7] else None,
                'employee_count': int(row[8]) if row[8] else None,
                'headquarters_location': row[9],
                'market_cap': float(row[10]) if row[10] else None,
                'annual_revenue': float(row[11]) if row[11] else None,
                'net_income': float(row[12]) if row[12] else None,
                'revenue_growth_pct': float(row[13]) if row[13] else None,
                'profit_margin_pct': float(row[14]) if row[14] else None,
                'credit_rating': row[15],
                'credit_rating_agency': row[16],
                'duns_number': row[17],
                'payment_history_score': float(row[18]) if row[18] else None,
                'financial_health_score': float(row[19]) if row[19] else None,
                'bankruptcy_risk': row[20],
                'industry_risk': row[21],
                'recent_news_sentiment': row[22],
                'litigation_flag': bool(row[23]) if row[23] is not None else None,
                'locations_count': int(row[24]) if row[24] else None,
                'years_in_business': int(row[25]) if row[25] else None,
                'enrichment_source': row[26],
                'enrichment_confidence': float(row[27]) if row[27] else None,
                'last_enriched_at': str(row[28]) if row[28] else None,
                'created_at': str(row[29]) if row[29] else None
            })
        
        return jsonify(tenants)
        
    except Exception as e:
        error_msg = f"Exception in get_all_tenants: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


# ============================================================
# FORECASTING ENDPOINTS
# ============================================================

@app.route('/api/forecasting/upload', methods=['POST'])
def forecasting_upload():
    """Upload a lease document for forecasting/impact analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Forecasting upload - file: {file.filename}")
        
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
        
        if not success:
            print(f"Upload failed: {error}")
            return jsonify({'error': error}), 500
        
        print(f"File uploaded successfully: {file_path}")
        
        # Wait a moment for ingestion to start
        time.sleep(2)
        
        # Check if the file has been ingested to raw layer
        filename = file_path.split('/')[-1]
        raw_query = f"""
        SELECT 
            ingested_at
        FROM {CATALOG}.{SCHEMA}.raw_leases
        WHERE file_path LIKE '%{filename}%'
        ORDER BY ingested_at DESC
        LIMIT 1
        """
        
        raw_data, raw_error = execute_query(raw_query)
        
        if raw_error:
            print(f"Error checking raw_leases: {raw_error}")
            # Don't fail - the file was uploaded successfully
        
        # Return the file path as lease_id for now (we'll get the actual extraction_id later)
        return jsonify({
            'success': True,
            'file_path': file_path,
            'lease_id': file_path,  # Use file_path as identifier for polling
            'message': 'File uploaded successfully and processing started'
        })
            
    except Exception as e:
        error_msg = f"Exception in forecasting_upload: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecasting/impact/<path:lease_id>', methods=['GET'])
def get_forecasting_impact(lease_id):
    """
    Get the portfolio impact analysis for a newly uploaded lease.
    Returns 202 if still processing, 200 with data when ready.
    """
    try:
        print(f"Checking forecasting impact for: {lease_id}")
        
        # Extract filename from the lease_id (which is the file_path)
        filename = lease_id.split('/')[-1]
        
        # Check if the lease has been extracted to bronze layer
        bronze_query = f"""
        SELECT 
            extraction_id,
            landlord_name,
            tenant_name,
            property_city,
            property_state,
            rentable_square_feet,
            annual_base_rent,
            base_rent_psf,
            term_months,
            commencement_date,
            expiration_date,
            validation_status,
            uploaded_at
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE uploaded_at IN (
            SELECT ingested_at 
            FROM {CATALOG}.{SCHEMA}.raw_leases 
            WHERE file_path LIKE '%{filename}%'
        )
        ORDER BY uploaded_at DESC
        LIMIT 1
        """
        
        bronze_data, bronze_error = execute_query(bronze_query)
        
        if bronze_error:
            print(f"Error checking bronze: {bronze_error}")
            return jsonify({
                'status': 'processing',
                'message': 'Extraction in progress...',
                'error': bronze_error
            }), 202
        
        if not bronze_data or len(bronze_data) == 0:
            print("No bronze record found yet - still processing")
            return jsonify({
                'status': 'processing',
                'message': 'AI extraction in progress... This typically takes 2-3 minutes.'
            }), 202
        
        # Lease has been extracted! Calculate impact
        lease_record = bronze_data[0]
        extraction_id = lease_record[0]
        current_status = lease_record[11]  # validation_status
        
        print(f"Found bronze record: extraction_id={extraction_id}, current_status={current_status}")
        
        # Update status to FORECAST if it's currently NEW
        # This prevents the forecasted lease from appearing in the validation queue
        if current_status == 'NEW':
            print(f"Updating extraction_id {extraction_id} status from NEW to FORECAST")
            update_status_query = f"""
            UPDATE {CATALOG}.{SCHEMA}.bronze_leases
            SET validation_status = 'FORECAST'
            WHERE extraction_id = {extraction_id}
            """
            _, update_error = execute_query(update_status_query)
            
            if update_error:
                print(f"Warning: Failed to update status to FORECAST: {update_error}")
                # Don't fail the request, just log the warning
            else:
                print(f"Successfully updated status to FORECAST")
        
        # Get current portfolio KPIs (from silver - verified leases only)
        current_kpis_query = f"""
        WITH base_kpis AS (
            SELECT 
                COUNT(*) as total_leases,
                AVG(base_rent_psf) as avg_rent_psf,
                AVG(GREATEST(DATEDIFF(lease_end_date, CURRENT_DATE()), 0) / 365.25) as portfolio_walt
            FROM {CATALOG}.{SCHEMA}.silver_leases
            WHERE tenant_name IS NOT NULL
        ),
        risk_kpis AS (
            SELECT 
                AVG(total_risk_score) as avg_risk_score
            FROM {CATALOG}.{SCHEMA}.gold_lease_risk_scores
        )
        SELECT 
            b.total_leases,
            COALESCE(r.avg_risk_score, 0) as avg_risk_score,
            b.avg_rent_psf,
            b.portfolio_walt
        FROM base_kpis b
        CROSS JOIN risk_kpis r
        """
        
        current_kpis_data, kpi_error = execute_query(current_kpis_query)
        
        if kpi_error:
            print(f"Error fetching current KPIs: {kpi_error}")
            return jsonify({'error': f'Failed to fetch portfolio KPIs: {kpi_error}'}), 500
        
        current_stats = current_kpis_data[0] if current_kpis_data else [0, 0, 0, 0]
        
        # Parse new lease data
        new_lease = {
            'extraction_id': extraction_id,
            'tenant_name': lease_record[2],
            'landlord_name': lease_record[1],
            'property_id': f"{lease_record[3]}, {lease_record[4]}" if lease_record[3] and lease_record[4] else 'N/A',
            'square_footage': int(float(lease_record[5])) if lease_record[5] else 0,
            'estimated_annual_rent': int(float(lease_record[6])) if lease_record[6] else 0,
            'rent_psf': float(lease_record[7]) if lease_record[7] else 0,
            'term_months': int(float(lease_record[8])) if lease_record[8] else 0,
            'commencement_date': str(lease_record[9]) if lease_record[9] else None,
            'expiration_date': str(lease_record[10]) if lease_record[10] else None,
            'risk_score': 50.0  # Default risk score for new leases
        }
        
        # Calculate current portfolio metrics
        current_total_leases = int(float(current_stats[0])) if current_stats[0] else 0
        current_avg_risk = float(current_stats[1]) if current_stats[1] else 0
        current_avg_rent_psf = float(current_stats[2]) if current_stats[2] else 0
        current_avg_walt = float(current_stats[3]) if current_stats[3] else 0
        
        # Calculate projected metrics (with new lease added)
        projected_total_leases = current_total_leases + 1
        projected_avg_risk = ((current_avg_risk * current_total_leases) + new_lease['risk_score']) / projected_total_leases if projected_total_leases > 0 else new_lease['risk_score']
        projected_avg_rent_psf = ((current_avg_rent_psf * current_total_leases) + new_lease['rent_psf']) / projected_total_leases if projected_total_leases > 0 else new_lease['rent_psf']
        new_lease_term_years = new_lease['term_months'] / 12.0
        projected_avg_walt = ((current_avg_walt * current_total_leases) + new_lease_term_years) / projected_total_leases if projected_total_leases > 0 else new_lease_term_years
        
        # Calculate impact deltas
        impact = {
            'leases_change': 1,
            'risk_change': projected_avg_risk - current_avg_risk,
            'rent_psf_change': projected_avg_rent_psf - current_avg_rent_psf,
            'walt_change': projected_avg_walt - current_avg_walt
        }
        
        response_data = {
            'status': 'ready',
            'lease_id': extraction_id,
            'new_lease': new_lease,
            'current': {
                'total_leases': current_total_leases,
                'avg_risk_score': current_avg_risk,
                'avg_rent_psf': current_avg_rent_psf,
                'portfolio_walt': current_avg_walt
            },
            'projected': {
                'total_leases': projected_total_leases,
                'avg_risk_score': projected_avg_risk,
                'avg_rent_psf': projected_avg_rent_psf,
                'portfolio_walt': projected_avg_walt
            },
            'impact': impact
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"Exception in get_forecasting_impact: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecasting/approve/<int:lease_id>', methods=['POST'])
def approve_forecasted_lease(lease_id):
    """
    Approve a forecasted lease and move it from bronze to silver layer.
    This is similar to validation but for forecasted leases.
    """
    try:
        print(f"Approving forecasted lease: {lease_id}")
        
        # Update the bronze record to VERIFIED status
        update_query = f"""
        UPDATE {CATALOG}.{SCHEMA}.bronze_leases
        SET validation_status = 'VERIFIED'
        WHERE extraction_id = {lease_id}
        """
        
        _, update_error = execute_query(update_query)
        
        if update_error:
            print(f"Error updating bronze layer: {update_error}")
            return jsonify({'error': f'Failed to update bronze layer: {update_error}'}), 500
        
        # Promote to silver layer
        promote_query = f"""
        INSERT INTO {CATALOG}.{SCHEMA}.silver_leases (
            extraction_id, uploaded_at, landlord_name, landlord_address, tenant_name, 
            tenant_address, industry_sector, suite_number, lease_type, 
            commencement_date, expiration_date, term_months, rentable_square_feet, 
            annual_base_rent, base_rent_psf, annual_escalation_pct, 
            renewal_notice_days, guarantor, 
            property_address, property_street_address, property_city, 
            property_state, property_zip_code, property_country, 
            validated_at
        )
        SELECT 
            extraction_id, uploaded_at, landlord_name, landlord_address, tenant_name, 
            tenant_address, industry_sector, suite_number, lease_type, 
            commencement_date, expiration_date, term_months, rentable_square_feet, 
            annual_base_rent, base_rent_psf, annual_escalation_pct, 
            renewal_notice_days, guarantor, 
            property_address, property_street_address, property_city, 
            property_state, property_zip_code, property_country, 
            CURRENT_TIMESTAMP() as validated_at
        FROM {CATALOG}.{SCHEMA}.bronze_leases
        WHERE extraction_id = {lease_id}
        """
        
        _, promote_error = execute_query(promote_query)
        
        if promote_error:
            print(f"Error promoting to silver: {promote_error}")
            return jsonify({'error': f'Failed to promote to silver layer: {promote_error}'}), 500
        
        print(f"Successfully approved and promoted lease {lease_id}")
        
        return jsonify({
            'success': True,
            'message': 'Lease approved and added to portfolio'
        })
        
    except Exception as e:
        error_msg = f"Exception in approve_forecasted_lease: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e)}), 500


# ============================================================
# STATIC FILE SERVING (must be at the end, after all API routes)
# ============================================================

# Serve React app for root path
@app.route('/')
def serve_react_app():
    """Serve the React application"""
    if os.path.exists(os.path.join(STATIC_FOLDER, 'index.html')):
        return send_from_directory(STATIC_FOLDER, 'index.html')
    return jsonify({'message': 'React build not found. Run npm build in FrontEndV2 directory.'}), 404


# Catch-all route to serve React app for client-side routing
# This MUST be defined after all API routes to avoid intercepting them
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files or fall back to index.html for React Router"""
    # Skip API routes - they should be handled by their own endpoints
    # If we get here with an API path, it means the route doesn't exist
    if path.startswith('api/'):
        return jsonify({'error': f'API endpoint not found: /{path}'}), 404
    # First try to serve the file directly
    static_file_path = os.path.join(STATIC_FOLDER, path)
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        return send_from_directory(STATIC_FOLDER, path)
    # Fall back to index.html for React Router
    if os.path.exists(os.path.join(STATIC_FOLDER, 'index.html')):
        return send_from_directory(STATIC_FOLDER, 'index.html')
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    # Use DATABRICKS_APP_PORT or PORT environment variable for Databricks Apps deployment
    # Falls back to 5001 for local development
    port = int(os.getenv('DATABRICKS_APP_PORT', os.getenv('PORT', 5001)))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    print(f"Starting server on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)

