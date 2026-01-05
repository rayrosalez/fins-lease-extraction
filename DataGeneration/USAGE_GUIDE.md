# Complete Usage Guide - DataGeneration

## 🎯 Goal
Generate synthetic lease data that immediately appears in your frontend application.

## 📋 Prerequisites

1. **Python packages installed:**
   ```bash
   pip install faker databricks-sdk python-dotenv
   ```

2. **Environment configured:**
   - `.env` file exists with `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
   - SQL Warehouse is running
   - `bronze_leases` and `silver_leases` tables exist

3. **Frontend running:**
   - Backend API running on port 5001
   - React frontend running on port 3000

## 🚀 Three Ways to Generate Data

### Option 1: All-in-One (RECOMMENDED) ⭐

**Best for:** Quick testing, demos, most common use case

```bash
cd DataGeneration
python3 generate_and_promote.py 100
```

**What it does:**
- ✅ Generates 100 synthetic leases
- ✅ Inserts into bronze_leases
- ✅ Promotes VERIFIED records to silver_leases
- ✅ Shows verification counts
- ✅ Data immediately appears in frontend

**Time:** ~15-20 seconds for 100 leases

---

### Option 2: Quick Test Script

**Best for:** First-time testing, verification

```bash
cd DataGeneration
./quick_test.sh
```

**What it does:**
- ✅ Generates 50 leases (smaller sample)
- ✅ Complete bronze → silver flow
- ✅ Interactive prompts
- ✅ Provides next steps

**Time:** ~10 seconds for 50 leases

---

### Option 3: Manual Two-Step

**Best for:** Advanced users, debugging, custom workflows

**Step 1 - Generate and insert to bronze:**
```bash
python3 generate_synthetic_leases.py
```

**Step 2 - Promote to silver:**
```bash
python3 promote_to_silver.py
```

**Time:** ~20-25 seconds total for 100 leases

---

## ✅ Verify Data Loaded

After running any generation script:

```bash
python3 check_silver.py
```

**Expected output:**
```
✅ Total leases in silver_leases: 100
✅ Data is ready for frontend!

📊 Data Summary:
  - Industries: 12
  - Cities: 12
  - Avg Rent PSF: $45.32
```

---

## 🌐 Check Frontend

1. Open browser to `http://localhost:3000`
2. You should see:
   - ✅ Portfolio KPIs updated (total leases, properties, etc.)
   - ✅ Map shows property locations
   - ✅ Charts populated with data
   - ✅ Lease table shows records

3. If data doesn't appear:
   - Refresh the page
   - Check browser console for errors
   - Verify backend is running on port 5001
   - Run `python3 check_silver.py` to confirm data in database

---

## 🔄 Data Flow Explained

```
┌─────────────────────────────────────┐
│  generate_and_promote.py            │
│  (or generate_synthetic_leases.py)  │
└──────────────┬──────────────────────┘
               │
               ▼
     ┌─────────────────┐
     │  BRONZE TABLE   │  ← All generated data inserted here
     │  bronze_leases  │     (includes VERIFIED and PENDING)
     └────────┬────────┘
              │
              │ Filter VERIFIED records only
              │ (promote_to_silver.py or built-in)
              │
              ▼
     ┌─────────────────┐
     │  SILVER TABLE   │  ← Only VERIFIED data
     │  silver_leases  │     (clean, validated records)
     └────────┬────────┘
              │
              │ API queries silver table
              │
              ▼
     ┌─────────────────┐
     │   FRONTEND UI   │  ← Users see the data
     │  React Dashboard │
     └─────────────────┘
```

**Key Point:** The frontend **only reads from silver_leases**. That's why promotion is essential!

---

## 📊 Generated Data Characteristics

### Realistic Attributes

- **12 Industries:** Technology, Healthcare, Finance, Retail, etc.
- **12 Markets:** SF, NY, Boston, Seattle, LA, Austin, Miami, Chicago, Denver, Dallas, Atlanta, Phoenix
- **15 Landlords:** Real estate companies (Blackstone, Brookfield, etc.)
- **Lease Terms:** 3, 5, 7, or 10 years
- **Rent Ranges:** $24-$100 PSF (market-based)
- **Square Footage:** 1,500 - 35,000 sq ft
- **Status:** 83% VERIFIED, 17% PENDING

### Perfect for Demos

The data is optimized to showcase:
- ✅ Portfolio diversity (multiple industries, markets)
- ✅ Geographic spread (map visualization)
- ✅ Timeline visualization (expirations over time)
- ✅ Rent analysis (realistic distributions)
- ✅ Market comparisons (varied pricing by city)

---

## 🔧 Configuration

### Default Settings

