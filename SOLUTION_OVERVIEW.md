# Commercial Real Estate Lease Intelligence Platform
## A Databricks Solution Accelerator for Portfolio Risk Management

---

## The Scenario: Meet Susan

**Susan Chen** is the **Vice President of Portfolio Analytics** at Meridian Capital Partners, a mid-market real estate private equity firm managing $2.8 billion in commercial real estate assets across 340 properties and 1,200+ active leases.

### Susan's Daily Challenges

Susan is responsible for providing executive leadership with accurate, timely insights into portfolio health and risk exposure. Her challenges include:

- **Manual document processing**: Her team spends 15+ hours per week manually extracting lease terms from PDF documents, leading to data entry errors and delays
- **Fragmented data sources**: Lease information is scattered across spreadsheets, property management systems, and filing cabinets with no single source of truth
- **Reactive risk management**: Without consolidated lease data, rollover risk often surfaces too late—sometimes discovering critical expirations only 60 days out
- **Limited counterparty visibility**: No systematic way to assess tenant or landlord financial health, leaving the portfolio exposed to hidden credit risks
- **Time-consuming reporting**: Preparing quarterly board presentations requires weeks of manual data aggregation and reconciliation
- **Difficulty answering ad-hoc questions**: When leadership asks "What's our exposure to the retail sector?" or "Which markets have the most lease expirations next year?", Susan's team scrambles to compile answers

### What Susan Needs

Susan needs a solution that can:

- **Automate lease extraction** from PDF documents with AI, eliminating manual data entry
- **Centralize all lease data** in a governed, queryable platform
- **Proactively identify risks** before they become problems
- **Enrich tenant and landlord profiles** with external financial and market intelligence
- **Enable self-service analytics** so her team can answer questions in minutes, not days
- **Provide executive-ready dashboards** that update automatically

---

## Business Reality: The Commercial Real Estate Challenge

### Industry Context

Commercial real estate (CRE) is a $20+ trillion asset class where lease agreements are the lifeblood of cash flow. Yet the industry faces a significant digital transformation gap:

**The Paper Problem**
- 78% of commercial leases still originate as PDF documents
- Average lease document is 40-80 pages of complex legal language
- Critical terms (rent escalations, renewal options, expense pass-throughs) are buried in dense text
- Most firms still rely on manual extraction into spreadsheets

**The Risk Landscape**
- **Rollover risk**: Unexpected lease expirations can create sudden vacancies and cash flow disruptions
- **Tenant credit risk**: Economic downturns disproportionately impact certain industries (retail, hospitality)
- **Concentration risk**: Over-exposure to single tenants, industries, or geographies amplifies portfolio volatility
- **Escalation risk**: Below-market rent escalations erode returns in inflationary environments

**The Data Challenge**
- Lease data is typically siloed in property management systems that don't communicate
- No standardized schema for lease terms across the industry
- Limited integration with external data sources for counterparty risk assessment
- Reporting is manual, error-prone, and backward-looking

### Why This Matters Now

The convergence of AI capabilities and modern data platforms creates an opportunity to transform how CRE firms manage lease portfolios:

- **Large Language Models** can now extract structured data from unstructured documents with high accuracy
- **Unified data platforms** like Databricks enable real-time analytics across massive datasets
- **External data APIs** provide access to financial health indicators, news sentiment, and market intelligence
- **Self-service BI tools** empower business users to explore data without IT bottlenecks

---

## How the Data Helps

### The Data Foundation

This solution accelerator demonstrates a complete data architecture for lease portfolio intelligence:

| Data Layer | Description | Key Data Elements |
|------------|-------------|-------------------|
| **Raw** | PDF lease documents stored in Unity Catalog Volumes | Original source documents for audit trail |
| **Bronze** | AI-extracted lease data (unvalidated) | 28+ extracted fields including parties, dates, financials, terms |
| **Silver** | Validated, production-ready lease records | Human-reviewed data with quality scores |
| **Gold** | Risk scores and derived analytics | Multi-factor risk assessments, KPIs, aggregations |
| **Enriched** | External counterparty intelligence | Tenant/landlord financial health, news sentiment, credit ratings |

### Extracted Lease Fields

The AI extraction agent captures critical lease terms including:

**Parties & Property**
- Tenant name, address, industry sector
- Landlord name, contact information
- Property address, city, state, ZIP

