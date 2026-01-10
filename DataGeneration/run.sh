#!/bin/bash

# Quick Start Script for Synthetic Data Generation
# ================================================

echo "=========================================="
echo "Synthetic Data Generator - Quick Start"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "[OK] Activated"
echo ""

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "[OK] Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo ""
    echo "Please create a .env file with:"
    echo "  DATABRICKS_HOST=https://your-workspace.cloud.databricks.com"
    echo "  DATABRICKS_TOKEN=your-token-here"
    echo ""
    read -p "Press Enter when .env is ready (or Ctrl+C to exit)..."
fi

# Check .env contents
if grep -q "your-workspace" .env 2>/dev/null || grep -q "your-token" .env 2>/dev/null; then
    echo "[WARNING] .env file contains placeholder values!"
    echo "Please update it with your actual Databricks credentials"
    echo ""
    read -p "Press Enter when ready (or Ctrl+C to exit)..."
fi

echo ""
echo "=========================================="
echo "Ready to generate synthetic data!"
echo "=========================================="
echo ""
echo "This will populate:"
echo "  - landlords table (20 REITs)"
echo "  - tenants table (unique companies)"
echo "  - silver_leases table (with enrichment IDs)"
echo ""
echo "Recommended: 100 leases with 0.8 enrichment rate"
echo ""

# Run the generator
python generate_enriched_data.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Check Databricks tables for data"
echo "  2. Query gold_lease_risk_scores view"
echo "  3. Open frontend Risk Assessment page"
echo "  4. Expand lease rows to see enrichment"
echo ""
echo "See README.md for verification queries"
echo ""
