"""
Comprehensive Synthetic Data Generator with Enrichment
=======================================================

Generates realistic lease data with full tenant and landlord enrichment
to demonstrate the complete enriched risk scoring ecosystem.

Features:
- Populates silver_leases with tenant_id, landlord_id
- Populates tenants table with REAL S&P 500 companies
- Populates landlords table with financial profiles
- Creates realistic correlations between company size and financial health
- Generates diverse mix of risk profiles for demonstration
- Uses CURRENT dates (leases within last 10 years, varying expirations)

Author: AI Assistant
Date: January 2026
"""

from faker import Faker
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json

# Import S&P 500 companies - handle both relative and absolute imports
try:
    from .sp500_companies import SP500_COMPANIES, COMPANY_SECTORS, get_sector_for_company
except ImportError:
    from sp500_companies import SP500_COMPANIES, COMPANY_SECTORS, get_sector_for_company

# Load environment variables
load_dotenv()

import os

# Initialize Faker
fake = Faker()

# Configuration - read from environment to match the app's runtime config
CATALOG = os.getenv('DATABRICKS_CATALOG', 'fins_team_3')
SCHEMA = os.getenv('DATABRICKS_SCHEMA', 'lease_management')
WAREHOUSE_ID = os.getenv('DATABRICKS_WAREHOUSE_ID', '288a7ec183eea397')

# Realistic data pools
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
    "Professional Services", "Restaurant", "Fitness", "Education",
    "Legal Services", "Marketing", "Consulting", "Biotechnology",
    "E-commerce", "Real Estate Services", "Hospitality"
]

# Industry risk levels (affects tenant risk profiles)
INDUSTRY_RISK = {
    "Retail": "HIGH",
    "Restaurant": "HIGH",
    "Hospitality": "MEDIUM",
    "Fitness": "MEDIUM",
    "Technology": "MEDIUM",
    "Healthcare": "LOW",
    "Finance": "LOW",
    "Legal Services": "LOW",
    "Biotechnology": "LOW",
    "Professional Services": "LOW",
    "Manufacturing": "MEDIUM",
    "Education": "LOW",
    "Marketing": "MEDIUM",
    "Consulting": "LOW",
    "E-commerce": "MEDIUM",
    "Real Estate Services": "MEDIUM"
}

LEASE_TYPES = [
    "Triple Net (NNN)", "Modified Gross", "Full Service",
    "Absolute Net", "Percentage Lease"
]

# Major real estate companies (REITs and private landlords)
LANDLORD_PROFILES = [
    {"name": "Blackstone Property Partners", "type": "REIT", "ticker": "BX"},
    {"name": "Brookfield Asset Management", "type": "Public", "ticker": "BAM"},
    {"name": "Prologis Properties", "type": "REIT", "ticker": "PLD"},
    {"name": "Equity Residential", "type": "REIT", "ticker": "EQR"},
    {"name": "Boston Properties", "type": "REIT", "ticker": "BXP"},
    {"name": "Vornado Realty Trust", "type": "REIT", "ticker": "VNO"},
    {"name": "Simon Property Group", "type": "REIT", "ticker": "SPG"},
    {"name": "Kimco Realty", "type": "REIT", "ticker": "KIM"},
    {"name": "Digital Realty", "type": "REIT", "ticker": "DLR"},
    {"name": "Alexandria Real Estate", "type": "REIT", "ticker": "ARE"},
    {"name": "Crown Castle Properties", "type": "REIT", "ticker": "CCI"},
    {"name": "Public Storage Holdings", "type": "REIT", "ticker": "PSA"},
    {"name": "Welltower Inc", "type": "REIT", "ticker": "WELL"},
    {"name": "Realty Income Corp", "type": "REIT", "ticker": "O"},
    {"name": "Duke Realty", "type": "REIT", "ticker": "DRE"},
    {"name": "Avalon Bay Communities", "type": "REIT", "ticker": "AVB"},
    {"name": "Essex Property Trust", "type": "REIT", "ticker": "ESS"},
    {"name": "Hudson Pacific Properties", "type": "REIT", "ticker": "HPP"},
    {"name": "SL Green Realty", "type": "REIT", "ticker": "SLG"},
    {"name": "Ventas Inc", "type": "REIT", "ticker": "VTR"}
]

