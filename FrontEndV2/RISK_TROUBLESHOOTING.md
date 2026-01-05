# Risk Assessment Troubleshooting Guide

## Error: "Error Loading Risk Data"

### Step 1: Check Browser Console

1. Open browser developer tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for error messages when clicking Risk Assessment tab
4. Check what the actual error says (it will now show detailed error info)

### Step 2: Verify Backend is Running

```bash
# Check if backend is running on port 5001
curl http://localhost:5001/api/health

# Should return: {"status":"healthy","message":"API is running"}
```

If backend is not running:
```bash
cd FrontEndV2/backend
python api.py
```

### Step 3: Test Risk Assessment Endpoint Directly

```bash
# Test the risk assessment endpoint
curl http://localhost:5001/api/portfolio/risk-assessment

# Should return JSON array of leases with risk scores
```

### Step 4: Verify Gold Table Exists

The risk assessment endpoint queries `gold_lease_risk_scores` view. Check if it exists in Databricks:

```sql
USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Check if view exists
SHOW VIEWS LIKE 'gold_lease_risk_scores';

-- If it exists, test the query
SELECT COUNT(*) FROM gold_lease_risk_scores;

-- If count is 0, you need data in silver_leases first
SELECT COUNT(*) FROM silver_leases;
```

### Step 5: Create Gold Table if Missing

If the view doesn't exist, run:

```sql
-- Execute CreateGoldTable.sql in Databricks
-- The file is in: DatabricksResources/CreateGoldTable.sql
```

### Step 6: Check for Data

The risk assessment needs data in silver_leases:

```sql
-- Check silver_leases
SELECT COUNT(*) FROM fins_team_3.lease_management.silver_leases;

-- If 0, you need to promote from bronze:
-- Run PromoteBronzeToSilver.sql

-- Check bronze_leases
SELECT COUNT(*) FROM fins_team_3.lease_management.bronze_leases;

-- If 0, upload some lease PDFs through the Upload interface
```

### Step 7: Check Databricks Credentials

Verify your `.env` file in `FrontEndV2/backend/`:

```bash
# Should have these variables:
DATABRICKS_HOST=your-workspace-url
DATABRICKS_TOKEN=your-token
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
DATABRICKS_CATALOG=fins_team_3
DATABRICKS_SCHEMA=lease_management
```

### Step 8: Check Python Dependencies

```bash
cd FrontEndV2/backend
pip list | grep databricks

# Should show:
# databricks-sdk
```

If not installed:
```bash
pip install databricks-sdk python-dotenv flask flask-cors
```

### Step 9: Check Frontend Dependencies

```bash
cd FrontEndV2
npm list recharts

# Should show recharts@2.10.3 or similar
```

If not installed:
```bash
npm install recharts
```

## Common Error Messages and Solutions

### "Failed to connect to backend API"
- Backend server is not running
- Backend is not on port 5001
- CORS issue (check backend logs)
- **Solution**: Start backend with `python api.py`

### "Failed to fetch risk data (500)"
- Backend error (check backend console for stack trace)
- Databricks connection issue
- SQL query error
- **Solution**: Check backend logs for detailed error

### "Failed to fetch risk data (404)"
- Endpoint not found
- Backend API version mismatch
- **Solution**: Verify `/api/portfolio/risk-assessment` endpoint exists in api.py

### Empty visualization (no error)
- Data fetched but no leases match criteria
- All risk scores are 0
- **Solution**: Check filter status, verify data in gold table

## Debug Checklist

- [ ] Backend running on port 5001
- [ ] `/api/health` endpoint responds
- [ ] `/api/portfolio/risk-assessment` endpoint exists
- [ ] Databricks credentials in `.env` are correct
- [ ] `gold_lease_risk_scores` view exists
- [ ] Silver leases table has data
- [ ] Frontend `recharts` dependency installed
- [ ] Browser console shows detailed error logs
- [ ] No CORS errors in browser console

## Quick Test Commands

```bash
# Test full stack
# Terminal 1 - Backend
cd FrontEndV2/backend
python api.py

# Terminal 2 - Frontend  
cd FrontEndV2
npm start

# Terminal 3 - Test endpoints
curl http://localhost:5001/api/health
curl http://localhost:5001/api/portfolio/risk-assessment | jq

# In Databricks SQL Editor
SELECT COUNT(*) FROM fins_team_3.lease_management.gold_lease_risk_scores;
```

## Still Having Issues?

1. Check backend terminal for error logs
2. Check browser console for JavaScript errors
3. Verify Databricks warehouse is running
4. Try restarting both backend and frontend
5. Clear browser cache and refresh

The component now logs detailed error messages to the console, so check there first!

