# Backend API

Flask REST API connecting React frontend to Databricks Unity Catalog.

## Quick Setup

### Option 1: Interactive Setup (Recommended)

```bash
cd backend
python setup.py
```

Prompts for Databricks credentials and creates `.env` file.

### Option 2: Manual Setup

Create `backend/.env`:

```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-access-token
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
DATABRICKS_CATALOG=fins_team_3
DATABRICKS_SCHEMA=lease_management
DATABRICKS_VOLUME=raw_lease_docs
```

## Installation

```bash
pip install -r requirements.txt
python setup.py    # Creates .env
python api.py      # Starts server on port 5001
```

## Test Connection

```bash
python test_connection.py
```

This verifies:
- Environment variables are set
- Databricks connection works
- SQL Warehouse is accessible
- bronze_leases table exists and has data

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/portfolio/kpis` | GET | Portfolio metrics |
| `/api/portfolio/leases` | GET | All leases |
| `/api/portfolio/recent` | GET | Recent extractions |
| `/api/portfolio/market-summary` | GET | Market aggregations |
| `/api/upload` | POST | Upload document |
| `/api/check-processing/<path>` | GET | Processing status |
| `/api/validate-record` | POST | Validate & promote data |
| `/api/chat/query` | POST | Natural language queries |

## Troubleshooting

**Connection Errors:**
- Run `python test_connection.py` for diagnostics
- Ensure SQL Warehouse is running (not stopped)
- Verify token hasn't expired
- Check catalog/schema names match your Databricks setup

**No Data:**
- Verify `bronze_leases` table exists
- Check table has data: `SELECT * FROM catalog.schema.bronze_leases LIMIT 10`
- Ensure token has read permissions

**Port Conflicts:**
- Change port in `api.py`: `app.run(debug=True, port=YOUR_PORT)`
- Update frontend API calls to match new port

## Dependencies

- **Flask** - Web framework
- **Flask-CORS** - Enable CORS for React
- **Databricks SDK** - Database client
- **python-dotenv** - Environment config

All listed in `requirements.txt`.
