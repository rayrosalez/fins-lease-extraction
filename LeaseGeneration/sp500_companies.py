#!/usr/bin/env python3
"""
S&P 500 Company names for realistic lease generation
Source: S&P 500 constituent companies
"""

# S&P 500 companies across various sectors
SP500_COMPANIES = [
    # Technology
    "Apple Inc.", "Microsoft Corporation", "NVIDIA Corporation", "Amazon.com Inc.",
    "Meta Platforms Inc.", "Alphabet Inc.", "Tesla Inc.", "Broadcom Inc.",
    "Oracle Corporation", "Adobe Inc.", "Salesforce Inc.", "Cisco Systems Inc.",
    "Advanced Micro Devices Inc.", "Qualcomm Inc.", "Intel Corporation",
    "Texas Instruments Inc.", "Applied Materials Inc.", "ServiceNow Inc.",
    "Intuit Inc.", "PayPal Holdings Inc.", "Block Inc.", "Workday Inc.",
    "Palo Alto Networks Inc.", "Snowflake Inc.", "Fortinet Inc.", "Synopsys Inc.",
    
    # Financial Services
    "JPMorgan Chase & Co.", "Bank of America Corporation", "Wells Fargo & Company",
    "Morgan Stanley", "Goldman Sachs Group Inc.", "Citigroup Inc.",
    "American Express Company", "BlackRock Inc.", "Charles Schwab Corporation",
    "S&P Global Inc.", "CME Group Inc.", "Moody's Corporation",
    "Capital One Financial Corporation", "PNC Financial Services Group Inc.",
    "U.S. Bancorp", "Truist Financial Corporation", "Bank of New York Mellon Corporation",
    "State Street Corporation", "Intercontinental Exchange Inc.", "MarketAxess Holdings Inc.",
    
    # Healthcare & Pharmaceuticals
    "UnitedHealth Group Inc.", "Johnson & Johnson", "Eli Lilly and Company",
    "Merck & Co. Inc.", "AbbVie Inc.", "Pfizer Inc.", "Abbott Laboratories",
    "Bristol-Myers Squibb Company", "Thermo Fisher Scientific Inc.", "Danaher Corporation",
    "Cigna Group", "CVS Health Corporation", "Elevance Health Inc.",
    "Intuitive Surgical Inc.", "Stryker Corporation", "Vertex Pharmaceuticals Inc.",
    "Regeneron Pharmaceuticals Inc.", "Amgen Inc.", "Gilead Sciences Inc.",
    "Moderna Inc.", "Humana Inc.", "Centene Corporation", "HCA Healthcare Inc.",
    
    # Consumer Discretionary & Retail
    "Walmart Inc.", "The Home Depot Inc.", "Costco Wholesale Corporation",
    "McDonald's Corporation", "Nike Inc.", "Starbucks Corporation",
    "Lowe's Companies Inc.", "Target Corporation", "The TJX Companies Inc.",
    "Booking Holdings Inc.", "Marriott International Inc.", "Ross Stores Inc.",
    "Dollar General Corporation", "AutoZone Inc.", "O'Reilly Automotive Inc.",
    "Chipotle Mexican Grill Inc.", "Yum! Brands Inc.", "Best Buy Co. Inc.",
    "Ulta Beauty Inc.", "Hilton Worldwide Holdings Inc.", "Expedia Group Inc.",
    
    # Industrial & Manufacturing
    "Honeywell International Inc.", "General Electric Company", "Caterpillar Inc.",
    "3M Company", "Lockheed Martin Corporation", "Raytheon Technologies Corporation",
    "Boeing Company", "Union Pacific Corporation", "United Parcel Service Inc.",
    "Deere & Company", "General Dynamics Corporation", "Northrop Grumman Corporation",
    "Illinois Tool Works Inc.", "Emerson Electric Co.", "Eaton Corporation plc",
    "Parker-Hannifin Corporation", "Rockwell Automation Inc.", "Carrier Global Corporation",
    "Otis Worldwide Corporation", "Ingersoll Rand Inc.", "Trane Technologies plc",
    
    # Energy
    "ExxonMobil Corporation", "Chevron Corporation", "ConocoPhillips",
    "EOG Resources Inc.", "Marathon Petroleum Corporation", "Phillips 66",
    "Schlumberger Limited", "Valero Energy Corporation", "Williams Companies Inc.",
    "Kinder Morgan Inc.", "Occidental Petroleum Corporation", "Baker Hughes Company",
    "Halliburton Company", "Pioneer Natural Resources Company", "Devon Energy Corporation",
    
    # Consumer Staples
    "Procter & Gamble Company", "Coca-Cola Company", "PepsiCo Inc.",
    "Philip Morris International Inc.", "Altria Group Inc.", "Mondelez International Inc.",
    "Colgate-Palmolive Company", "General Mills Inc.", "Kellogg Company",
    "Kraft Heinz Company", "Estée Lauder Companies Inc.", "Kimberly-Clark Corporation",
    "Church & Dwight Co. Inc.", "Conagra Brands Inc.", "The Hershey Company",
    
    # Telecommunications & Media
    "Verizon Communications Inc.", "AT&T Inc.", "T-Mobile US Inc.",
    "Comcast Corporation", "Charter Communications Inc.", "Walt Disney Company",
    "Netflix Inc.", "Warner Bros. Discovery Inc.", "Paramount Global",
    "Fox Corporation", "Omnicom Group Inc.", "Interpublic Group of Companies Inc.",
    
    # Real Estate
    "American Tower Corporation", "Prologis Inc.", "Crown Castle Inc.",
    "Equinix Inc.", "Public Storage", "Simon Property Group Inc.",
    "Realty Income Corporation", "Digital Realty Trust Inc.", "Welltower Inc.",
    "Alexandria Real Estate Equities Inc.", "AvalonBay Communities Inc.",
    
    # Utilities
    "NextEra Energy Inc.", "Duke Energy Corporation", "Southern Company",
    "Dominion Energy Inc.", "American Electric Power Company Inc.",
    "Exelon Corporation", "Sempra Energy", "Public Service Enterprise Group Inc.",
    "Xcel Energy Inc.", "Consolidated Edison Inc.", "WEC Energy Group Inc.",
    
    # Materials & Chemicals
    "Linde plc", "Air Products and Chemicals Inc.", "Sherwin-Williams Company",
    "Ecolab Inc.", "Freeport-McMoRan Inc.", "Newmont Corporation",
    "Nucor Corporation", "DuPont de Nemours Inc.", "Dow Inc.",
    "PPG Industries Inc.", "LyondellBasell Industries N.V.", "Mosaic Company",
    
    # Insurance
    "Berkshire Hathaway Inc.", "Marsh & McLennan Companies Inc.",
    "Progressive Corporation", "Chubb Limited", "Travelers Companies Inc.",
    "Allstate Corporation", "MetLife Inc.", "Prudential Financial Inc.",
    "Aflac Inc.", "Hartford Financial Services Group Inc.", "Arthur J. Gallagher & Co.",
    
    # Additional Diversified Companies
    "Visa Inc.", "Mastercard Inc.", "Accenture plc", "IBM Corporation",
    "Deloitte LLP", "FedEx Corporation", "Sysco Corporation",
    "Republic Services Inc.", "Waste Management Inc.", "Cintas Corporation"
]

