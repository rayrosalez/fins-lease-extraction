#!/bin/bash

# Quick Test Script - Generate Sample Data for Frontend Testing
# ==============================================================

echo "🚀 Quick Test: Generating 50 sample leases for frontend testing"
echo ""

# Check if we're in the right directory
if [ ! -f "generate_and_promote.py" ]; then
    echo "❌ Error: Must run from DataGeneration directory"
    exit 1
fi

# Check if .env exists
if [ ! -f "../FrontEndV2/backend/.env" ] && [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Make sure DATABRICKS_HOST and DATABRICKS_TOKEN are set"
    echo ""
fi

echo "This will:"
echo "  1. Generate 50 synthetic leases"
echo "  2. Insert into bronze_leases table"
echo "  3. Promote VERIFIED records to silver_leases"
echo "  4. Your frontend will immediately show the data"
echo ""
echo "Continue? (y/n)"
read -r response

if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Starting quick test..."
echo ""

# Run the all-in-one script with 50 leases
python3 generate_and_promote.py 50

echo ""
echo "✅ Quick test complete!"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 (if not already open)"
echo "  2. Check the dashboard - you should see 50 leases"
echo "  3. Verify the map shows property locations"
echo "  4. Check portfolio KPIs update"
echo ""
echo "To generate more data, run:"
echo "  python3 generate_and_promote.py 100"
echo ""