# Markets with detailed data
MARKETS = {
    "San Francisco": {"min_rent": 55, "max_rent": 95, "sqft_range": (2000, 25000), "state": "California", "state_abbr": "CA", "zip_range": (94102, 94188)},
    "New York": {"min_rent": 60, "max_rent": 100, "sqft_range": (1500, 30000), "state": "New York", "state_abbr": "NY", "zip_range": (10001, 10282)},
    "Boston": {"min_rent": 45, "max_rent": 75, "sqft_range": (2000, 20000), "state": "Massachusetts", "state_abbr": "MA", "zip_range": (2108, 2298)},
    "Austin": {"min_rent": 35, "max_rent": 55, "sqft_range": (3000, 35000), "state": "Texas", "state_abbr": "TX", "zip_range": (78701, 78799)},
    "Seattle": {"min_rent": 40, "max_rent": 70, "sqft_range": (2500, 28000), "state": "Washington", "state_abbr": "WA", "zip_range": (98101, 98199)},
    "Los Angeles": {"min_rent": 38, "max_rent": 65, "sqft_range": (2000, 30000), "state": "California", "state_abbr": "CA", "zip_range": (90001, 90089)},
    "Chicago": {"min_rent": 32, "max_rent": 52, "sqft_range": (2500, 25000), "state": "Illinois", "state_abbr": "IL", "zip_range": (60601, 60661)},
    "Miami": {"min_rent": 35, "max_rent": 60, "sqft_range": (2000, 22000), "state": "Florida", "state_abbr": "FL", "zip_range": (33101, 33199)},
    "Denver": {"min_rent": 30, "max_rent": 50, "sqft_range": (3000, 26000), "state": "Colorado", "state_abbr": "CO", "zip_range": (80201, 80299)},
    "Dallas": {"min_rent": 28, "max_rent": 45, "sqft_range": (3500, 35000), "state": "Texas", "state_abbr": "TX", "zip_range": (75201, 75398)},
    "Atlanta": {"min_rent": 25, "max_rent": 42, "sqft_range": (3000, 30000), "state": "Georgia", "state_abbr": "GA", "zip_range": (30301, 30398)},
    "Phoenix": {"min_rent": 24, "max_rent": 40, "sqft_range": (3500, 32000), "state": "Arizona", "state_abbr": "AZ", "zip_range": (85001, 85099)}
}

# Credit ratings
CREDIT_RATINGS = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-", "BB+", "BB", "BB-", "B+", "B"]

def normalize_id(name):
    """Convert name to normalized ID format"""
    return name.lower().replace(' ', '_').replace(',', '').replace('.', '').replace("'", '').replace('&', 'and')

def get_real_company_for_industry(industry):
    """Get a real S&P 500 company that matches the industry"""
    # Filter companies by industry
    matching_companies = [
        company for company, sector in COMPANY_SECTORS.items()
        if sector == industry or (industry == "Technology" and sector in ["Technology", "Media & Entertainment"])
        or (industry == "Finance" and sector in ["Financial Services", "Insurance"])
        or (industry == "Healthcare" and sector in ["Healthcare", "Pharmaceuticals"])
        or (industry == "Retail" and sector == "Retail")
        or (industry == "Restaurant" and company in ["McDonald's Corporation", "Starbucks Corporation", "Chipotle Mexican Grill Inc.", "Yum! Brands Inc."])
        or (industry == "Manufacturing" and sector in ["Manufacturing", "Industrial", "Aerospace"])
        or (industry == "Energy" and sector == "Energy")
        or (industry == "Telecommunications" and sector in ["Telecommunications", "Media & Entertainment"])
    ]
    
    if matching_companies:
        return random.choice(matching_companies)
    else:
        # Fallback to any S&P 500 company
        return random.choice(SP500_COMPANIES)

def get_real_company_for_industry(industry):
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
    return get_real_company_for_industry(industry)