**Financial Terms**
- Base rent per square foot
- Annual escalation percentage
- Security deposit
- Estimated annual rent

**Lease Terms**
- Commencement and expiration dates
- Square footage
- Lease type (NNN, Gross, Modified Gross)
- Renewal options
- Termination clauses

### Enriched Counterparty Data

Beyond lease extraction, the platform enriches tenant and landlord profiles with:

- **Financial health scores** (1-10 scale based on credit indicators)
- **Bankruptcy risk assessment** (Low/Medium/High)
- **Recent news sentiment** (Positive/Neutral/Negative)
- **Revenue and growth metrics**
- **Credit ratings** (where available)
- **Industry risk profiles**

### Risk Scoring Methodology

The platform calculates a composite risk score (0-100) based on four weighted factors:

| Risk Factor | Weight | What It Measures |
|-------------|--------|------------------|
| **Rollover Risk** | 40% | Days until lease expiration—identifies upcoming vacancies |
| **Escalation Risk** | 20% | Whether rent increases keep pace with inflation |
| **Industry Risk** | 20% | Sector-specific default and disruption risk |
| **Concentration Risk** | 20% | Portfolio exposure to individual tenants |

---

## Solution Accelerator Components

This repository provides a complete, deployable solution with the following components:

### 1. AI Document Extraction Pipeline

**Location**: `DatabricksResources/`

An end-to-end pipeline for processing lease documents:

- **Ingestor** (`01_Ingestor.py`): Monitors Unity Catalog Volume for new PDFs
- **Extraction Agent** (`ExtractionAgent.json`): Databricks AI agent configuration for lease field extraction
- **Data Tables**: SQL scripts for creating Bronze, Silver, and Gold layer tables
- **Promotion Logic**: Workflows to validate and promote data through layers

**AI Capabilities**:
- Extracts 28+ fields from complex legal documents
- Handles varied document formats and layouts
- Provides confidence scores for human review
- Supports batch processing for portfolio onboarding

### 2. Interactive Web Application

**Location**: `app/`

A modern React + Flask application providing:

**Upload & Processing**
- Drag-and-drop PDF upload interface
- Real-time processing status tracking
- Animated upload experience

**Human-in-the-Loop Validation**
- Review AI-extracted data side-by-side with source document
- Edit and correct fields before promotion
- Track validation status and quality metrics

**Portfolio Dashboard**
- Real-time KPIs (total leases, properties, tenants, markets)
- Interactive lease table with filtering and sorting
- Market summary by industry sector
- Geographic distribution map

**Risk Assessment**
- Multi-dimensional risk visualization (bubble charts, radar charts)
- Risk distribution analysis
- Industry sector risk breakdown
- Top 10 highest risk leases with actionable details

**AI Chat Assistant**
- Natural language queries about portfolio data
- Instant answers to questions like "What's our retail exposure?"
- SQL generation under the hood, plain English on top

### 3. Databricks AI/BI Dashboard

**Location**: `AIBIDashboard/`

A native Databricks dashboard (`LeasePortfolioAnalytics.lvdash.json`) providing:

| Dashboard Page | Visualizations |
|----------------|----------------|
| **Overview** | KPI counters, recent extractions table |
| **Risk Assessment** | Risk distribution pie/bar charts, industry risk analysis, top risky leases |
| **Location Analysis** | Geographic distribution by city and state |
| **All Leases** | Complete lease inventory with all fields |
| **Market Summary** | Portfolio metrics by industry sector |
| **Landlords** | Landlord profiles with financial health indicators |
| **Tenants** | Tenant profiles with growth and risk metrics |
| **Glossary** | Definitions of key CRE terms |

**Key Features**:
- Connects directly to Unity Catalog tables
- Shareable with stakeholders via Databricks workspace
- Supports AI-assisted chart creation
- Mobile-responsive design

### 4. Databricks Metric Views

**Location**: `AIBIDashboard/metric_views/deploy_all_metrics.sql`

Centralized, governed metric definitions for consistent analytics:

| Metric View | Purpose | Key Measures |
|-------------|---------|--------------|
| `portfolio_lease_metrics` | Core lease KPIs | total_leases, avg_rent_psf, expiring_90_days |
| `risk_assessment_metrics` | Risk scoring | avg_risk_score, high_risk_rent, critical_lease_count |
| `landlord_metrics` | Landlord health | avg_health_score, bankruptcy_risk distribution |
| `tenant_metrics` | Tenant health | revenue_growth, growing_companies, litigation_count |
| `market_performance_metrics` | Geographic performance | walt_years, total_annual_rent by market |

