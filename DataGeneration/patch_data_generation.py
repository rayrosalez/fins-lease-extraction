"""
Patch for generate_enriched_data.py to fix:
1. Use real S&P 500 companies
2. Fix lease dates to be current (max 10 years old)
3. Vary expiration dates (some soon, some far away)
"""

import sys
from pathlib import Path

# Read the current file
gen_data_path = Path(__file__).parent / 'generate_enriched_data.py'
with open(gen_data_path, 'r') as f:
    content = f.read()

# Fix 1: Update imports to include sp500_companies
import_fix = '''from faker import Faker
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json
import sys
from pathlib import Path

# Import S&P 500 companies
sp500_path = Path(__file__).parent.parent / 'LeaseGeneration'
sys.path.insert(0, str(sp500_path))
from sp500_companies import SP500_COMPANIES, COMPANY_SECTORS'''

old_imports = '''from faker import Faker
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json'''

content = content.replace(old_imports, import_fix)

# Fix 2: Update generate_company_name to use real S&P 500 companies
new_company_function = '''def get_real_company_for_industry(industry):
    """Get a real S&P 500 company that matches the industry"""
    matching_companies = [
        company for company, sector in COMPANY_SECTORS.items()
        if sector == industry or 
        (industry == "Technology" and sector in ["Technology", "Media & Entertainment"]) or
        (industry in ["Finance", "Financial Services"] and sector in ["Financial Services", "Insurance"]) or
        (industry == "Healthcare" and sector in ["Healthcare", "Pharmaceuticals"]) or
        (industry == "Retail" and sector == "Retail") or
        (industry == "Restaurant" and company in ["McDonald's Corporation", "Starbucks Corporation", "Chipotle Mexican Grill Inc.", "Yum! Brands Inc."]) or
        (industry == "Manufacturing" and sector in ["Manufacturing", "Industrial", "Aerospace"]) or
        (industry == "Energy" and sector == "Energy") or
        (industry == "Telecommunications" and sector in ["Telecommunications", "Media & Entertainment"])
    ]
    if matching_companies:
        return random.choice(matching_companies)
    return random.choice(SP500_COMPANIES)

def generate_company_name(industry):
    """Generate company name - now uses REAL S&P 500 companies"""
    return get_real_company_for_industry(industry)'''

# Find and replace the old function
start_marker = "def generate_company_name(industry):"
end_marker = "def generate_tenant_enrichment"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_company_function + "\n\n" + content[end_idx:]

# Fix 3: Update lease date generation to be current
new_date_function = '''def generate_lease_dates():
    """Generate CURRENT lease dates - leases from last 10 years with varying expirations"""
    from datetime import date
    
    today = date.today()
    
    # Start date: anywhere from 10 years ago to 2 years in the future
    years_offset = random.uniform(-10, 2)
    days_offset = int(years_offset * 365.25)
    start_date = today + timedelta(days=days_offset)
    
    # Lease term: 3, 5, 7, or 10 years
    term_years = random.choice([3, 5, 7, 10])
    term_months = term_years * 12
    
    # End date = start date + term
    end_date = start_date + timedelta(days=int(term_years * 365.25))
    
    # Create varied expiration scenarios:
    # - Some expiring soon (high rollover risk)
    # - Some expiring in medium term
    # - Some expiring far in future
    scenario = random.choices(
        ["soon", "medium", "far"],
        weights=[0.15, 0.35, 0.5]  # 15% soon, 35% medium, 50% far
    )[0]
    
    if scenario == "soon":
        # Expiring in next 0-12 months (high risk)
        months_until_expiry = random.randint(0, 12)
        end_date = today + timedelta(days=months_until_expiry * 30)
        # Backdate start
        start_date = end_date - timedelta(days=int(term_years * 365.25))
    elif scenario == "medium":
        # Expiring in 1-3 years (moderate risk)
        months_until_expiry = random.randint(12, 36)
        end_date = today + timedelta(days=months_until_expiry * 30)
        start_date = end_date - timedelta(days=int(term_years * 365.25))
    # else "far" - already calculated above
    
    # Ensure start date isn't too old (max 10 years)
    ten_years_ago = today - timedelta(days=3650)
    if start_date < ten_years_ago:
        start_date = ten_years_ago
        end_date = start_date + timedelta(days=int(term_years * 365.25))
    
    return start_date, end_date, term_months'''

# Find and replace the date function
date_start = content.find("def generate_lease_dates():")
if date_start != -1:
    # Find the end of this function (next def or class)
    next_def = content.find("\ndef ", date_start + 10)
    if next_def != -1:
        content = content[:date_start] + new_date_function + "\n" + content[next_def:]

# Fix 4: Update tenant enrichment to handle S&P 500 companies better
tenant_patch = '''    # Check if this is a real S&P 500 company
    is_sp500 = tenant_name in SP500_COMPANIES
    
    # S&P 500 companies are typically enterprise-sized
    if is_sp500:
        size_tier = random.choices(["enterprise", "mid"], weights=[0.9, 0.1])[0]
        employee_count = random.randint(5000, 150000)
        annual_revenue = random.uniform(1_000_000_000, 500_000_000_000)
        health_score = min(10.0, base_health + random.uniform(0.5, 1.5))
    elif size_tier == "enterprise":'''

old_tenant = '''    # Size adjustment
    if size_tier == "enterprise":'''

content = content.replace(old_tenant, tenant_patch)

# Fix 5: Update stock ticker generation for real companies
ticker_patch = '''    if company_type == "Public":
        if is_sp500:
            # Generate realistic ticker from company name
            words = tenant_name.upper().replace(',', '').replace('.', '').split()
            if len(words) == 1:
                ticker = words[0][:4]
            elif words[0] in ['THE', 'A', 'AN']:
                ticker = words[1][:4]
            else:
                ticker = ''.join([w[0] for w in words[:min(4, len(words))]])
            ticker = ticker[:5]
            stock_ticker = ticker
            market_cap = annual_revenue * random.uniform(2, 12)
        else:
            stock_ticker = f"{tenant_name[:3].upper()}{random.randint(10, 99)}"
            market_cap = annual_revenue * random.uniform(2, 8)
    else:'''

old_ticker = '''    if company_type == "Public":
        market_cap = annual_revenue * random.uniform(2, 8)
        stock_ticker = f"{tenant_name[:3].upper()}{random.randint(10, 99)}"
    else:'''

content = content.replace(old_ticker, ticker_patch)

# Write the updated file
with open(gen_data_path, 'w') as f:
    f.write(content)

print("✅ Patched generate_enriched_data.py successfully!")
print("   - Added S&P 500 company imports")
print("   - Updated company name generation to use real companies")
print("   - Fixed lease dates to be current (max 10 years old)")
print("   - Added varied expiration dates (15% soon, 35% medium, 50% far)")
print("   - Enhanced tenant enrichment for S&P 500 companies")
print("   - Improved stock ticker generation")
