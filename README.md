# FINS Lease Extraction System

AI-powered commercial lease document extraction and portfolio risk analytics platform built with Databricks, React, and Flask.

## 🎯 Overview

This system automates the extraction of critical data from commercial real estate lease agreements using AI agents, stores the data in a structured format using Databricks Unity Catalog, and provides interactive analytics and risk assessment dashboards.

## 📁 Project Structure

```
fins-lease-extraction/
├── app/                     # React frontend + Flask backend
│   ├── src/                 # React components
│   └── backend/             # Flask API server
├── DatabricksResources/     # Databricks SQL scripts and configurations
├── LeaseGeneration/         # Synthetic lease PDF generator
└── DataGeneration/          # Synthetic data utilities
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Databricks workspace with Unity Catalog
- Databricks SQL Warehouse

### 1. Backend Setup

```bash
cd app/backend

# Create .env file with your credentials
cat > .env << EOF
DATABRICKS_HOST=your-workspace-url
DATABRICKS_TOKEN=your-token
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
DATABRICKS_CATALOG=fins_team_3
DATABRICKS_SCHEMA=lease_management
EOF

# Install dependencies and start
pip install -r requirements.txt
python api.py
```

Backend runs on http://localhost:5001

### 2. Frontend Setup

```bash
cd app

# Install dependencies
npm install

# Start development server
npm start
```

Frontend opens on http://localhost:3000

### 3. Databricks Setup

Run these scripts in your Databricks SQL Editor in order:

```sql
-- 1. Create tables
DatabricksResources/CreateRawTable.sql
DatabricksResources/CreateBronzeTable.sql
DatabricksResources/CreateSilverTable.sql
DatabricksResources/CreateGoldTable.sql

-- 2. Set up extraction agent
-- Import ExtractionAgent.json as an AI agent

-- 3. Create directories (run in notebook)
DatabricksResources/DirectoryCreation.py
```

## 🎨 Features

### 📤 Document Upload & Extraction
- Drag-and-drop PDF upload interface
- AI-powered extraction of 28+ lease fields
- Validation workflow for human review
- Automatic promotion to structured tables

### 📊 Portfolio Analytics
- Real-time KPI dashboard
- Interactive lease map visualization
- Market summary by location
- Comprehensive lease details table

### 🎯 Risk Assessment
- **Multi-dimensional risk scoring**:
  - Rollover Risk (40%) - lease expiration timing
  - Escalation Risk (20%) - inflation protection
  - Industry Risk (20%) - sector exposure
  - Concentration Risk (20%) - portfolio balance
- **4 Visualization Types**:
  - Bubble chart (risk vs. time matrix)
  - Radar chart (risk components)
  - Distribution charts (risk categories)
  - Industry sector analysis
- Top 10 highest risk leases table
- Actionable insights and recommendations

### 💬 AI Chat Assistant
- Natural language queries about portfolio
- Automatic SQL generation
- Contextual lease information

## 🗂️ Data Architecture

```
Raw Layer      → PDF documents in Unity Catalog volumes
Bronze Layer   → AI-extracted JSON data (unvalidated)
Silver Layer   → Validated, structured lease data
Gold Layer     → Risk scores and analytics
```

## 📚 Component Documentation

- **[app/README.md](app/README.md)** - Frontend application setup and architecture
- **[app/backend/README.md](app/backend/README.md)** - API endpoints and Databricks integration
- **[app/RISK_TROUBLESHOOTING.md](app/RISK_TROUBLESHOOTING.md)** - Risk assessment debugging guide
- **[LeaseGeneration/README.md](LeaseGeneration/README.md)** - Synthetic lease PDF generator
- **[DataGeneration/README.md](DataGeneration/README.md)** - Test data generation utilities

## 🔧 Development

### Tech Stack
- **Frontend**: React, Framer Motion, Recharts, Leaflet
- **Backend**: Flask, Python 3.8+
- **Database**: Databricks Unity Catalog
- **AI**: Databricks AI Agents
- **Visualization**: Recharts, React-Leaflet

### Key Dependencies
```bash
# Frontend
npm install react framer-motion recharts react-leaflet

# Backend  
pip install databricks-sdk flask flask-cors python-dotenv
```

## 📈 Risk Scoring Methodology

Total Risk Score = Weighted sum of four components:

1. **Rollover Risk (40%)**: Days until lease expiration
   - Critical: 0-90 days (score: 100)
   - High: 91-180 days (score: 90)
   - Elevated: 181-365 days (score: 75)
   - Monitor: 1-2 years (score: 40)
   - Stable: 2+ years (score: 10)

2. **Escalation Risk (20%)**: Annual rent escalation percentage
   - <2%: High risk (80) - below inflation
   - 2-3%: Moderate (50)
   - 3-4%: Good (30)
   - 4%+: Low risk (20)

3. **Industry Risk (20%)**: Tenant sector risk profile
   - Retail/Restaurant: 80
   - Tech/Office: 50
   - Healthcare/Government: 20

4. **Concentration Risk (20%)**: Portfolio exposure
   - >10% of portfolio: 90
   - 5-10%: 70
   - 2-5%: 40
   - <1%: 10

## 🧪 Testing with Synthetic Data

Generate realistic test leases:

```bash
cd LeaseGeneration
pip install -r requirements.txt
python generate_leases.py  # Generates 10 sample PDFs
```

Upload generated PDFs through the web interface to test the full pipeline.

## 🛠️ Troubleshooting

### Backend Connection Issues
1. Verify `.env` credentials are correct
2. Check Databricks SQL Warehouse is running
3. Test endpoint: `curl http://localhost:5001/api/health`

### Risk Assessment Not Loading
1. Ensure `gold_lease_risk_scores` view exists
2. Verify data in `silver_leases` table
3. Check browser console for detailed errors
4. See [RISK_TROUBLESHOOTING.md](app/RISK_TROUBLESHOOTING.md)

### Upload Issues
1. Check volume permissions in Databricks
2. Verify backend can write to Unity Catalog
3. Ensure AI agent is configured

## 📄 License

Internal use - FINS Team 3

## 🏗️ Built For

Buildathon Project - Commercial Real Estate Portfolio Risk Management

