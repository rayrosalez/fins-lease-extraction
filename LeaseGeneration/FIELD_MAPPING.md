# Field Mapping Reference

This document shows where each required extraction field appears in the generated lease PDFs.

## Document Structure → Extraction Fields

### ARTICLE I: PARTIES TO THE LEASE

#### Section 1.1 - LANDLORD
```
Extraction Fields:
- landlord.name          → "Metropolitan Real Estate Holdings LLC"
- landlord.address       → "100 Pine Street, San Francisco, CA 94111"
```

**PDF Text:**
> "LANDLORD: Metropolitan Real Estate Holdings LLC, a limited liability company organized under the laws of the State of Delaware, with a principal place of business at 100 Pine Street, San Francisco, CA 94111 (hereinafter referred to as "Landlord")."

#### Section 1.2 - TENANT
```
Extraction Fields:
- tenant.name            → "Acme Corporation"
- tenant.address         → "350 Fifth Avenue, New York, NY 10118"
- tenant.industry_sector → "Technology"
```

**PDF Text:**
> "TENANT: Acme Corporation, a corporation engaged in the Technology industry, with an address at 350 Fifth Avenue, New York, NY 10118 (hereinafter referred to as "Tenant")."

---

### ARTICLE II: DEMISED PREMISES

#### Section 2.1 - PREMISES DESCRIPTION
```
Extraction Fields:
- property_location.full_address    → "350 Fifth Avenue, New York, NY 10118, United States"
- property_location.street_address  → "350 Fifth Avenue"
- property_location.city            → "New York"
- property_location.state           → "NY"
- property_location.zip_code        → "10118"
- property_location.country         → "United States"
```

**PDF Text:**
> "Landlord hereby leases to Tenant, and Tenant hereby leases from Landlord, those certain premises known as Suite 100, located at 350 Fifth Avenue, New York, NY 10118, United States (the "Premises")."

#### Section 2.2 - RENTABLE SQUARE FEET
```
Extraction Field:
- lease_details.rentable_square_feet → 15000
```

**PDF Text:**
> "The Premises contain approximately 15,000 rentable square feet (RSF), as measured in accordance with the Building Owners and Managers Association (BOMA) standards."

#### Section 2.3 - LEASE TYPE
```
Extraction Field:
- lease_details.lease_type → "Triple Net (NNN)"
```

**PDF Text:**
> "This lease shall be classified as a Triple Net (NNN) lease."

---

### ARTICLE III: LEASE TERM

#### Section 3.1 - COMMENCEMENT DATE
```
Extraction Field:
- lease_details.commencement_date → "2024-06-15"
```

**PDF Text:**
> "The term of this Lease shall commence on June 15, 2024 (the "Commencement Date")."

#### Section 3.2 - EXPIRATION DATE
```
Extraction Field:
- lease_details.expiration_date → "2029-06-14"
```

**PDF Text:**
> "Unless sooner terminated as provided herein, this Lease shall expire on June 14, 2029 (the "Expiration Date"), at 11:59 p.m. local time."

#### Section 3.3 - TERM LENGTH
```
Extraction Field:
- lease_details.term_months → 60
```

**PDF Text:**
> "The initial term of this Lease shall be 60 months (5 years)."

---

### ARTICLE III: DEMISED PREMISES (Title Page)

#### Basic Information Table
```
Extraction Field:
- lease_details.suite_number → "Suite 100"
```

**PDF Text (Table):**
```
| Suite/Unit: | Suite 100 |
```

---

### ARTICLE IV: RENT AND FINANCIAL OBLIGATIONS

#### Section 4.1 - ANNUAL BASE RENT
```
Extraction Field:
- financial_terms.annual_base_rent → 750000
```

**PDF Text:**
> "Tenant shall pay to Landlord annual base rent in the amount of $750,000 (the "Annual Base Rent")."

#### Section 4.2 - MONTHLY BASE RENT
```
Extraction Field:
- financial_terms.monthly_base_rent → 62500.00
```

**PDF Text:**
> "The Annual Base Rent shall be payable in equal monthly installments of $62,500.00, due and payable on the first day of each calendar month during the Lease Term, without demand, deduction, or offset."

#### Section 4.3 - BASE RENT PER SQUARE FOOT
```
Extraction Field:
- financial_terms.base_rent_psf → 50.00
```

**PDF Text:**
> "The base rent is calculated at a rate of $50.00 per rentable square foot per annum."

#### Section 4.4 - ANNUAL ESCALATION
```
Extraction Field:
- financial_terms.annual_escalation_pct → 3
```

**PDF Text:**
> "Commencing on the first anniversary of the Commencement Date, and on each anniversary thereafter, the Annual Base Rent shall increase by 3% annually. Such increases shall be cumulative and compounding."

#### Section 4.5 - ADDITIONAL RENT
```
Extraction Field:
- financial_terms.additional_rent_estimate → 150000.00
```

**PDF Text:**
> "In addition to the Base Rent, Tenant shall pay as additional rent Tenant's Pro Rata Share of Operating Expenses, estimated to be approximately $150,000.00 annually."

