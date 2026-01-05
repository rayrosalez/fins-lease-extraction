#!/bin/bash

# Quick Start Script for Synthetic Data Generation
# =================================================

echo "=========================================="
echo "Synthetic Lease Data Generator Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "generate_and_promote.py" ]; then
    echo "❌ Error: generate_and_promote.py not found"
    echo "Please run this script from the DataGeneration directory"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo ""

if pip3 install -r requirements.txt; then
    echo ""
    echo "✅ Dependencies installed successfully"
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo "Try: pip3 install faker databricks-sdk python-dotenv"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has DATABRICKS_HOST and DATABRICKS_TOKEN"
echo "2. Update WAREHOUSE_ID in the scripts (if needed)"
echo "3. Run: python3 generate_and_promote.py"
echo ""
echo "This will generate data AND promote it to silver so it appears in the frontend!"
echo ""
echo "Or run it now? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "How many leases to generate? (recommended 50-200, default 100):"
    read -r num_leases
    num_leases=${num_leases:-100}
    
    echo ""
    echo "Starting complete data generation pipeline..."
    echo ""
    python3 generate_and_promote.py $num_leases
else
    echo ""
    echo "When you're ready, run:"
    echo "  python3 generate_and_promote.py 100"
    echo ""
fi