# Industry sector mapping for realistic assignments
COMPANY_SECTORS = {
    # Technology companies
    "Apple Inc.": "Technology",
    "Microsoft Corporation": "Technology",
    "NVIDIA Corporation": "Technology",
    "Amazon.com Inc.": "Technology",
    "Meta Platforms Inc.": "Technology",
    "Alphabet Inc.": "Technology",
    "Tesla Inc.": "Technology",
    "Oracle Corporation": "Technology",
    "Adobe Inc.": "Technology",
    "Salesforce Inc.": "Technology",
    "Cisco Systems Inc.": "Technology",
    "Intel Corporation": "Technology",
    "ServiceNow Inc.": "Technology",
    "PayPal Holdings Inc.": "Financial Services",
    "Netflix Inc.": "Media & Entertainment",
    
    # Financial Services
    "JPMorgan Chase & Co.": "Financial Services",
    "Bank of America Corporation": "Financial Services",
    "Wells Fargo & Company": "Financial Services",
    "Morgan Stanley": "Financial Services",
    "Goldman Sachs Group Inc.": "Financial Services",
    "Citigroup Inc.": "Financial Services",
    "American Express Company": "Financial Services",
    "BlackRock Inc.": "Financial Services",
    "Visa Inc.": "Financial Services",
    "Mastercard Inc.": "Financial Services",
    
    # Healthcare
    "UnitedHealth Group Inc.": "Healthcare",
    "Johnson & Johnson": "Pharmaceuticals",
    "Eli Lilly and Company": "Pharmaceuticals",
    "Merck & Co. Inc.": "Pharmaceuticals",
    "AbbVie Inc.": "Pharmaceuticals",
    "Pfizer Inc.": "Pharmaceuticals",
    "Abbott Laboratories": "Healthcare",
    "CVS Health Corporation": "Healthcare",
    
    # Retail
    "Walmart Inc.": "Retail",
    "The Home Depot Inc.": "Retail",
    "Costco Wholesale Corporation": "Retail",
    "Target Corporation": "Retail",
    "McDonald's Corporation": "Restaurant",
    "Starbucks Corporation": "Restaurant",
    "Nike Inc.": "Retail",
    "Lowe's Companies Inc.": "Retail",
    
    # Industrial
    "Honeywell International Inc.": "Manufacturing",
    "General Electric Company": "Manufacturing",
    "Caterpillar Inc.": "Manufacturing",
    "3M Company": "Manufacturing",
    "Boeing Company": "Aerospace",
    "Lockheed Martin Corporation": "Aerospace",
    "United Parcel Service Inc.": "Logistics",
    "FedEx Corporation": "Logistics",
    
    # Energy
    "ExxonMobil Corporation": "Energy",
    "Chevron Corporation": "Energy",
    "ConocoPhillips": "Energy",
    
    # Telecom
    "Verizon Communications Inc.": "Telecommunications",
    "AT&T Inc.": "Telecommunications",
    "T-Mobile US Inc.": "Telecommunications",
    "Comcast Corporation": "Telecommunications",
    
    # Real Estate
    "American Tower Corporation": "Real Estate Services",
    "Prologis Inc.": "Real Estate Services",
    "Simon Property Group Inc.": "Real Estate Services",
    
    # Insurance
    "Berkshire Hathaway Inc.": "Financial Services",
    "Progressive Corporation": "Insurance",
    "Travelers Companies Inc.": "Insurance",
}

def get_sector_for_company(company_name):
    """Get the appropriate sector for a company, with fallback"""
    return COMPANY_SECTORS.get(company_name, "Professional Services")