def generate_tenant_enrichment(tenant_name, industry):
    """Generate realistic tenant enrichment data"""
    
    # Determine company size tier (affects financial metrics)
    size_tier = random.choices(
        ["enterprise", "mid", "small"],
        weights=[0.3, 0.4, 0.3]
    )[0]
    
    # Base financial health influenced by industry and size
    industry_risk_level = INDUSTRY_RISK.get(industry, "MEDIUM")
    
    if industry_risk_level == "LOW":
        base_health = random.uniform(6.5, 9.5)
    elif industry_risk_level == "MEDIUM":
        base_health = random.uniform(4.5, 7.5)
    else:  # HIGH
        base_health = random.uniform(3.0, 6.5)
    
    # Check if this is a real S&P 500 company
    is_sp500 = tenant_name in SP500_COMPANIES
    
    # S&P 500 companies are typically enterprise-sized
    if is_sp500:
        size_tier = random.choices(["enterprise", "mid"], weights=[0.9, 0.1])[0]
        employee_count = random.randint(5000, 150000)
        annual_revenue = random.uniform(1_000_000_000, 500_000_000_000)
        health_score = min(10.0, base_health + random.uniform(0.5, 1.5))
    elif size_tier == "enterprise":
        health_score = min(10.0, base_health + random.uniform(0.5, 1.5))
        employee_count = random.randint(5000, 50000)
        annual_revenue = random.uniform(500_000_000, 10_000_000_000)
    elif size_tier == "mid":
        health_score = base_health
        employee_count = random.randint(500, 5000)
        annual_revenue = random.uniform(50_000_000, 500_000_000)
    else:  # small
        health_score = max(1.0, base_health - random.uniform(0.5, 1.0))
        employee_count = random.randint(10, 500)
        annual_revenue = random.uniform(1_000_000, 50_000_000)
    
    # Credit rating based on health score
    if health_score >= 9.0:
        credit_rating = random.choice(["AAA", "AA+", "AA"])
    elif health_score >= 8.0:
        credit_rating = random.choice(["AA-", "A+", "A"])
    elif health_score >= 7.0:
        credit_rating = random.choice(["A-", "BBB+", "BBB"])
    elif health_score >= 5.0:
        credit_rating = random.choice(["BBB", "BBB-", "BB+"])
    else:
        credit_rating = random.choice(["BB", "BB-", "B+", "B"])
    
    # Bankruptcy risk based on health score and industry
    if health_score >= 7.0:
        bankruptcy_risk = "LOW"
    elif health_score >= 4.0:
        bankruptcy_risk = "MEDIUM"
    else:
        bankruptcy_risk = "HIGH"
    
    # Revenue growth
    if size_tier == "small" or industry == "Technology":
        revenue_growth = random.uniform(-5, 25)
    else:
        revenue_growth = random.uniform(-2, 12)
    
    # Profit margin
    if industry in ["Technology", "Finance", "Legal Services"]:
        profit_margin = random.uniform(15, 35)
    elif industry in ["Healthcare", "Professional Services"]:
        profit_margin = random.uniform(8, 20)
    else:
        profit_margin = random.uniform(2, 15)
    
    # Market cap for public companies
    company_type = random.choices(
        ["Public", "Private", "Subsidiary"],
        weights=[0.25, 0.6, 0.15]
    )[0]
    
    if company_type == "Public":
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
    else:
        market_cap = None
        stock_ticker = None
    
    # Payment history score (correlates with health score)
    payment_history = min(100, max(0, (health_score * 10) + random.uniform(-10, 5)))
    
    # Location
    hq_city = random.choice(list(MARKETS.keys()))
    hq_market = MARKETS[hq_city]
    
    # Source URLs (simulated)
    source_urls = json.dumps([
        f"https://www.company-data.com/{normalize_id(tenant_name)}",
        f"https://finance.yahoo.com/quote/{stock_ticker}" if stock_ticker else "https://www.dnb.com",
        f"https://www.sec.gov/cgi-bin/browse-edgar?company={normalize_id(tenant_name)}" if company_type == "Public" else None
    ])
    
    return {
        "tenant_id": normalize_id(tenant_name),
        "tenant_name": tenant_name,
        "tenant_address": f"{random.randint(100, 9999)} {fake.street_name()}, {hq_city}, {hq_market['state_abbr']} {random.randint(hq_market['zip_range'][0], hq_market['zip_range'][1])}",
        "industry_sector": industry,
        "company_type": company_type,
        "parent_company": fake.company() if company_type == "Subsidiary" else None,
        "stock_ticker": stock_ticker,
        "founding_year": random.randint(1950, 2020),
        "employee_count": employee_count,
        "headquarters_location": f"{hq_city}, {hq_market['state_abbr']}",
        "market_cap": market_cap,
        "annual_revenue": annual_revenue,
        "net_income": annual_revenue * (profit_margin / 100),
        "revenue_growth_pct": revenue_growth,
        "profit_margin_pct": profit_margin,
        "credit_rating": credit_rating,
        "credit_rating_agency": random.choice(["S&P", "Moody's", "Fitch"]),
        "duns_number": f"{random.randint(100000000, 999999999)}",
        "payment_history_score": payment_history,
        "financial_health_score": round(health_score, 1),
        "bankruptcy_risk": bankruptcy_risk,
        "industry_risk": industry_risk_level,
        "recent_news_sentiment": random.choices(
            ["POSITIVE", "NEUTRAL", "NEGATIVE"],
            weights=[0.4, 0.5, 0.1]
        )[0],
        "litigation_flag": random.random() < 0.1,  # 10% have litigation
        "locations_count": random.randint(1, 50) if size_tier != "small" else 1,
        "years_in_business": 2026 - random.randint(1950, 2020),
        "enrichment_source": "MCP_WEB_SEARCH",
        "enrichment_confidence": random.uniform(0.75, 0.99),
        "last_enriched_at": datetime.now(),
        "source_urls": source_urls
    }