**Benefits**:
- Single source of truth for metric definitions
- Reusable across dashboards, notebooks, and applications
- Governed by Unity Catalog access controls
- Versioned and auditable

### 5. MCP Enrichment Agent

**Location**: `DatabricksResources/MCPEnrichmentAgent.json`

An AI agent that enriches tenant and landlord profiles with external intelligence:

- Queries external data sources for financial information
- Calculates financial health scores
- Assesses bankruptcy risk
- Captures recent news sentiment
- Integrates with the Silver layer for comprehensive counterparty profiles

### 6. Sample Data Generation

**Location**: `LeaseGeneration/` and `DataGeneration/`

Tools for generating realistic synthetic data for demos and testing:

- **Lease PDF Generator**: Creates realistic lease documents with varied terms
- **Data Generator**: Populates tables with synthetic but realistic portfolio data
- **Batch Processing**: Generate hundreds of leases for scale testing

---

## Demo Scenarios

### Scenario 1: New Lease Onboarding
1. Susan's team receives a batch of 50 new lease documents from a recent acquisition
2. They upload the PDFs through the web interface
3. The AI extraction agent processes documents in minutes (vs. weeks manually)
4. Analysts review and validate extracted data
5. Validated leases flow into the portfolio dashboard automatically

### Scenario 2: Quarterly Risk Review
1. Susan opens the AI/BI dashboard before the board meeting
2. She reviews the risk distribution—noting 12 leases in "Critical" status
3. She drills into the top risky leases table to identify specific concerns
4. She exports the findings for her board presentation
5. Total time: 15 minutes (vs. 2 weeks of manual analysis)

### Scenario 3: Ad-Hoc Executive Question
1. The CEO asks: "What's our exposure to tech tenants in San Francisco?"
2. Susan opens the AI chat assistant
3. She types the question in plain English
4. The system returns: 8 leases, $4.2M annual rent, 18% of SF portfolio
5. Total time: 30 seconds

---

## Getting Started

### Prerequisites
- Databricks workspace with Unity Catalog enabled
- SQL Warehouse (Serverless or Pro recommended)
- Python 3.8+ and Node.js 16+ (for web application)

### Deployment Steps

1. **Create Unity Catalog objects**
   ```sql
   -- Run scripts in DatabricksResources/ folder
   -- Creates catalog, schema, tables, and volumes
   ```

2. **Deploy AI extraction agent**
   - Import `ExtractionAgent.json` as a Databricks AI agent

3. **Deploy metric views**
   ```sql
   -- Run in Databricks SQL Editor
   %run AIBIDashboard/metric_views/deploy_all_metrics.sql
   ```

4. **Import AI/BI dashboard**
   - Upload `LeasePortfolioAnalytics.lvdash.json` via Databricks UI

5. **Start web application** (optional)
   ```bash
   # Backend
   cd app/backend && pip install -r requirements.txt && python api.py
   
   # Frontend
   cd app && npm install && npm start
   ```

6. **Generate sample data** (for demos)
   ```bash
   cd LeaseGeneration && python generate_leases.py
   ```

---

## Additional Resources

- [Databricks AI/BI Dashboards Documentation](https://docs.databricks.com/en/dashboards/)
- [Databricks Metric Views Documentation](https://docs.databricks.com/en/metric-views/)
- [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/)
- [Databricks AI Agents Documentation](https://docs.databricks.com/en/generative-ai/agent-framework/)

---

## Built With

| Component | Technology |
|-----------|------------|
| Data Platform | Databricks Unity Catalog, Delta Lake |
| AI/ML | Databricks AI Agents, Foundation Models |
| Dashboard | Databricks AI/BI, Metric Views |
| Web Frontend | React, Framer Motion, Recharts, Leaflet |
| Web Backend | Flask, Databricks SDK |
| Data Processing | Apache Spark, Databricks SQL |

---

*This solution accelerator is designed for demonstration purposes by Databricks field engineering teams. It showcases the art of the possible when combining AI document processing, unified data platforms, and modern analytics to solve real-world industry challenges.*
