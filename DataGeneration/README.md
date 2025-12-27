# Synthetic Lease Data Generator

## Overview

This tool generates realistic synthetic lease data to populate your `bronze_leases` table for demonstration and testing purposes. The data is designed to showcase the dashboard at scale with meaningful visualizations.

## Features

✨ **Realistic Data Generation:**
- Industry-appropriate company names
- Market-based rent pricing (12 major US markets)
- Realistic lease terms (3, 5, 7, 10 years)
- Historical and future lease dates
- Real estate company names for landlords
- Proper lease types (NNN, Modified Gross, etc.)

📊 **Dashboard Optimized:**
- Diverse industries for pie chart visualization
- Multiple markets for geographic analysis
- Varied expiration dates for timeline charts
- Mix of rent levels for distribution analysis
- Realistic WALT calculations
- Mix of validation statuses

## Prerequisites

### Required Dependencies

```bash
pip install faker databricks-sdk python-dotenv
```

### Environment Setup

Ensure your `.env` file in the `FrontEnd/` directory contains:

```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token
```

### Databricks Configuration

1. **SQL Warehouse must be running**
2. **Update the WAREHOUSE_ID** in `generate_synthetic_leases.py` (line 22)
   ```python
   WAREHOUSE_ID = "your-warehouse-id"  # Replace with your ID
   ```
3. **bronze_leases table must exist** (created via `DatabricksResources/CreateBronzeTable.sql`)

## Installation

1. Navigate to the DataGeneration directory:
   ```bash
   cd /Users/ray.rosalez/Desktop/Buildathon/fins-lease-extraction-temp/DataGeneration
   ```

2. Install required packages:
   ```bash
   pip install faker databricks-sdk python-dotenv
   ```

3. Copy your `.env` file (or ensure it exists in parent directory):
   ```bash
   # If .env is in FrontEnd directory, it will be found automatically
   # Or create one here with the same credentials
   ```

## Usage

### Basic Execution

```bash
python generate_synthetic_leases.py
```

You'll be prompted:
```
How many synthetic leases to generate? (recommended 50-200):
```

**Recommendations:**
- **Demo/Testing:** 50-100 leases
- **Full Portfolio Simulation:** 150-200 leases
- **Small Dataset:** 20-50 leases

### Example Session

```bash
$ python generate_synthetic_leases.py

============================================================
Synthetic Lease Data Generator
============================================================

How many synthetic leases to generate? (recommended 50-200): 100

Generating 100 synthetic leases...

Connecting to Databricks...
✅ Connected successfully

Generating 100 lease records...
  Generated 20/100...
  Generated 40/100...
  Generated 60/100...
  Generated 80/100...
  Generated 100/100...
✅ Generated 100 lease records

Inserting leases into fins_team_3.lease_management.bronze_leases (batch size: 10)...

  Batch 1/10 (10 leases)... ✅
  Batch 2/10 (10 leases)... ✅
  Batch 3/10 (10 leases)... ✅
  ...
  Batch 10/10 (10 leases)... ✅

============================================================
Generation Complete!
============================================================
✅ Successfully inserted: 100 leases

Summary Statistics:
  - Industries: 12
  - Markets: 12
  - Landlords: 15
  - Date range: Last 8 years to +10 years

Next steps:
  1. Refresh your Streamlit dashboard
  2. Verify data appears in visualizations
  3. Test filters and exports
```

## Generated Data Structure

### Industries (12 total)
- Technology
- Healthcare
- Finance
- Retail
- Manufacturing
- Professional Services
- Restaurant
- Fitness
- Education
- Legal Services
- Marketing
- Consulting

### Markets (12 major US cities)
Each with realistic rent ranges:

