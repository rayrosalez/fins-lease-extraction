# Lease Intelligence Platform - Frontend Application

## Overview

A comprehensive Streamlit-based frontend application for the AI-Powered Lease Intelligence Platform. This application provides real estate portfolio managers and private equity firms with advanced analytics, visualizations, and data management capabilities for commercial lease portfolios.

## Features

### 1. Portfolio Dashboard
- **Advanced Filtering**: Search by property/tenant name, filter by risk level, and select specific markets
- **Key Performance Indicators (KPIs)**:
  - Total leases, properties, tenants, and markets
  - Average rent per square foot
  - Portfolio WALT (Weighted Average Lease Term)
  - AI-powered risk index
- **Market Analysis**:
  - Lease count by market
  - Average rent PSF by market
  - WALT analysis by market
  - Risk index visualization by market
- **Risk Analysis**:
  - Lease risk factors (termination options, ROFR clauses)
  - Rent escalation type distribution
- **New Visualizations**:
  - **Lease Expiration Timeline**: Visual timeline showing when leases expire
  - **Rent Analysis**: Distribution and industry comparisons
  - **Portfolio Composition**: Pie charts for market, asset type, and industry distribution
  - **Predictive Insights**: Lease expiration forecast with risk trends
- **Detailed Data Tables**:
  - Market summary with downloadable CSV
  - All lease details with AI enrichments
  - High-risk lease identification

### 2. Upload Lease
- **Single Upload**: Upload individual lease PDFs
- **Batch Upload**: Upload multiple lease PDFs simultaneously for parallel processing
  - Progress tracking
  - Success/failure reporting
  - Detailed upload results
- **AI Processing**: Automatic extraction and structuring of lease data

### 3. Manual Data Entry (NEW)
- **New Entry**: Manually add lease data without PDF upload
  - Property & tenant information
  - Lease terms and dates
  - Financial details
  - Risk flags
- **Correction Interface**: Edit existing lease data
  - Select any lease from the portfolio
  - Modify incorrect values
  - Track correction reasons
  - Audit trail for all changes

### 4. Analytics & Export (NEW)
- **Quick Exports**:
  - Export all leases to CSV
  - Export high-risk leases only
  - Export market summary
- **Custom Reports**:
  - SQL query builder for advanced users
  - Execute custom queries
  - Download results as CSV
- **API Access**:
  - Python SDK examples
  - REST API examples
  - Programmatic data access documentation

### 5. AI Pipeline
- **Architecture Visualization**: Interactive view of the data pipeline
  - Stage 1: Document Upload
  - Stage 2: AI Document Parser (Raw Layer)
  - Stage 3: Bronze Layer (Agent Parsing)
  - Stage 4: Silver Layer (Multi-Source Enrichment)
  - Stage 5: Gold Layer (Analytics & Intelligence)
- **Technology Stack**: Overview of Databricks, AI/ML, and application technologies
- **Performance Metrics**: System capabilities and benchmarks

## Installation

### Prerequisites
- Python 3.9 or higher
- Databricks workspace with Unity Catalog
- SQL Warehouse access

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the FrontEnd directory:
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-access-token
```

3. Run the application:
```bash
streamlit run app.py
```

## Configuration

Configure the following in the sidebar:
- **Catalog**: Unity Catalog name (default: `fins_team_3`)
- **Schema**: Schema name (default: `lease_management`)
- **Volume**: Volume name for file storage (default: `raw_lease_docs`)
- **Warehouse ID**: SQL Warehouse ID for queries

## Data Pipeline

### Tables Used

1. **raw_leases**: Raw PDF parse results
   - `file_path`: Location of PDF in volume
   - `raw_parsed_json`: AI-parsed document content
   - `ingested_at`: Timestamp

2. **bronze_leases**: Structured lease data from AI extraction
   - Landlord and tenant information
   - Lease terms and dates
   - Financial details
   - Risk and option clauses

3. **fact_lease**: Enriched lease facts (Silver Layer)
   - All bronze fields plus enrichments
   - AI risk scores
   - Market data
   - Industry classifications

4. **dim_property**: Property dimension table
   - Property details
   - Market information
   - Asset type classification

5. **dim_tenant**: Tenant dimension table
   - Tenant information
   - Industry sector
   - Credit ratings

6. **gold_portfolio_health**: Pre-aggregated portfolio metrics
   - Market-level aggregations
   - WALT calculations
   - Risk indices

## Key Visualizations

### Interactive Charts
- **Bar Charts**: Market analysis, rent comparisons
- **Line Charts**: WALT trends, risk forecasts
- **Pie Charts**: Portfolio composition breakdowns
- **Timeline**: Lease expiration visualization
- **Histogram**: Rent distribution analysis
- **Multi-axis Charts**: Expiration forecast with risk overlay

All charts are interactive with:
- Hover tooltips
- Zoom and pan
- Export to PNG
- Color-coded by metrics

## Export Capabilities

### Supported Export Formats
- **CSV**: All data tables
- **SQL Results**: Custom query outputs
- **Visual Reports**: (PDF generation ready for implementation)

### Export Types
1. Complete portfolio data
2. Filtered data (high-risk, expiring soon, etc.)
3. Market summaries
4. Custom query results

## API Integration

The application uses the Databricks SDK to:
- Upload files to Unity Catalog Volumes
- Execute SQL queries via SQL Warehouses
- Retrieve structured data from Delta tables
- Support real-time data refresh

## Performance

- **Load Time**: < 3 seconds for dashboard
- **Query Execution**: Typically < 2 seconds
- **Batch Upload**: Parallel processing of multiple files
- **Data Refresh**: On-demand via refresh button

## Best Practices

1. **Data Refresh**: Click the "Refresh Data" button after uploading new leases
2. **Batch Processing**: Use batch upload for multiple files to save time
3. **Manual Corrections**: Use the correction interface to improve AI accuracy
4. **Export Regularly**: Download data for backup and external analysis
5. **Monitor Risk**: Check the high-risk leases tab regularly

## Troubleshooting

### Connection Issues
- Verify DATABRICKS_HOST and DATABRICKS_TOKEN in .env
- Ensure SQL Warehouse is running
- Check network connectivity

### No Data Displayed
- Verify tables exist in the specified catalog/schema
- Check SQL Warehouse permissions
- Ensure data has been processed through the pipeline

### Upload Failures
- Verify volume path exists
- Check file size limits
- Ensure proper permissions on Unity Catalog volume

## Future Enhancements

- [ ] PDF report generation
- [ ] Email alerts for expiring leases
- [ ] Mobile-responsive design
- [ ] Multi-user collaboration features
- [ ] Automated lease renewal recommendations
- [ ] Integration with external property management systems

## Support

For issues or questions, refer to the Databricks documentation or contact your workspace administrator.

## Version

Current Version: 2.0.0
Last Updated: December 2025

