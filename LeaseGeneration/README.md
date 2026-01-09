# Commercial Lease Agreement Generator

This system generates realistic, multi-page synthetic PDF lease agreements that resemble real commercial real estate leases used by REPE analysts.

## Features

- **10+ Page Documents**: Each lease is approximately 10-12 pages with professional formatting
- **Realistic Content**: Includes all standard commercial lease sections and legal language
- **Complete Data**: All fields required by the extraction agent are present
- **Real Addresses**: Uses actual US commercial building addresses
- **S&P 500 Companies**: Uses REAL company names from the S&P 500 index for tenants
- **Industry-Specific Sectors**: Automatically assigns correct industry sectors to companies
- **Randomized Fields**: Financial terms, dates, and other details are randomized
- **Professional Formatting**: Multi-column tables, proper legal formatting, and section numbering

## S&P 500 Integration

The generator now uses **208 real S&P 500 companies** as tenants, including:
- **Technology**: Apple, Microsoft, NVIDIA, Amazon, Meta, Alphabet, Tesla, Oracle, Adobe, Salesforce, etc.
- **Financial Services**: JPMorgan Chase, Bank of America, Goldman Sachs, Morgan Stanley, Visa, Mastercard, etc.
- **Healthcare & Pharma**: UnitedHealth, Johnson & Johnson, Eli Lilly, Merck, Pfizer, Abbott, CVS Health, etc.
- **Retail**: Walmart, Home Depot, Costco, Target, McDonald's, Starbucks, Nike, Lowe's, etc.
- **Industrial**: Honeywell, GE, Caterpillar, 3M, Boeing, Lockheed Martin, UPS, FedEx, etc.
- **Energy**: ExxonMobil, Chevron, ConocoPhillips, etc.
- **Telecommunications**: Verizon, AT&T, T-Mobile, Comcast, etc.
- **And more across all major sectors**

Each company is automatically assigned its appropriate industry sector for realistic lease generation.

## Fields Included

Every generated lease contains all fields required by the AI extraction agent:

### Landlord Information
- Legal name
- Complete address

### Tenant Information
- Company name
- Address
- Industry sector

### Property Location
- Full address
- Street address
- City, State, ZIP code
- Country

### Lease Details
- Suite number
- Lease type (Triple Net, Modified Gross, etc.)
- Commencement date
- Expiration date
- Term in months
- Rentable square feet

### Financial Terms
- Annual base rent
- Monthly base rent
- Base rent per square foot
- Annual escalation percentage
- Additional rent estimate
- Pro rata share
- Security deposit

### Risk & Options
- Renewal options
- Renewal notice days
- Termination rights
- Guarantor information

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate 10 Leases (Default)

```bash
python generate_leases.py
```

### Generate Custom Number of Leases

Edit the last line in `generate_leases.py`:

```python
generator.generate_multiple_leases(count=25)  # Generate 25 leases
```

### Use in Your Own Code

```python
from generate_leases import LeaseGenerator

# Initialize generator
generator = LeaseGenerator(output_dir="my_leases")

# Generate single lease
lease_data = generator.generate_lease_data()
filepath = generator.create_lease_pdf(lease_data)

# Generate multiple leases
generator.generate_multiple_leases(count=50)
```

## Output

PDFs are saved to the `generated_leases/` directory by default with filenames like:
```
Commercial_Lease_001_Acme_Corporation.pdf
Commercial_Lease_002_TechFlow_Solutions_Inc.pdf
...
```

## Document Structure

Each lease includes:

1. **Title Page**: Basic information table
2. **Parties**: Landlord and tenant details
3. **Premises**: Property description and square footage
4. **Term**: Start date, end date, duration
5. **Financial Terms**: Detailed rent schedule and obligations
6. **Use and Maintenance**: Permitted uses and repair obligations
7. **Insurance**: Required coverage and indemnification
8. **Operating Expenses**: CAM charges and reconciliation
9. **Utilities and Services**: HVAC, janitorial, etc.
10. **Alterations**: Tenant improvement procedures
11. **Assignment**: Subletting restrictions
12. **Default**: Events of default and remedies
13. **Renewal Options**: Extension rights and procedures
14. **Termination**: Early termination provisions
15. **Additional Provisions**: Parking, signage, access, environmental
16. **Legal Clauses**: Subordination, notices, governing law, etc.
17. **Signature Page**: Execution blocks

## Customization

### Add More Addresses

Edit the `US_ADDRESSES` list in `generate_leases.py`:

```python
US_ADDRESSES = [
    {"street": "123 Main St", "city": "Your City", "state": "ST", "zip": "12345", "country": "United States"},
    # Add more...
]
```

### Add More Company Names

The system now uses real S&P 500 companies from `sp500_companies.py`. To add more companies:

```python
# Edit sp500_companies.py
SP500_COMPANIES = [
    "Your Company Name",
    # ... existing companies
]

# Add sector mapping
COMPANY_SECTORS = {
    "Your Company Name": "Your Industry Sector",
    # ... existing mappings
}
```

Available sectors: Technology, Financial Services, Healthcare, Pharmaceuticals, Retail, Restaurant, 
Manufacturing, Aerospace, Logistics, Energy, Telecommunications, Insurance, Media & Entertainment, 
Real Estate Services, Professional Services

### Modify Financial Ranges

Adjust the ranges in the `generate_lease_data()` method:

```python
square_feet = random.randint(5000, 50000)  # Larger spaces
base_rent_psf = round(random.uniform(50.0, 150.0), 2)  # Higher rents
```

## Testing with Extraction Pipeline

1. Generate leases: `python generate_leases.py`
2. Upload PDFs to your extraction system
3. Verify all fields are extracted correctly
4. Use for performance testing and validation

## License

Created for the FINS Lease Extraction system.