| Market | Rent PSF Range | Typical Square Footage |
|--------|----------------|------------------------|
| New York | $60-$100 | 1,500 - 30,000 |
| San Francisco | $55-$95 | 2,000 - 25,000 |
| Boston | $45-$75 | 2,000 - 20,000 |
| Seattle | $40-$70 | 2,500 - 28,000 |
| Los Angeles | $38-$65 | 2,000 - 30,000 |
| Austin | $35-$55 | 3,000 - 35,000 |
| Miami | $35-$60 | 2,000 - 22,000 |
| Chicago | $32-$52 | 2,500 - 25,000 |
| Denver | $30-$50 | 3,000 - 26,000 |
| Dallas | $28-$45 | 3,500 - 35,000 |
| Atlanta | $25-$42 | 3,000 - 30,000 |
| Phoenix | $24-$40 | 3,500 - 32,000 |

### Landlords
15 realistic real estate company names including:
- Blackstone Property Partners
- Brookfield Asset Management
- Prologis Properties
- Boston Properties
- And more...

### Tenant Companies
Generated using Faker library with industry-specific naming:
- Tech companies: "Cloud Data Solutions Inc"
- Healthcare: "Medical Care Partners LLC"
- Finance: "Capital Investment Group"
- And more...

### Lease Terms
- **Duration:** 3, 5, 7, or 10 years
- **Start dates:** Mix of historical (past 8 years) and recent
- **Escalation:** 0%, 2%, 2.5%, 3%, 3.5%, or 4% annual
- **Types:** Triple Net (NNN), Modified Gross, Full Service, etc.

## Configuration Options

### Adjust Number of Leases
Modify the default when prompted, or edit the script:

```python
num_leases = int(input("How many synthetic leases to generate? (recommended 50-200): ") or "100")
```

Change `"100"` to your preferred default.

### Adjust Batch Size
For faster insertion (risk of timeout) or slower (more stable):

```python
batch_size = 10  # Default: 10 leases per batch
```

### Update Warehouse ID
**Important:** Update line 22 with your actual warehouse ID:

```python
WAREHOUSE_ID = "288a7ec183eea397"  # Replace with your warehouse ID
```

Find your warehouse ID in:
1. Databricks workspace → SQL → Warehouses
2. Click on your warehouse
3. Copy the ID from the URL or warehouse details

### Add More Industries/Markets

Edit the lists in the script:

```python
INDUSTRIES = [
    "Technology",
    "Healthcare",
    # Add more...
]

MARKETS = {
    "San Francisco": {"min_rent": 55, "max_rent": 95, "sqft_range": (2000, 25000)},
    # Add more cities...
}
```

## Troubleshooting

### Connection Errors

**Error:** `Failed to connect: ...`

**Solution:**
1. Check `.env` file exists with correct credentials
2. Verify DATABRICKS_HOST includes `https://`
3. Ensure token hasn't expired
4. Test connection: `databricks workspace ls /` (Databricks CLI)

### Insert Failures

**Error:** `❌ Error: Statement failed`

**Solution:**
1. Verify SQL Warehouse is running
2. Check table exists: `SHOW TABLES IN fins_team_3.lease_management;`
3. Verify table schema matches (run `CreateBronzeTable.sql` if needed)
4. Check warehouse permissions (need INSERT permission)

### Timeout Errors

**Error:** `wait_timeout exceeded`

**Solution:**
1. Reduce batch size (change `batch_size = 5`)
2. Ensure warehouse isn't overloaded
3. Try again when warehouse is less busy

### Duplicate Data

If you run the script multiple times, you'll get duplicate records. To clear and start fresh:

```sql
-- In Databricks SQL Editor
TRUNCATE TABLE fins_team_3.lease_management.bronze_leases;
```

Then re-run the generator.

## Verification

### Check Data in Databricks

```sql
-- Count records
SELECT COUNT(*) FROM fins_team_3.lease_management.bronze_leases;

-- Sample records
SELECT * FROM fins_team_3.lease_management.bronze_leases LIMIT 10;

-- Check distribution by industry
SELECT industry_sector, COUNT(*) as count
FROM fins_team_3.lease_management.bronze_leases
GROUP BY industry_sector
ORDER BY count DESC;

-- Check rent range
SELECT 
    MIN(base_rent_psf) as min_rent,
    MAX(base_rent_psf) as max_rent,
    AVG(base_rent_psf) as avg_rent
FROM fins_team_3.lease_management.bronze_leases;
```

