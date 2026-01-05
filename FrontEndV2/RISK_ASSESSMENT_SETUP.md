# Risk Assessment Feature - Setup Guide

## What Was Added

### 1. Backend API Endpoint
- New endpoint: `/api/portfolio/risk-assessment`
- Queries the `gold_lease_risk_scores` view in Databricks
- Returns comprehensive risk data for all leases

### 2. Frontend Component
- **RiskAssessment.js** - Main risk visualization component
- **RiskAssessment.css** - Styling for risk visualizations

### 3. Visualizations Included

#### 🫧 Bubble Chart (Risk vs Time Matrix)
- X-axis: Days until expiration
- Y-axis: Total risk score
- Bubble size: Annual rent value
- Color-coded by risk level
- Interactive tooltips with detailed lease info

#### 📡 Risk Components Radar
- Shows 4 risk dimensions:
  - Rollover Risk (lease expiration timing)
  - Escalation Risk (rent keeping pace with inflation)
  - Industry Risk (sector-specific risk)
  - Concentration Risk (portfolio exposure)
- Average scores across portfolio

#### 📊 Risk Distribution
- Pie chart showing lease count by risk category
- Bar chart showing distribution breakdown
- Categories: Critical, High, Medium, Low, Minimal

#### 🏢 Risk by Industry Sector
- Horizontal bar chart by industry
- Shows average risk scores
- Displays lease count and total rent per sector
- Color-coded by risk level

### 4. Additional Features

- **Summary Cards**: Quick stats on critical leases, high priority, avg risk, revenue at risk
- **Top 10 Risk Table**: Detailed table of highest risk leases
- **Status Filtering**: Filter by lease status (Critical, High Priority, etc.)
- **Key Insights**: Actionable recommendations based on risk analysis
- **Responsive Design**: Works on desktop and mobile

## Installation

### Step 1: Install Dependencies

In the FrontEndV2 directory:

```bash
cd FrontEndV2
npm install
```

This will install the new `recharts` library needed for visualizations.

### Step 2: Ensure Gold Table Exists

The risk assessment queries `gold_lease_risk_scores` view. Make sure it's created:

```sql
-- Run this in Databricks
USE CATALOG fins_team_3;
USE SCHEMA lease_management;

-- Execute the CreateGoldTable.sql script
```

### Step 3: Start Backend (if not running)

```bash
cd backend
python api.py
```

Backend should be running on port 5001.

### Step 4: Start Frontend (if not running)

```bash
cd FrontEndV2
npm start
```

Frontend should open on http://localhost:3000

## Usage

1. Navigate to **Portfolio** section
2. Click on the **"🎯 Risk Assessment"** tab (second tab)
3. Explore different visualizations:
   - Click **"🫧 Bubble Chart"** for risk vs time view
   - Click **"📡 Risk Components"** for radar analysis
   - Click **"📊 Distribution"** for category breakdown
   - Click **"🏢 By Industry"** for sector analysis
4. Use the **Status Filter** to focus on specific lease statuses
5. Review the **Top 10 Highest Risk Leases** table
6. Read **Key Insights** for actionable recommendations

## Risk Scoring Explained

### Total Risk Score (0-100)
Weighted combination of four components:
- **Rollover Risk (40%)**: Based on days until lease expiration
- **Escalation Risk (20%)**: Based on annual rent escalation percentage
- **Industry Risk (20%)**: Based on tenant's industry sector
- **Concentration Risk (20%)**: Based on lease's share of total portfolio

### Risk Categories
- **Critical (80-100)**: Immediate action required
- **High (60-79)**: High priority attention needed
- **Medium (40-59)**: Monitor closely
- **Low (20-39)**: Routine monitoring
- **Minimal (0-19)**: Stable, low concern

### Lease Statuses
- **CRITICAL**: Expiring 0-90 days
- **HIGH_PRIORITY**: Expiring 91-180 days
- **NEEDS_ATTENTION**: Expiring 181-365 days
- **MONITOR**: Expiring 1-2 years
- **STABLE**: Expiring 2+ years
- **EXPIRED_RECENT**: Expired within last year
- **EXPIRED_OLD**: Expired over 1 year ago

## Troubleshooting

### "Failed to fetch risk data"
- Check that backend is running on port 5001
- Verify Databricks credentials in `.env` file
- Ensure `gold_lease_risk_scores` view exists

### Empty visualizations
- Verify there's data in `silver_leases` table
- Check that risk scores are being calculated
- Look for errors in browser console (F12)

### Charts not displaying
- Verify `recharts` was installed: `npm list recharts`
- If not, run: `npm install recharts@^2.10.3`
- Restart the dev server

## Technical Details

### API Response Format
```json
[
  {
    "lease_id": "string",
    "tenant_name": "string",
    "property_id": "string",
    "industry_sector": "string",
    "lease_end_date": "YYYY-MM-DD",
    "annual_escalation_pct": 3.0,
    "estimated_annual_rent": 500000,
    "square_footage": 10000,
    "days_to_expiry": 180,
    "sector_risk_base": 50,
    "portfolio_concentration_pct": 2.5,
    "rollover_score": 90,
    "escalation_risk_score": 50,
    "concentration_risk_score": 40,
    "lease_status": "HIGH_PRIORITY",
    "total_risk_score": 67.5
  }
]
```

### Component Structure
- `RiskAssessment.js` - Main component with state and data fetching
- `RiskAssessment.css` - Comprehensive styling
- Uses React Hooks (useState, useEffect, useMemo)
- Framer Motion for animations
- Recharts for data visualizations

## Future Enhancements

Possible additions:
- Export risk report to PDF
- Email alerts for critical leases
- Historical risk trend analysis
- Custom risk weighting configuration
- Drill-down into individual lease details
- Comparison with market benchmarks

---

**Created**: January 5, 2026  
**Version**: 1.0  
**Status**: Production Ready

