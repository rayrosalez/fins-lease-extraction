#!/bin/bash
# Quick setup and generation script for lease PDFs

echo "=================================================="
echo "Commercial Lease Generator - Quick Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "generate_leases.py" ]; then
    echo "❌ Error: Please run this script from the LeaseGeneration directory"
    exit 1
fi

# Check if reportlab is installed
python -c "import reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
    echo ""
fi

# Get number of leases to generate
if [ -z "$1" ]; then
    COUNT=10
else
    COUNT=$1
fi

echo "🏢 Generating $COUNT commercial lease agreements..."
echo ""

# Create a temporary Python script to generate specific count
cat > temp_generate.py << EOF
from generate_leases import LeaseGenerator

generator = LeaseGenerator()
generator.generate_multiple_leases(count=$COUNT)
EOF

# Run the generator
python temp_generate.py

# Clean up
rm temp_generate.py

echo ""
echo "=================================================="
echo "✓ Complete! PDFs are in generated_leases/"
echo "=================================================="
echo ""
echo "To generate more leases:"
echo "  ./quickstart.sh 25    # Generate 25 leases"
echo ""