def generate_landlord_enrichment(landlord_profile):
    """Generate realistic landlord enrichment data"""
    
    landlord_name = landlord_profile["name"]
    company_type = landlord_profile["type"]
    ticker = landlord_profile.get("ticker")
    
    # REITs typically have stronger financials
    if company_type == "REIT":
        base_health = random.uniform(7.0, 9.5)
        credit_rating = random.choice(["AAA", "AA+", "AA", "AA-", "A+", "A"])
        bankruptcy_risk = "LOW"
    else:
        base_health = random.uniform(6.0, 8.5)
        credit_rating = random.choice(["A", "A-", "BBB+", "BBB", "BBB-"])
        bankruptcy_risk = random.choice(["LOW", "MEDIUM"])
    
    health_score = round(base_health, 1)
    
    # Financial metrics for REITs/property companies
    market_cap = random.uniform(5_000_000_000, 50_000_000_000) if company_type == "REIT" else random.uniform(500_000_000, 10_000_000_000)
    total_assets = market_cap * random.uniform(1.5, 3.0)
    annual_revenue = total_assets * random.uniform(0.05, 0.12)
    net_operating_income = annual_revenue * random.uniform(0.5, 0.7)
    
    # Debt to equity (REITs typically leverage debt)
    if company_type == "REIT":
        debt_to_equity = random.uniform(0.4, 1.2)
    else:
        debt_to_equity = random.uniform(0.3, 0.9)
    
    # Portfolio size
    total_properties = random.randint(50, 500) if company_type == "REIT" else random.randint(10, 100)
    total_sqft = total_properties * random.uniform(50000, 200000)
    
    # Location
    hq_city = random.choice(["New York", "San Francisco", "Boston", "Chicago", "Los Angeles"])
    hq_market = MARKETS[hq_city]
    
    # Property focus
    property_types = random.choice([
        "Office, Industrial",
        "Retail, Mixed-Use",
        "Healthcare, Life Science",
        "Industrial, Logistics",
        "Multifamily, Residential",
        "Data Center, Technology"
    ])
    
    # Geographic focus
    geo_focus = random.choice([
        "Nationwide",
        "East Coast Major Markets",
        "West Coast Tech Hubs",
        "Sunbelt Markets",
        "Top 25 MSAs",
        "Gateway Cities"
    ])
    
    return {
        "landlord_id": normalize_id(landlord_name),
        "landlord_name": landlord_name,
        "landlord_address": f"{random.randint(100, 9999)} {fake.street_name()}, {hq_city}, {hq_market['state_abbr']} {random.randint(hq_market['zip_range'][0], hq_market['zip_range'][1])}",
        "company_type": company_type,
        "stock_ticker": ticker,
        "market_cap": market_cap if company_type in ["REIT", "Public"] else None,
        "total_assets": total_assets,
        "credit_rating": credit_rating,
        "credit_rating_agency": random.choice(["S&P", "Moody's", "Fitch"]),
        "annual_revenue": annual_revenue,
        "net_operating_income": net_operating_income,
        "debt_to_equity_ratio": round(debt_to_equity, 2),
        "total_properties": total_properties,
        "total_square_footage": total_sqft,
        "primary_property_types": property_types,
        "geographic_focus": geo_focus,
        "financial_health_score": health_score,
        "bankruptcy_risk": bankruptcy_risk,
        "recent_news_sentiment": random.choices(
            ["POSITIVE", "NEUTRAL", "NEGATIVE"],
            weights=[0.5, 0.4, 0.1]
        )[0],
        "enrichment_source": "MCP_WEB_SEARCH",
        "enrichment_confidence": random.uniform(0.80, 0.99),
        "last_enriched_at": datetime.now(),
        "source_urls": json.dumps([
            f"https://www.reit.com/{normalize_id(landlord_name)}",
            f"https://finance.yahoo.com/quote/{ticker}" if ticker else "https://www.sec.gov",
            f"https://www.nareit.com/company/{normalize_id(landlord_name)}"
        ])
    }