#### Section 4.6 - PRO RATA SHARE
```
Extraction Field:
- financial_terms.pro_rata_share → 0.1250
```

**PDF Text:**
> "Tenant's proportionate share of building expenses shall be 0.1250 (12.50%), calculated as the ratio of the Premises' rentable square footage to the total rentable square footage of the building."

#### Section 4.7 - SECURITY DEPOSIT
```
Extraction Field:
- financial_terms.security_deposit → 125000
```

**PDF Text:**
> "Upon execution of this Lease, Tenant shall deposit with Landlord the sum of $125,000 as security for the faithful performance of Tenant's obligations hereunder (the "Security Deposit")."

---

### ARTICLE XIII: RENEWAL OPTIONS

#### Section 13.1 - RENEWAL RIGHTS
```
Extraction Field:
- risk_and_options.renewal_options → "Two (2) five-year renewal options"
```

**PDF Text:**
> "Subject to the terms and conditions set forth herein, Tenant shall have Two (2) five-year renewal options to extend the Lease Term (each, a "Renewal Term")."

#### Section 13.2 - EXERCISE OF OPTION
```
Extraction Field:
- risk_and_options.renewal_notice_days → 180
```

**PDF Text:**
> "To exercise a renewal option, Tenant must provide written notice to Landlord not less than 180 days prior to the expiration of the then-current term."

---

### ARTICLE XIV: TERMINATION RIGHTS

#### Section 14.1 - EARLY TERMINATION
```
Extraction Field:
- risk_and_options.termination_rights → "Tenant may terminate after 36 months with 6 months notice and payment of unamortized tenant improvements"
```

**PDF Text:**
> "Tenant may terminate after 36 months with 6 months notice and payment of unamortized tenant improvements"

---

### ARTICLE XV: GUARANTY

#### Section 15.1 - GUARANTY REQUIREMENT
```
Extraction Field:
- risk_and_options.guarantor → "Personal guaranty by John Smith, CEO"
```

**PDF Text:**
> "Personal guaranty by John Smith, CEO"

---

## Field Categories Summary

### Category 1: Landlord (2 fields)
- **Location in PDF**: Article I, Section 1.1
- **Fields**: name, address

### Category 2: Tenant (3 fields)
- **Location in PDF**: Article I, Section 1.2
- **Fields**: name, address, industry_sector

### Category 3: Property Location (6 fields)
- **Location in PDF**: Title page + Article II, Section 2.1
- **Fields**: full_address, street_address, city, state, zip_code, country

### Category 4: Lease Details (6 fields)
- **Location in PDF**: Articles II & III
- **Fields**: suite_number, lease_type, commencement_date, expiration_date, term_months, rentable_square_feet

### Category 5: Financial Terms (7 fields)
- **Location in PDF**: Article IV (entire section)
- **Fields**: annual_base_rent, monthly_base_rent, base_rent_psf, annual_escalation_pct, additional_rent_estimate, pro_rata_share, security_deposit

### Category 6: Risk & Options (4 fields)
- **Location in PDF**: Articles XIII, XIV, XV
- **Fields**: renewal_options, renewal_notice_days, termination_rights, guarantor

---

## Extraction Tips

### 1. Date Formats
Dates appear as: "June 15, 2024" → Extract as: "2024-06-15"

### 2. Currency Values
Money appears as: "$750,000" → Extract as: 750000

### 3. Percentages
Percentages appear as: "3%" → Extract as: 3

### 4. Decimal Numbers
Decimals appear as: "0.1250 (12.50%)" → Extract as: 0.1250

### 5. Square Footage
Areas appear as: "15,000 rentable square feet" → Extract as: 15000

### 6. Addresses
Complete addresses combine multiple sentence parts

### 7. Multi-line Fields
Some fields span multiple sentences (termination_rights, renewal_options)

---

## Common Extraction Patterns

### Pattern: Bold Labels
```
Look for: <b>LANDLORD:</b>
Extract: Text following the label
```

### Pattern: Section Headers
```
Look for: "ARTICLE [Roman Numeral]: [SECTION NAME]"
Context: Content follows in numbered subsections
```

### Pattern: Defined Terms
```
Look for: (the "Term Name")
Context: Key terms are defined in quotes
```

### Pattern: Tables
```
Look for: "RENT SCHEDULE SUMMARY"
Extract: Structured data from table rows
```

### Pattern: Monetary Values
```
Look for: $ followed by numbers
Clean: Remove commas and $ sign
```

---

## Quality Assurance

### Validation Checklist
- [ ] All 28 fields present
- [ ] Dates in YYYY-MM-DD format
- [ ] Numbers without formatting (no commas, $, %)
- [ ] Addresses complete with all components
- [ ] No null values for required fields

### Common Issues
1. **Multiple addresses**: Ensure you extract property address, not landlord/tenant address
2. **Date formats**: Convert from written format to ISO format
3. **Calculated values**: Some fields may need calculation (term_months from dates)
4. **Unit conversions**: Ensure consistent units (annual vs monthly rent)

---

**Version**: 1.0  
**Last Updated**: January 5, 2026  
**Purpose**: Guide for AI extraction agent development and validation

