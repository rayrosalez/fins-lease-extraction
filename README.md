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
-- 1. Create core tables
DatabricksResources/CreateRawTable.sql
DatabricksResources/CreateBronzeTable.sql
DatabricksResources/CreateSilverTable.sql       -- Updated with tenant_id/landlord_id

-- 2. Create enrichment tables
DatabricksResources/CreateTenantTable.sql       -- Tenant financial profiles
DatabricksResources/CreateLandlordTable.sql     -- Landlord financial profiles

-- 3. Create analytics layer
DatabricksResources/CreateGoldTable.sql         -- Enhanced with 4 risk models

-- 4. Set up extraction agent
-- Import ExtractionAgent.json as an AI agent

-- 5. Create directories (run in notebook)
DatabricksResources/DirectoryCreation.py

-- 6. (Optional) Generate synthetic data for demo
-- See DataGeneration/README.md
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
- **Adaptive risk scoring with 4 models**:
  - FULLY_ENRICHED: Uses tenant + landlord financial data (7 factors)
  - TENANT_ENRICHED: Uses tenant financial data only (6 factors)
  - LANDLORD_ENRICHED: Uses landlord financial data only (5 factors)
  - BASIC: Standard model when no enrichment available (4 factors)
- **Enriched risk factors**:
  - Tenant Credit Risk (financial health, credit rating)
  - Tenant Bankruptcy Risk (LOW/MEDIUM/HIGH)
  - Landlord Financial Strength (REIT profiles, portfolio quality)
- **Standard risk factors**:
  - Rollover Risk - lease expiration timing
  - Escalation Risk - inflation protection
  - Industry Risk - sector exposure
  - Concentration Risk - portfolio balance
- **4 Visualization Types**:
  - Bubble chart (risk vs. time matrix)
  - Radar chart (risk components)
  - Distribution charts (risk categories)
  - Industry sector analysis
- **Expandable lease details**:
  - Click any lease to see risk component breakdown
  - View tenant financial profiles (health score, credit rating, bankruptcy risk)
  - View landlord financial profiles (assets, portfolio size, D/E ratio)
  - Enrichment confidence scores and data sources
- Top 10 highest risk leases table with model badges
- Actionable insights and recommendations

### 💬 AI Chat Assistant
- Natural language queries about portfolio
- Automatic SQL generation
- Contextual lease information

## 🗂️ Data Architecture

