# LeaseGeneration - System Overview

## Summary

The LeaseGeneration system creates realistic, synthetic commercial lease agreement PDFs that resemble real-world documents used by Real Estate Private Equity (REPE) analysts. Each generated lease is approximately 10-12 pages long and contains all fields required by the AI extraction agent.

## Purpose

- **Testing**: Validate extraction pipeline functionality
- **Development**: Test system without sensitive real-world data
- **Performance**: Benchmark system with large datasets
- **Demonstration**: Show complete end-to-end workflow

## Features

✅ **Professional Formatting**: Multi-page PDFs with proper legal document structure  
✅ **Complete Data**: All 28 required extraction fields present  
✅ **Real Addresses**: Actual US commercial property addresses  
✅ **Randomized Content**: Unique values for each generated lease  
✅ **Realistic Ranges**: Financial terms match industry standards  
✅ **Scalable Generation**: Generate from 1 to 1000+ leases  

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate 10 leases (default)
python generate_leases.py

# OR use quick start script
./quickstart.sh
```

## Files & Scripts

| File | Purpose |
|------|---------|
| `generate_leases.py` | Main lease generator class and script |
| `batch_generate.py` | Command-line batch generator with options |
| `test_generator.py` | Generate single test lease with details |
| `view_data.py` | Display lease data in JSON format |
| `verify_fields.py` | Verify all required fields are present |
| `quickstart.sh` | Quick setup and generation script |
| `requirements.txt` | Python dependencies |
| `README.md` | System documentation |
| `USAGE_GUIDE.md` | Detailed usage instructions |

## Generated Lease Structure

Each 10-12 page PDF contains:

### Page 1-2: Core Information
- Title and execution date
- Parties (Landlord & Tenant)
- Premises description
- Lease term dates

### Page 3-4: Financial Terms
- Base rent (annual, monthly, PSF)
- Escalation provisions
- Additional rent and operating expenses
- Security deposit
- Pro rata share

### Page 5-6: Operations
- Use restrictions
- Maintenance obligations
- Insurance requirements
- Utilities and services

### Page 7-8: Legal Provisions
- Assignment and subletting
- Default and remedies
- Renewal options (with notice periods)
- Termination rights
- Guarantor information

### Page 9-10: Additional Terms
- Parking
- Signage
- Access and security
- Environmental compliance
- Subordination
- Estoppel certificates

### Page 11-12: Final Provisions
- Notices
- Governing law
- Signature page

## Data Fields (28 Required)

### Landlord (2 fields)
- Name
- Address

### Tenant (3 fields)
- Name
- Address
- Industry sector

### Property Location (6 fields)
- Full address
- Street address
- City
- State
- ZIP code
- Country

### Lease Details (6 fields)
- Suite number
- Lease type
- Commencement date
- Expiration date
- Term (months)
- Rentable square feet

### Financial Terms (7 fields)
- Annual base rent
- Monthly base rent
- Base rent per square foot
- Annual escalation percentage
- Additional rent estimate
- Pro rata share
- Security deposit

### Risk & Options (4 fields)
- Renewal options
- Renewal notice days
- Termination rights
- Guarantor

## Usage Examples

### Generate Default Batch
```bash
python generate_leases.py
# Output: 10 PDFs in generated_leases/
```

### Generate Custom Quantity
```bash
python batch_generate.py --count 50
# Output: 50 PDFs
```

### Generate to Custom Directory
```bash
python batch_generate.py --count 25 --output test_leases
# Output: 25 PDFs in test_leases/
```

### Test Single Lease
```bash
python test_generator.py
# Output: 1 PDF with details printed
```

### Verify Field Completeness
```bash
python verify_fields.py
# Output: Verification report
```

### View Sample Data
```bash
python view_data.py
# Output: JSON formatted lease data
```

## Integration with Extraction Pipeline

### 1. Generate Leases
```bash
python batch_generate.py --count 100
```

### 2. Upload to System
- Via Frontend: Use upload interface
- Via API: POST to `/upload` endpoint
- Via Databricks: Direct volume upload

### 3. Monitor Extraction
- Check Bronze table for raw extractions
- Validate all 28 fields extracted
- Verify data accuracy

### 4. Validate Silver Layer
- Confirm promotion to Silver
- Check calculated fields
- Review data quality

## Customization

### Add More Addresses
Edit `US_ADDRESSES` list in `generate_leases.py`

### Add More Companies
Edit `TENANT_NAMES` or `LANDLORD_NAMES` lists

### Adjust Financial Ranges
Modify ranges in `generate_lease_data()` method

### Change Document Formatting
Update styles in `_setup_custom_styles()` method

## Performance Metrics

| Metric | Value |
|--------|-------|
| Generation Speed | ~1-2 seconds per lease |
| Average File Size | 30-40 KB per PDF |
| Pages per Lease | 10-12 pages |
| Fields per Lease | 28 required fields |
| 100 Leases | ~2-3 minutes, ~3-4 MB |
| 1000 Leases | ~20-30 minutes, ~30-40 MB |

## Verification

All generated leases have been verified to include:

✅ All 28 required fields (see `verify_fields.py` output)  
✅ Valid dates in YYYY-MM-DD format  
✅ Realistic financial calculations  
✅ Proper address formatting  
✅ Legal document structure  
✅ Professional PDF formatting  

## Testing Workflow

1. **Generate Sample**: `python test_generator.py`
2. **Verify Fields**: `python verify_fields.py`
3. **View Data**: `python view_data.py`
4. **Upload One**: Test extraction with single PDF
5. **Validate**: Check Bronze table for extracted data
6. **Scale Up**: Generate larger batch if successful
7. **Performance Test**: Test system with 100+ leases

## Best Practices

1. **Start Small**: Generate 5-10 leases for initial testing
2. **Verify Extraction**: Confirm pipeline extracts all fields correctly
3. **Scale Gradually**: Increase batch size once validated
4. **Monitor Performance**: Track extraction times and accuracy
5. **Keep Separate**: Store test data separately from production
6. **Version Control**: Track which version generated test data

## Support & Troubleshooting

See `USAGE_GUIDE.md` for:
- Detailed usage instructions
- Troubleshooting common issues
- Command-line reference
- Integration examples
- Customization guide

## Technical Stack

- **Python 3.8+**: Core language
- **ReportLab 4.0+**: PDF generation
- **Pillow**: Image handling for ReportLab
- **Random**: Data generation
- **DateTime**: Date handling

## Directory Structure

```
LeaseGeneration/
├── generate_leases.py      # Main generator
├── batch_generate.py       # CLI batch tool
├── test_generator.py       # Single test
├── view_data.py            # Data viewer
├── verify_fields.py        # Field validator
├── quickstart.sh           # Setup script
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── USAGE_GUIDE.md          # Usage details
├── OVERVIEW.md             # This file
└── generated_leases/       # Output directory
    └── *.pdf               # Generated leases
```

## Status

✅ **Complete and Tested**

- All scripts functional
- All fields verified present
- PDFs generate successfully
- Documentation complete
- Ready for integration testing

## Next Steps

1. Upload generated PDFs to extraction system
2. Validate extraction accuracy
3. Test promotion to Silver layer
4. Benchmark performance with large batches
5. Integrate into CI/CD pipeline (optional)

---

**Version:** 1.0  
**Created:** January 2026  
**Status:** Production Ready  
**License:** Internal Use