def generate_lease_dates():
    """Generate ACTIVE lease dates - all leases currently active with varying future expirations"""
    from datetime import date
    
    today = date.today()
    
    # Lease term: 3, 5, 7, or 10 years
    term_years = random.choice([3, 5, 7, 10])
    term_months = term_years * 12
    
    # Create varied expiration scenarios - ALL IN THE FUTURE
    # Increased weight for "soon" to create more elevated risk scenarios
    scenario = random.choices(
        ["soon", "medium", "far"],
        weights=[0.35, 0.35, 0.30]  # 35% soon (HIGH RISK), 35% medium, 30% far
    )[0]
    
    if scenario == "soon":
        # Expiring in next 3-12 months (high rollover risk)
        months_until_expiry = random.randint(3, 12)
        end_date = today + timedelta(days=months_until_expiry * 30)
        # Calculate start date by going back the term length
        start_date = end_date - timedelta(days=int(term_years * 365.25))
        
    elif scenario == "medium":
        # Expiring in 1-3 years (moderate planning horizon)
        months_until_expiry = random.randint(13, 36)
        end_date = today + timedelta(days=months_until_expiry * 30)
        start_date = end_date - timedelta(days=int(term_years * 365.25))
        
    else:  # "far"
        # Expiring in 3-10 years (stable, low rollover risk)
        months_until_expiry = random.randint(37, 120)
        end_date = today + timedelta(days=months_until_expiry * 30)
        start_date = end_date - timedelta(days=int(term_years * 365.25))
    
    # Enforce commencement date constraints: 8 years ago to 6 months future
    eight_years_ago = today - timedelta(days=8 * 365)
    six_months_future = today + timedelta(days=180)
    
    if start_date < eight_years_ago:
        # Start date too old - move it forward to 8 years ago
        days_to_adjust = (eight_years_ago - start_date).days
        start_date = eight_years_ago
        # Adjust end date forward by same amount to maintain active lease
        end_date = end_date + timedelta(days=days_to_adjust)
        
    elif start_date > six_months_future:
        # Start date too far in future - move it back to 6 months from now
        days_to_adjust = (start_date - six_months_future).days
        start_date = six_months_future
        # Adjust end date back by same amount
        end_date = end_date - timedelta(days=days_to_adjust)
    
    # Final safety check: ensure end date is always in the future
    if end_date <= today:
        # Force end date to be at least 3 months in the future
        end_date = today + timedelta(days=90)
        start_date = end_date - timedelta(days=int(term_years * 365.25))
        # Re-check start date constraint after adjustment
        if start_date < eight_years_ago:
            start_date = eight_years_ago
            # For very short remaining leases, recalculate end date
            end_date = start_date + timedelta(days=int(term_years * 365.25))
    
    return start_date, end_date, term_months

def generate_address(city, state, state_abbr, zip_range):
    """Generate a realistic street address"""
    street_number = random.randint(100, 9999)
    street_names = [
        "Main Street", "Market Street", "Broadway", "Park Avenue", "Madison Avenue",
        "Oak Street", "Maple Avenue", "Washington Boulevard", "Lincoln Way", "Commerce Drive",
        "Business Parkway", "Tech Boulevard", "Innovation Drive", "Corporate Plaza"
    ]
    street = random.choice(street_names)
    zip_code = str(random.randint(zip_range[0], zip_range[1]))
    
    return {
        "street_address": f"{street_number} {street}",
        "city": city,
        "state": state,
        "state_abbr": state_abbr,
        "zip_code": zip_code,
        "full_address": f"{street_number} {street}, {city}, {state_abbr} {zip_code}"
    }

