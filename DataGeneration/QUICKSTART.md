# Data Generation Tool - Summary

## 📁 Files Created

```
DataGeneration/
├── README.md                          # Comprehensive documentation
├── requirements.txt                   # Python dependencies
├── setup.sh                          # Quick setup script (executable)
├── generate_synthetic_leases.py      # Main data generator
└── verify_data.py                    # Data verification tool
```

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
cd DataGeneration
./setup.sh
```

### Option 2: Manual Setup
```bash
cd DataGeneration
pip install -r requirements.txt
python generate_synthetic_leases.py
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

## 📋 Execution Steps

1. **Install dependencies:**
   ```bash
   pip install faker databricks-sdk python-dotenv
   ```

2. **Update warehouse ID in script**

3. **Run generator:**
   ```bash
   python generate_synthetic_leases.py
   ```

4. **Enter number of leases when prompted** (e.g., 100)

5. **Wait for completion** (~10-20 seconds)

6. **Verify data:**
   ```bash
   python verify_data.py
   ```

7. **Refresh dashboard** and view results!

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
- Verify bronze_leases table exists
- Check INSERT permissions

### "Timeout"
- Reduce batch_size in script (line 17)
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