### View in Dashboard

1. Navigate to your Streamlit app
2. Click "Refresh Data" button
3. Verify:
   - KPI cards show correct totals
   - Industry pie chart has 12 segments
   - Timeline chart shows lease expirations
   - Rent distribution histogram is populated
   - All data tables display records

## Data Characteristics

### Dashboard Optimization

The generated data is specifically designed to showcase:

1. **Portfolio Overview KPIs**
   - Wide range of tenants and properties
   - Realistic averages (rent PSF, WALT)
   - Mix of industries and markets

2. **Market Analysis Charts**
   - 12 distinct markets for comparison
   - Varied lease counts per market
   - Realistic rent ranges

3. **Timeline Visualization**
   - Leases expiring across next 10 years
   - Some already expired for context
   - Dense visualization for scale demo

4. **Rent Analysis**
   - Bell curve distribution
   - Market-appropriate ranges
   - Industry-based variations

5. **Portfolio Composition**
   - Balanced industry distribution
   - Multiple asset types
   - Diverse tenant base

### Realism Features

- **Names:** Uses Faker library for realistic companies
- **Rent Prices:** Market-based with realistic ranges
- **Square Footage:** Appropriate for each market
- **Lease Terms:** Standard commercial terms
- **Dates:** Mix of active, expiring, and expired
- **Validation:** 75% verified, 25% pending (realistic workflow)

## Advanced Usage

### Generate Multiple Datasets

For A/B testing or scenarios:

```bash
# High-risk portfolio
python generate_synthetic_leases.py  # Generate 100
# Manually set more short-term leases in code

# Stable portfolio  
python generate_synthetic_leases.py  # Generate 100
# Use default settings
```

### Export Generated Data

To save generated data before inserting:

Add to the script before insertion:

```python
import json

# Save to JSON file
with open('generated_leases.json', 'w') as f:
    json.dump(all_leases, f, indent=2, default=str)
```

### Custom Data Distributions

Modify the generation logic for specific scenarios:

```python
# Example: More expiring leases
def generate_lease_dates():
    years_back = random.randint(4, 6)  # Narrow range
    term_years = random.choice([5, 7])  # Shorter terms only
    # ... rest of function
```

## Best Practices

1. **Start Small:** Generate 20-50 leases first to verify setup
2. **Verify Schema:** Ensure table schema matches before large runs
3. **Monitor Warehouse:** Watch for performance issues
4. **Backup Data:** Export existing data before adding synthetic records
5. **Clean Slate:** Use TRUNCATE if you want fresh data only

## Performance

### Generation Speed
- **100 leases:** ~2-3 seconds to generate
- **100 leases:** ~5-10 seconds to insert (depends on warehouse)
- **200 leases:** ~5-6 seconds to generate, ~10-20 seconds to insert

### Warehouse Impact
- Minimal impact with default batch size (10)
- Optimize for larger datasets by increasing batch size
- Allow warehouse warm-up between large batches

## FAQ

**Q: Can I generate more than 200 leases?**
A: Yes, but start small to verify everything works. The dashboard handles thousands of records efficiently.

**Q: Will this overwrite existing data?**
A: No, it only INSERTS new records. Use TRUNCATE TABLE to start fresh.

**Q: Can I customize company names more?**
A: Yes! Edit the `generate_company_name()` function to use specific names or patterns.

**Q: How do I delete synthetic data?**
A: Use `TRUNCATE TABLE` or `DELETE FROM ... WHERE validation_status = 'VERIFIED'` to selectively remove.

**Q: Does it work with silver_leases table?**
A: Currently only generates for bronze_leases. You can adapt the script for silver if needed.

## Support

For issues or questions:
1. Check Databricks SQL history for error details
2. Verify all prerequisites are met
3. Test with small dataset first (20 leases)
4. Check the generated SQL statements in the script

---

**Happy Data Generating! 🎉**

*Generated data is for demonstration purposes only and does not represent real lease agreements.*