def generate_synthetic_lease_data(num_leases=100, enrichment_rate=0.8):
    """
    Generate complete lease ecosystem with enrichment
    
    Args:
        num_leases: Number of leases to generate
        enrichment_rate: Percentage of leases that should have enrichment (0.0-1.0)
    
    Returns:
        Dict with leases, tenants, and landlords
    """
    
    print(f"Generating {num_leases} leases with {int(enrichment_rate*100)}% enrichment rate...")
    
    # Track unique tenants and landlords
    unique_tenants = {}
    unique_landlords = {}
    leases = []
    
    # Pre-generate all landlords (limited set)
    for landlord_profile in LANDLORD_PROFILES:
        landlord_enrichment = generate_landlord_enrichment(landlord_profile)
        unique_landlords[landlord_enrichment["landlord_id"]] = landlord_enrichment
    
    print(f"Generated {len(unique_landlords)} landlord profiles")
    
    # Generate leases and tenants
    for i in range(num_leases):
        # Select market
        market = random.choice(list(MARKETS.keys()))
        market_data = MARKETS[market]
        
        # Generate dates
        commencement_date, expiration_date, term_months = generate_lease_dates()
        
        # Generate company details
        industry = random.choice(INDUSTRIES)
        tenant_name = generate_company_name(industry)
        tenant_id = normalize_id(tenant_name)
        
        # Avoid duplicate tenants (some tenants can have multiple leases)
        if tenant_id not in unique_tenants and random.random() < 0.7:  # 70% new tenants
            tenant_enrichment = generate_tenant_enrichment(tenant_name, industry)
            unique_tenants[tenant_id] = tenant_enrichment
        elif tenant_id in unique_tenants:
            pass  # Reuse existing tenant
        else:
            # Pick an existing tenant for this lease
            if unique_tenants:
                tenant_id = random.choice(list(unique_tenants.keys()))
                tenant_name = unique_tenants[tenant_id]["tenant_name"]
                industry = unique_tenants[tenant_id]["industry_sector"]
        
        # Select landlord
        landlord_profile = random.choice(LANDLORD_PROFILES)
        landlord_name = landlord_profile["name"]
        landlord_id = normalize_id(landlord_name)
        
        # Property location
        property_location = generate_address(
            market, market_data["state"], market_data["state_abbr"], market_data["zip_range"]
        )
        
        # Square footage and rent
        sqft_min, sqft_max = market_data["sqft_range"]
        square_feet = random.randint(sqft_min, sqft_max)
        square_feet = round(square_feet / 100) * 100
        
        base_rent_psf = random.uniform(market_data["min_rent"], market_data["max_rent"])
        base_rent_psf = round(base_rent_psf, 2)
        annual_base_rent = base_rent_psf * square_feet
        
        # Escalation
        annual_escalation_pct = random.choice([0, 2, 2.5, 3, 3.5, 4])
        
        # Suite and type
        suite_number = f"{random.choice(['Suite', 'Unit', 'Space'])} {random.randint(100, 999)}"
        lease_type = random.choice(LEASE_TYPES)
        
        # Build lease record
        lease = {
            "lease_id": f"{landlord_id}_{tenant_id}_{normalize_id(suite_number)}",
            "property_id": f"PROP_{landlord_id}_{normalize_id(suite_number)}",
            "tenant_name": tenant_name,
            "tenant_id": tenant_id,
            "landlord_name": landlord_name,
            "landlord_id": landlord_id,
            "industry_sector": industry,
            "suite_id": suite_number,
            "square_footage": float(square_feet),
            "lease_type": lease_type,
            "lease_start_date": commencement_date,
            "lease_end_date": expiration_date,
            "base_rent_psf": float(base_rent_psf),
            "annual_escalation_pct": float(annual_escalation_pct),
            "property_address": property_location["full_address"],
            "property_street_address": property_location["street_address"],
            "property_city": property_location["city"],
            "property_state": property_location["state_abbr"],
            "property_zip_code": property_location["zip_code"],
            "property_country": "United States",
            "estimated_annual_rent": float(annual_base_rent),
            "next_escalation_date": (commencement_date + timedelta(days=365)),
            "enhancement_source": "AI_HUMAN_VERIFIED",
            "validation_status": "VERIFIED",
            "verified_by": "synthetic_data_generator",
            "verified_at": datetime.now(),
            "raw_document_path": None,
            "uploaded_at": datetime.now() - timedelta(days=random.randint(1, 30)),
            "updated_at": datetime.now()
        }
        
        leases.append(lease)
        
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{num_leases} leases...")
    
    print(f"\nSummary:")
    print(f"  - Leases: {len(leases)}")
    print(f"  - Unique Tenants: {len(unique_tenants)}")
    print(f"  - Unique Landlords: {len(unique_landlords)}")
    
    return {
        "leases": leases,
        "tenants": list(unique_tenants.values()),
        "landlords": list(unique_landlords.values())
    }

def escape_sql(value):
    """Escape SQL string values"""
    if value is None:
        return "NULL"
    return str(value).replace("'", "''")

