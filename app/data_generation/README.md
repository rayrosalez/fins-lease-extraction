# Data Generation Scripts

This directory contains the data generation scripts used by the "Reset Demo" button in the application.

## Files

### `generate_enriched_data.py`
Main script for generating synthetic lease data with enrichment. This is called by the backend API endpoint `/api/reset-demo-data`.

**Functions:**
- `generate_synthetic_lease_data(num_leases, enrichment_rate)` - Generates synthetic data
- `insert_landlords(client, warehouse_id, landlords)` - Inserts landlord records
- `insert_tenants(client, warehouse_id, tenants)` - Inserts tenant records
- `insert_leases(client, warehouse_id, leases)` - Inserts lease records

### `sp500_companies.py`
Contains lists of S&P 500 companies used for realistic tenant name generation.

**Exports:**
- `SP500_COMPANIES` - List of company names
- `COMPANY_SECTORS` - Dictionary mapping companies to sectors
- `get_sector_for_company(company)` - Helper function to get sector

## Usage

These scripts are automatically called by the backend when the "Reset Demo" button is clicked in the UI. They should not need to be run manually.

## Dependencies

Required packages (installed via `app/backend/requirements.txt`):
- `faker` - For generating realistic fake data
- `databricks-sdk` - For Databricks API access
- `python-dotenv` - For environment variable management

## Deployment

This directory is part of the `app/` deployment directory and will be deployed along with the rest of the application.
