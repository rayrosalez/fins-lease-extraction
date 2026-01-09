#!/bin/bash

# Setup Helper for Databricks Authentication
# ==========================================

echo "========================================"
echo "Databricks Authentication Setup"
echo "========================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "✓ .env file already exists"
    echo ""
    echo "Current configuration:"
    grep -v "TOKEN" .env 2>/dev/null | head -1
    echo "DATABRICKS_TOKEN=***hidden***"
    echo ""
    read -p "Do you want to update it? (y/n): " update
    if [ "$update" != "y" ]; then
        echo "Keeping existing configuration"
        exit 0
    fi
    echo ""
fi

echo "You need two pieces of information from Databricks:"
echo ""
echo "1. DATABRICKS_HOST"
echo "   - Go to your Databricks workspace"
echo "   - Copy the URL from your browser"
echo "   - Example: https://dbc-abc12345-def6.cloud.databricks.com"
echo ""
echo "2. DATABRICKS_TOKEN (Personal Access Token)"
echo "   - In Databricks: Click your username (top right)"
echo "   - Settings → Developer → Access Tokens"
echo "   - Click 'Generate New Token'"
echo "   - Give it a name like 'Data Generator'"
echo "   - Set lifetime (recommend 90 days)"
echo "   - Copy the token (you won't see it again!)"
echo ""
echo "========================================"
echo ""

# Get host
read -p "Enter DATABRICKS_HOST: " db_host

# Validate host format
if [[ ! $db_host =~ ^https:// ]]; then
    echo ""
    echo "⚠️  Warning: Host should start with https://"
    echo "   Adding https:// prefix..."
    db_host="https://$db_host"
fi

echo ""

# Get token
read -sp "Enter DATABRICKS_TOKEN (hidden): " db_token
echo ""
echo ""

# Validate token is not empty
if [ -z "$db_token" ]; then
    echo "❌ Error: Token cannot be empty"
    exit 1
fi

# Create .env file
cat > .env << EOF
# Databricks Configuration
# Generated: $(date)

DATABRICKS_HOST=$db_host
DATABRICKS_TOKEN=$db_token
EOF

echo "✓ .env file created successfully!"
echo ""

# Test connection
echo "Testing connection..."
python3 -c "
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
load_dotenv()
try:
    client = WorkspaceClient()
    print('✓ Connection successful!')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('')
    print('Common issues:')
    print('  - Wrong host URL')
    print('  - Expired or invalid token')
    print('  - Network/firewall blocking connection')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Setup Complete!"
    echo "========================================"
    echo ""
    echo "You can now run:"
    echo "  python generate_enriched_data.py"
    echo ""
else
    echo ""
    echo "Please check your credentials and try again"
    echo "Run: ./setup_auth.sh"
fi