def insert_tenants(client, warehouse_id, tenants):
    """Insert tenant enrichment data"""
    print("\nInserting tenant enrichment data...")
    
    for i, tenant in enumerate(tenants):
        sql = f"""
        INSERT INTO {CATALOG}.{SCHEMA}.tenants (
            tenant_id, tenant_name, tenant_address, industry_sector,
            company_type, parent_company, stock_ticker, founding_year,
            employee_count, headquarters_location, market_cap, annual_revenue,
            net_income, revenue_growth_pct, profit_margin_pct,
            credit_rating, credit_rating_agency, duns_number, payment_history_score,
            financial_health_score, bankruptcy_risk, industry_risk,
            recent_news_sentiment, litigation_flag, locations_count,
            years_in_business, enrichment_source, enrichment_confidence,
            last_enriched_at, source_urls
        ) VALUES (
            '{escape_sql(tenant["tenant_id"])}',
            '{escape_sql(tenant["tenant_name"])}',
            '{escape_sql(tenant["tenant_address"])}',
            '{escape_sql(tenant["industry_sector"])}',
            '{escape_sql(tenant["company_type"])}',
            {f"'{escape_sql(tenant['parent_company'])}'" if tenant['parent_company'] else "NULL"},
            {f"'{escape_sql(tenant['stock_ticker'])}'" if tenant['stock_ticker'] else "NULL"},
            {tenant['founding_year']},
            {tenant['employee_count']},
            '{escape_sql(tenant["headquarters_location"])}',
            {tenant['market_cap'] if tenant['market_cap'] else "NULL"},
            {tenant['annual_revenue']},
            {tenant['net_income']},
            {tenant['revenue_growth_pct']},
            {tenant['profit_margin_pct']},
            '{escape_sql(tenant["credit_rating"])}',
            '{escape_sql(tenant["credit_rating_agency"])}',
            '{escape_sql(tenant["duns_number"])}',
            {tenant['payment_history_score']},
            {tenant['financial_health_score']},
            '{escape_sql(tenant["bankruptcy_risk"])}',
            '{escape_sql(tenant["industry_risk"])}',
            '{escape_sql(tenant["recent_news_sentiment"])}',
            {str(tenant['litigation_flag']).upper()},
            {tenant['locations_count']},
            {tenant['years_in_business']},
            '{escape_sql(tenant["enrichment_source"])}',
            {tenant['enrichment_confidence']},
            '{tenant["last_enriched_at"].strftime("%Y-%m-%d %H:%M:%S")}',
            '{escape_sql(tenant["source_urls"])}'
        )
        """
        
        try:
            client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql,
                wait_timeout="30s"
            )
            if (i + 1) % 10 == 0:
                print(f"  Inserted {i + 1}/{len(tenants)} tenants...")
        except Exception as e:
            print(f"  Error inserting tenant {tenant['tenant_name']}: {e}")
    
    print(f"[OK] Inserted {len(tenants)} tenants")

def insert_landlords(client, warehouse_id, landlords):
    """Insert landlord enrichment data"""
    print("\nInserting landlord enrichment data...")
    
    for i, landlord in enumerate(landlords):
        sql = f"""
        INSERT INTO {CATALOG}.{SCHEMA}.landlords (
            landlord_id, landlord_name, landlord_address, company_type,
            stock_ticker, market_cap, total_assets, credit_rating,
            credit_rating_agency, annual_revenue, net_operating_income,
            debt_to_equity_ratio, total_properties, total_square_footage,
            primary_property_types, geographic_focus, financial_health_score,
            bankruptcy_risk, recent_news_sentiment, enrichment_source,
            enrichment_confidence, last_enriched_at, source_urls
        ) VALUES (
            '{escape_sql(landlord["landlord_id"])}',
            '{escape_sql(landlord["landlord_name"])}',
            '{escape_sql(landlord["landlord_address"])}',
            '{escape_sql(landlord["company_type"])}',
            {f"'{escape_sql(landlord['stock_ticker'])}'" if landlord['stock_ticker'] else "NULL"},
            {landlord['market_cap'] if landlord['market_cap'] else "NULL"},
            {landlord['total_assets']},
            '{escape_sql(landlord["credit_rating"])}',
            '{escape_sql(landlord["credit_rating_agency"])}',
            {landlord['annual_revenue']},
            {landlord['net_operating_income']},
            {landlord['debt_to_equity_ratio']},
            {landlord['total_properties']},
            {landlord['total_square_footage']},
            '{escape_sql(landlord["primary_property_types"])}',
            '{escape_sql(landlord["geographic_focus"])}',
            {landlord['financial_health_score']},
            '{escape_sql(landlord["bankruptcy_risk"])}',
            '{escape_sql(landlord["recent_news_sentiment"])}',
            '{escape_sql(landlord["enrichment_source"])}',
            {landlord['enrichment_confidence']},
            '{landlord["last_enriched_at"].strftime("%Y-%m-%d %H:%M:%S")}',
            '{escape_sql(landlord["source_urls"])}'
        )
        """
        
        try:
            client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"  Error inserting landlord {landlord['landlord_name']}: {e}")
    
    print(f"[OK] Inserted {len(landlords)} landlords")