All scripts use these defaults (edit if needed):

```python
CATALOG = "fins_team_3"
SCHEMA = "lease_management"
WAREHOUSE_ID = "288a7ec183eea397"
```

### Customize Number of Leases

**Command-line argument:**
```bash
python3 generate_and_promote.py 150
```

**Interactive prompt:**
```bash
python3 generate_and_promote.py
# Enter number when prompted
```

**Recommendations:**
- Testing: 20-50 leases
- Demo: 100 leases
- Full simulation: 150-200 leases

---

## 🐛 Troubleshooting

### Problem: "No data in silver table"

**Check 1:** Did you promote to silver?
```bash
python3 check_silver.py
```

**Solution:** Use `generate_and_promote.py` instead of just `generate_synthetic_leases.py`

---

### Problem: "Frontend shows empty dashboard"

**Check 1:** Is backend API running?
```bash
# In FrontEndV2/backend directory
python3 api.py
```

**Check 2:** Is data in silver table?
```bash
python3 check_silver.py
```

**Check 3:** Browser console errors?
- Open DevTools (F12)
- Check Console tab for API errors
- Check Network tab for failed requests

---

### Problem: "Connection failed"

**Check:** Environment variables
```bash
# Verify .env file exists
cat ../FrontEndV2/backend/.env

# Should contain:
# DATABRICKS_HOST=https://...
# DATABRICKS_TOKEN=...
```

**Check:** SQL Warehouse running
- Log into Databricks
- Go to SQL → Warehouses
- Ensure warehouse is "Running" (not "Stopped")

---

### Problem: "Statement timeout"

**Solution:** Reduce batch size

Edit script and change:
```python
batch_size = 10  # Default
```

To:
```python
batch_size = 5  # Smaller, more stable
```

---

## 🔄 Re-running Scripts

### Add More Data
Just run again - new leases will be added:
```bash
python3 generate_and_promote.py 50  # Add 50 more
```

### Start Fresh
Clear both tables and regenerate:
```sql
-- In Databricks SQL Editor
TRUNCATE TABLE fins_team_3.lease_management.bronze_leases;
TRUNCATE TABLE fins_team_3.lease_management.silver_leases;
```

Then:
```bash
python3 generate_and_promote.py 100
```

---

## 📈 Performance Tips

1. **Larger batches = faster** (but risk timeout)
   - Default: 10 leases per batch
   - Safe range: 5-15 leases per batch

2. **Generate once, promote separately** for debugging
   ```bash
   python3 generate_synthetic_leases.py  # Insert to bronze
   # Debug bronze data
   python3 promote_to_silver.py          # Promote to silver
   ```

3. **Monitor warehouse utilization**
   - Check Databricks SQL History
   - View query execution times
   - Adjust batch size if needed

---

## 📁 Script Reference

| Script | Purpose | Output Table(s) | Recommended For |
|--------|---------|-----------------|-----------------|
| `generate_and_promote.py` | Complete pipeline | Bronze + Silver | ⭐ Most users |
| `generate_synthetic_leases.py` | Bronze only | Bronze | Advanced/debugging |
| `promote_to_silver.py` | Promotion only | Silver | Manual workflow |
| `check_silver.py` | Verification | N/A | Quick checks |
| `verify_data.py` | Full analysis | N/A | Data validation |
| `quick_test.sh` | Guided test | Bronze + Silver | First-time users |
| `setup.sh` | Automated setup | N/A | Initial setup |

---

## ✨ Best Practices

1. **Start small:** Test with 20 leases first
2. **Use all-in-one:** `generate_and_promote.py` for simplicity
3. **Verify always:** Run `check_silver.py` after generation
4. **Check frontend:** Refresh browser to see data
5. **Monitor logs:** Watch terminal output for errors
6. **Clean between tests:** Use TRUNCATE for fresh starts

---

## 🎯 Quick Command Reference

```bash
# Most Common: Generate and see data immediately
python3 generate_and_promote.py 100

# Quick test with small dataset
./quick_test.sh

# Verify data loaded successfully
python3 check_silver.py

# Full verification with statistics
python3 verify_data.py

# Clean slate (run in Databricks SQL Editor)
TRUNCATE TABLE fins_team_3.lease_management.bronze_leases;
TRUNCATE TABLE fins_team_3.lease_management.silver_leases;
```

---

## 📞 Need Help?

1. Check this guide first
2. Run `python3 check_silver.py` to diagnose
3. Check browser console (F12) for frontend errors
4. Verify SQL Warehouse is running
5. Check Databricks SQL History for query errors

---

**🎉 You're ready to generate data!**

Start with:
```bash
python3 generate_and_promote.py 100
```

