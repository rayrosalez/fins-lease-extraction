# Data Generation Tool - Quick Start

## 📁 Files

```
DataGeneration/
├── README.md                          # Comprehensive documentation
├── requirements.txt                   # Python dependencies
├── setup.sh                          # Quick setup script (executable)
├── generate_and_promote.py           # ⭐ ALL-IN-ONE SCRIPT (RECOMMENDED)
├── generate_synthetic_leases.py      # Bronze-only generator
├── promote_to_silver.py              # Bronze → Silver promotion
└── verify_data.py                    # Data verification tool
```

## 🚀 Quick Start (Recommended)

### ⚡ Fastest Way - Use All-in-One Script

This generates data AND promotes it to silver so it appears in the frontend immediately:

```bash
cd DataGeneration
python3 generate_and_promote.py 100
```

That's it! Your data will now appear in the frontend application.

### Option 1: Automated Setup with Script

```bash
cd DataGeneration
./setup.sh
```

Follow the prompts to install dependencies and run the generator.

### Option 2: Manual Setup

```bash
cd DataGeneration
pip install -r requirements.txt
python3 generate_and_promote.py 100
```

## 📊 What Gets Generated

### Data Volume
- **Recommended:** 50-200 leases
- **Processing time:** ~10-20 seconds for 100 leases
- **Batch insertion:** 10 leases per batch (configurable)

### Data Characteristics

**12 Industries:**
- Technology, Healthcare, Finance, Retail, Manufacturing
- Professional Services, Restaurant, Fitness, Education
- Legal Services, Marketing, Consulting

**12 Markets:**
- San Francisco, New York, Boston, Seattle, Los Angeles
- Austin, Miami, Chicago, Denver, Dallas, Atlanta, Phoenix

**15 Landlord Companies:**
- Blackstone, Brookfield, Prologis, Boston Properties, etc.

**Realistic Attributes:**
- Market-based rent pricing ($24-$100 PSF)
- Square footage: 1,500 - 35,000 sq ft
- Lease terms: 3, 5, 7, or 10 years
- Start dates: Mix of last 8 years
- Escalation: 0-4% annual
- Lease types: NNN, Modified Gross, Full Service, etc.

## 🎯 Dashboard Optimization

The generated data perfectly complements your dashboards:

✅ **Portfolio Overview KPIs**
- Diverse tenant and property counts
- Realistic rent averages
- Meaningful WALT calculations

✅ **Market Analysis**
- 12 distinct markets for comparison
- Varied lease distributions
- Geographic diversity

✅ **Timeline Visualization**
- Leases across 10-year span
- Mix of active and expiring
- Dense timeline for scale demo

✅ **Rent Analysis**
- Bell curve distribution
- Industry-based variations
- Market-appropriate ranges

✅ **Portfolio Composition**
- Balanced industry split
- Multiple asset types
- Diverse tenant base

## 🔧 Configuration

### Before Running

**Update in `generate_synthetic_leases.py`:**
```python
WAREHOUSE_ID = "288a7ec183eea397"  # Line 22 - Use your warehouse ID
```

**Ensure `.env` file exists** (in FrontEnd directory):
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token
```

## 📋 Complete Execution Steps

### Using All-in-One Script (Recommended)

1. **Install dependencies:**
   ```bash
   pip install faker databricks-sdk python-dotenv
   ```

2. **Ensure `.env` file exists** with Databricks credentials

3. **Run the complete pipeline:**
   ```bash
   python3 generate_and_promote.py 100
   ```

4. **Open your frontend** at http://localhost:3000 - data will be there!

### Using Manual Two-Step Process

If you prefer more control:

1. **Generate and insert to bronze:**
   ```bash
   python3 generate_synthetic_leases.py
   ```

2. **Promote to silver:**
   ```bash
   python3 promote_to_silver.py
   ```

3. **Refresh dashboard** and view results!

## 🔄 Data Flow

```
generate_and_promote.py
   ↓
[Bronze Table] → VERIFIED records → [Silver Table] → Frontend App
```

**Important:** The frontend reads from `silver_leases` table. Data must be promoted from bronze to silver to appear in the UI.

## ✅ Verification

### Automated Verification
```bash
python verify_data.py
```

Shows:
- Total lease count
- Industry distribution
- Landlord count
- Date ranges
- Rent statistics
- Validation status
- Upcoming expirations

### Manual Verification (Databricks SQL)
```sql
-- Check total count
SELECT COUNT(*) FROM fins_team_3.lease_management.bronze_leases;

-- View sample
SELECT * FROM fins_team_3.lease_management.bronze_leases LIMIT 10;

-- Industry breakdown
SELECT industry_sector, COUNT(*) 
FROM fins_team_3.lease_management.bronze_leases 
GROUP BY industry_sector;
```

## 🎨 Dashboard Testing

After generation:

1. **Navigate to Streamlit app**
2. **Click "Refresh Data"** button (top right)
3. **Verify all sections populate:**
   - ✅ KPI cards show totals
   - ✅ Industry pie chart (12 segments)
   - ✅ Market analysis charts
   - ✅ Timeline visualization
   - ✅ Rent distribution histogram
   - ✅ All data tables

## 🔄 Re-running

### Add More Data
Just run again - new leases will be added.

### Start Fresh
```sql
-- Clear all data
TRUNCATE TABLE fins_team_3.lease_management.bronze_leases;
```
Then run generator again.

## 💡 Tips

1. **Start small** - Generate 20 leases first to test
2. **Check warehouse** - Ensure it's running before generation
3. **Monitor progress** - Script shows real-time status
4. **Verify immediately** - Run verify_data.py after generation
5. **Dashboard refresh** - Always click refresh after new data

## 🐛 Troubleshooting

### "Failed to connect"
- Check `.env` file has correct credentials
- Verify DATABRICKS_HOST and DATABRICKS_TOKEN
- Test: `databricks workspace ls /`

### "Statement failed"
- Ensure SQL Warehouse is running
- Verify bronze_leases and silver_leases tables exist
- Check INSERT permissions

### "Data not appearing in frontend"
- Make sure you used `generate_and_promote.py` (recommended)
- OR run `promote_to_silver.py` after generating data
- Frontend reads from silver_leases, not bronze_leases
- Check browser console for API errors

### "Timeout"
- Reduce batch_size in script
- Ensure warehouse isn't overloaded
- Try during off-peak hours

## 📈 Performance

- **Generation:** Instant (< 1 second for 100 leases)
- **Insertion:** ~0.5-1 second per batch (10 leases)
- **Total time:** 10-20 seconds for 100 leases
- **Dashboard load:** < 3 seconds with 200 leases

## 🎯 Perfect For

- ✅ Demo presentations
- ✅ PoC showcases
- ✅ Testing at scale
- ✅ User training
- ✅ Dashboard development
- ✅ Query optimization

## 📝 Notes

- Generated names are realistic but fictitious
- Data is completely synthetic
- Safe for demos and testing
- No PII or sensitive information
- Complements existing dashboard features

---

**Ready to populate your dashboard with realistic data!** 🚀

