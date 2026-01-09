# S&P 500 Company Integration - Examples

## Overview
The lease generator now uses real S&P 500 company names instead of fictional companies.

## Sample Generated Leases

Here are examples of the real companies that will now appear in generated leases:

### Technology Sector
- **Apple Inc.** - Technology
- **Microsoft Corporation** - Technology
- **NVIDIA Corporation** - Technology
- **Amazon.com Inc.** - Technology
- **Meta Platforms Inc.** - Technology
- **Alphabet Inc.** - Technology
- **Tesla Inc.** - Technology
- **Oracle Corporation** - Technology
- **Salesforce Inc.** - Technology

### Financial Services
- **JPMorgan Chase & Co.** - Financial Services
- **Bank of America Corporation** - Financial Services
- **Goldman Sachs Group Inc.** - Financial Services
- **Visa Inc.** - Financial Services
- **Mastercard Inc.** - Financial Services
- **American Express Company** - Financial Services

### Healthcare & Pharmaceuticals
- **UnitedHealth Group Inc.** - Healthcare
- **Johnson & Johnson** - Pharmaceuticals
- **Pfizer Inc.** - Pharmaceuticals
- **CVS Health Corporation** - Healthcare
- **Eli Lilly and Company** - Pharmaceuticals

### Retail & Restaurant
- **Walmart Inc.** - Retail
- **The Home Depot Inc.** - Retail
- **Costco Wholesale Corporation** - Retail
- **McDonald's Corporation** - Restaurant
- **Starbucks Corporation** - Restaurant
- **Target Corporation** - Retail

### Energy
- **ExxonMobil Corporation** - Energy
- **Chevron Corporation** - Energy
- **ConocoPhillips** - Energy

### Industrial & Manufacturing
- **Honeywell International Inc.** - Manufacturing
- **General Electric Company** - Manufacturing
- **Caterpillar Inc.** - Manufacturing
- **Boeing Company** - Aerospace
- **3M Company** - Manufacturing

### Telecommunications
- **Verizon Communications Inc.** - Telecommunications
- **AT&T Inc.** - Telecommunications
- **T-Mobile US Inc.** - Telecommunications

## Total Companies
**208 real S&P 500 companies** available for lease generation

## Example Lease Output

```
Commercial_Lease_001_Apple_Inc..pdf
  Tenant: Apple Inc.
  Industry: Technology
  Property: 1 Market Street, San Francisco, CA 94105
  Square Feet: 15,842
  Annual Rent: $1,267,360
  Term: 60 months

Commercial_Lease_002_JPMorgan_Chase_&_Co..pdf
  Tenant: JPMorgan Chase & Co.
  Industry: Financial Services
  Property: 350 Fifth Avenue, New York, NY 10118
  Square Feet: 22,450
  Annual Rent: $1,797,600
  Term: 84 months
```

## Benefits

1. **Realistic Data**: Real company names make the extraction results more believable
2. **Industry Accuracy**: Each company has its correct industry sector assigned
3. **Testing & Demos**: More professional for demonstrations and testing
4. **Real-World Simulation**: Better represents actual REPE portfolio analysis

## Usage

Simply run the generator as before - S&P 500 companies are automatically used:

```bash
python generate_leases.py
```

Or with batch generation:

```bash
python batch_generate.py --count 50
```

The system will randomly select from the 208 available S&P 500 companies for each lease.