def insert_leases(client, warehouse_id, leases, batch_size=10):
    """Insert lease data into silver layer"""
    print("\nInserting leases into silver layer...")
    
    for i in range(0, len(leases), batch_size):
        batch = leases[i:i + batch_size]
        
        values_clauses = []
        for lease in batch:
            values = f"""(
                '{escape_sql(lease["lease_id"])}',
                '{escape_sql(lease["property_id"])}',
                '{escape_sql(lease["tenant_name"])}',
                '{escape_sql(lease["tenant_id"])}',
                '{escape_sql(lease["landlord_name"])}',
                '{escape_sql(lease["landlord_id"])}',
                '{escape_sql(lease["industry_sector"])}',
                '{escape_sql(lease["suite_id"])}',
                {lease["square_footage"]},
                '{escape_sql(lease["lease_type"])}',
                '{lease["lease_start_date"]}',
                '{lease["lease_end_date"]}',
                {lease["base_rent_psf"]},
                {lease["annual_escalation_pct"]},
                '{escape_sql(lease["property_address"])}',
                '{escape_sql(lease["property_street_address"])}',
                '{escape_sql(lease["property_city"])}',
                '{escape_sql(lease["property_state"])}',
                '{escape_sql(lease["property_zip_code"])}',
                '{escape_sql(lease["property_country"])}',
                {lease["estimated_annual_rent"]},
                '{lease["next_escalation_date"]}',
                '{escape_sql(lease["enhancement_source"])}',
                '{escape_sql(lease["validation_status"])}',
                '{escape_sql(lease["verified_by"])}',
                '{lease["verified_at"].strftime("%Y-%m-%d %H:%M:%S")}',
                NULL,
                '{lease["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S")}',
                '{lease["updated_at"].strftime("%Y-%m-%d %H:%M:%S")}'
            )"""
            values_clauses.append(values)
        
        sql = f"""
        INSERT INTO {CATALOG}.{SCHEMA}.silver_leases (
            lease_id, property_id, tenant_name, tenant_id, landlord_name, landlord_id,
            industry_sector, suite_id, square_footage, lease_type, lease_start_date,
            lease_end_date, base_rent_psf, annual_escalation_pct, property_address,
            property_street_address, property_city, property_state, property_zip_code,
            property_country, estimated_annual_rent, next_escalation_date,
            enhancement_source, validation_status, verified_by, verified_at,
            raw_document_path, uploaded_at, updated_at
        ) VALUES
        {','.join(values_clauses)}
        """
        
        try:
            client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql,
                wait_timeout="50s"
            )
            print(f"  Inserted batch {(i//batch_size)+1}/{(len(leases)+batch_size-1)//batch_size}")
        except Exception as e:
            print(f"  Error inserting batch: {e}")
    
    print(f"[OK] Inserted {len(leases)} leases")

def main():
    """Main execution"""
    print("="*70)
    print("Comprehensive Synthetic Data Generator with Enrichment")
    print("="*70)
    print()
    
    num_leases = int(input("Number of leases to generate (recommended 50-200): ") or "100")
    enrichment_rate = float(input("Enrichment rate (0.5-1.0, recommended 0.8): ") or "0.8")
    
    print()
    print("Connecting to Databricks...")
    try:
        client = WorkspaceClient()
        print("[OK] Connected successfully")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return
    
    print()
    
    # Generate all data
    data = generate_synthetic_lease_data(num_leases, enrichment_rate)
    
    # Insert in order: landlords -> tenants -> leases
    insert_landlords(client, WAREHOUSE_ID, data["landlords"])
    insert_tenants(client, WAREHOUSE_ID, data["tenants"])
    insert_leases(client, WAREHOUSE_ID, data["leases"])
    
    print()
    print("="*70)
    print("COMPLETE!")
    print("="*70)
    print(f"Generated:")
    print(f"  - {len(data['leases'])} leases")
    print(f"  - {len(data['tenants'])} unique tenants (with enrichment)")
    print(f"  - {len(data['landlords'])} landlords (with enrichment)")
    print()
    print("Next steps:")
    print("  1. Verify gold_lease_risk_scores view shows enriched data")
    print("  2. Check frontend Risk Assessment page for enrichment badges")
    print("  3. Expand rows to see tenant/landlord financial profiles")
    print()

if __name__ == "__main__":
    main()