```
Raw Layer      → PDF documents in Unity Catalog volumes
                 
Bronze Layer   → AI-extracted JSON data (unvalidated)
                 └─ bronze_leases table

Silver Layer   → Validated, structured lease data with enrichment IDs
                 └─ silver_leases table (tenant_id, landlord_id)

Enrichment     → Financial profiles for risk assessment
                 ├─ tenants table (credit ratings, health scores)
                 └─ landlords table (REIT profiles, portfolios)

Gold Layer     → Risk scores and analytics with adaptive models
                 └─ gold_lease_risk_scores view (LEFT JOIN enrichment)
                    ├─ FULLY_ENRICHED (tenant + landlord data)
                    ├─ TENANT_ENRICHED (tenant data only)
                    ├─ LANDLORD_ENRICHED (landlord data only)
                    └─ BASIC (fallback, no enrichment)
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

The system uses an **adaptive risk model** that adjusts based on available enrichment data:

### Risk Models

#### FULLY_ENRICHED Model (Both Tenant & Landlord Data Available)
Total Risk Score = Weighted sum of seven components:

1. **Rollover Risk (25%)**: Days until lease expiration
2. **Escalation Risk (10%)**: Annual rent escalation percentage  
3. **Industry Risk (10%)**: Tenant sector risk profile
4. **Concentration Risk (15%)**: Portfolio exposure
5. **Tenant Credit Risk (20%)**: Financial health score (inverted 1-10 to 0-100)
6. **Tenant Bankruptcy Risk (10%)**: HIGH/MEDIUM/LOW → 90/50/10
7. **Landlord Risk (10%)**: Financial strength score

#### TENANT_ENRICHED Model (Tenant Data Only)
Total Risk Score = Weighted sum of six components (30/15/10/15/20/10):
- Rollover, Escalation, Industry, Concentration, Tenant Credit, Tenant Bankruptcy

#### LANDLORD_ENRICHED Model (Landlord Data Only)  
Total Risk Score = Weighted sum of five components (35/15/15/20/15):
- Rollover, Escalation, Industry, Concentration, Landlord Risk

#### BASIC Model (No Enrichment - Fallback)
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

### How Enrichment Improves Accuracy

**Example: Retail Tenant Lease**

**Without Enrichment (BASIC):**
- Industry Risk: 80 (Retail = high risk)
- Total Score: 65 (based on lease terms only)

**With Enrichment (FULLY_ENRICHED):**
- Industry Risk: 80 (Retail)
- Tenant Health: 8.5/10 → Credit Risk: 16.7 (strong company)
- Tenant Bankruptcy: LOW → Score: 10 (low risk)
- Landlord Health: 8.9/10 → Risk: 12.2 (stable REIT)
- **Total Score: 38** (significantly lower due to strong financials)

The enriched model reveals that despite being in a high-risk industry, the tenant's excellent financial health and stable landlord reduce overall risk by 27 points!

## 🧪 Testing with Synthetic Data

Generate realistic test leases:

```bash
cd LeaseGeneration
pip install -r requirements.txt
python generate_leases.py  # Generates 10 sample PDFs
```

Upload generated PDFs through the web interface to test the full pipeline.

## 📖 Glossary

### Data Layers
- **Raw Layer** - Unprocessed PDF lease documents stored in Unity Catalog Volumes
- **Bronze Layer** - AI-extracted JSON data from PDFs, unvalidated (bronze_leases table)
- **Silver Layer** - Validated, structured, production-ready lease data (silver_leases table)
- **Gold Layer** - Aggregated analytics and risk scores (gold_lease_risk_scores view)

### Enrichment Tables
- **Tenants Table** - Financial profiles of tenant companies with credit ratings, health scores, bankruptcy risk
- **Landlords Table** - Financial profiles of property owners/REITs with portfolio statistics and credit ratings
- **Tenant ID** - Normalized identifier linking leases to tenant enrichment data
- **Landlord ID** - Normalized identifier linking leases to landlord enrichment data

### Risk Scoring
- **Risk Model** - Algorithm used to calculate risk score, varies based on enrichment availability
  - **FULLY_ENRICHED** - Uses both tenant and landlord financial data (7 factors)
  - **TENANT_ENRICHED** - Uses only tenant financial data (6 factors)
  - **LANDLORD_ENRICHED** - Uses only landlord financial data (5 factors)
  - **BASIC** - No enrichment data, uses standard factors only (4 factors)
- **Financial Health Score** - 1-10 rating of company's financial stability (10 = excellent)
- **Credit Rating** - Letter grade (AAA to B) indicating creditworthiness
- **Bankruptcy Risk** - Assessment level: LOW, MEDIUM, or HIGH
- **Industry Risk** - Sector-specific risk based on market volatility
- **Rollover Risk** - Risk from lease expiration timing (40% weight in BASIC model)
- **Escalation Risk** - Risk from insufficient rent escalation vs inflation (20% weight)
- **Concentration Risk** - Risk from portfolio exposure to single tenant (20% weight)
- **Tenant Credit Risk** - Risk score derived from tenant financial health (0-100)
- **Landlord Risk** - Risk score derived from landlord financial strength (0-100)

### Lease Terms
- **Commencement Date** - Lease start date
- **Expiration Date** - Lease end date
- **Term Months** - Total lease duration in months
- **Base Rent PSF** - Annual rent per square foot
- **Annual Escalation** - Yearly percentage rent increase
- **Triple Net (NNN)** - Lease type where tenant pays property taxes, insurance, and maintenance
- **Modified Gross** - Lease type with shared operating expenses
- **Suite/Unit** - Specific leased space identifier within a property
- **Rentable Square Feet** - Total leasable area in square feet

### Validation & Status
- **Validation Status** - Record state: NEW, PENDING, VERIFIED, DELETED
- **Enhancement Source** - Data origin: AI_ONLY, AI_MCP, AI_HUMAN_VERIFIED, USER_ENTRY
- **Enrichment Confidence** - 0-1 score indicating data quality/accuracy of enrichment
- **Enrichment Coverage** - Percentage of leases with tenant/landlord enrichment data

### Property Data
- **Property ID** - Unique identifier for leased property
- **Lease ID** - Unique identifier for lease agreement
- **Market** - Geographic location/metro area
- **Industry Sector** - Tenant's business category (Technology, Healthcare, Retail, etc.)

### Financial Metrics (Tenant Enrichment)
- **Market Cap** - Total market value of publicly traded company
- **Annual Revenue** - Total yearly income
- **Net Income** - Profit after all expenses
- **Revenue Growth** - Year-over-year revenue change percentage
- **Profit Margin** - Net income as percentage of revenue
- **Payment History Score** - 1-100 rating of on-time payment reliability
- **DUNS Number** - Dun & Bradstreet business identifier
- **Litigation Flag** - Boolean indicating ongoing significant legal issues

### Financial Metrics (Landlord Enrichment)
- **Total Assets** - Combined value of all properties and holdings
- **Net Operating Income (NOI)** - Revenue minus operating expenses
- **Debt-to-Equity Ratio** - Leverage metric showing debt vs equity financing
- **Total Properties** - Number of properties in landlord's portfolio
- **Total Square Footage** - Combined leasable area across all properties
- **Primary Property Types** - Main categories (Office, Retail, Industrial, Healthcare, etc.)
- **Geographic Focus** - Markets/regions where landlord operates

### System Components
- **Unity Catalog** - Databricks data governance layer
- **SQL Warehouse** - Databricks compute resource for queries
- **Delta Lake** - ACID-compliant storage format
- **Volumes** - File storage locations in Unity Catalog
- **AI Agent** - Databricks AI for document extraction
- **MCP (Model Context Protocol)** - Framework for AI enrichment via web search

### API & Frontend
- **KPI** - Key Performance Indicator (metrics like total leases, revenue, etc.)
- **Portfolio Concentration** - Percentage of total portfolio represented by single lease
- **Lease Status** - Risk-based categorization: CRITICAL, HIGH_PRIORITY, NEEDS_ATTENTION, MONITOR, STABLE
- **Days to Expiry** - Number of days until lease ends (negative = already expired)

### Data Generation
- **Synthetic Data** - Artificially generated realistic lease data for testing/demo
- **Enrichment Rate** - Percentage of generated data that includes tenant/landlord enrichment
- **REIT** - Real Estate Investment Trust (publicly traded landlord company)

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

