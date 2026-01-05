# Lease Generation System - Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate 10 Leases (Default)
```bash
python generate_leases.py
```

OR use the quick start script:
```bash
./quickstart.sh
```

## Usage Options

### Option 1: Simple Generation
Generate a default batch of 10 leases:
```bash
python generate_leases.py
```

### Option 2: Batch Generation with Options
Use the batch generator for more control:

```bash
# Generate 25 leases
python batch_generate.py --count 25

# Generate to custom directory
python batch_generate.py --count 50 --output my_leases

# Custom prefix for filenames
python batch_generate.py --count 20 --prefix TestLease

# Show sample data before generating
python batch_generate.py --count 10 --show-sample
```

### Option 3: Test Single Lease
Generate and view details of a single test lease:
```bash
python test_generator.py
```

### Option 4: View Sample Data
View lease data structure in JSON format:
```bash
python view_data.py
```

## Command-Line Reference

### batch_generate.py

```bash
python batch_generate.py [OPTIONS]

Options:
  -c, --count N         Number of leases to generate (default: 10)
  -o, --output DIR      Output directory (default: generated_leases)
  -p, --prefix PREFIX   Filename prefix (default: Commercial_Lease)
  --show-sample         Show sample lease data before generating
  -h, --help            Show help message
```

### Examples

```bash
# Generate 100 leases
python batch_generate.py -c 100

# Generate to specific folder
python batch_generate.py -c 50 -o ../test_leases

# Custom naming
python batch_generate.py -c 25 -p MyCompany_Lease

# Review before generating
python batch_generate.py -c 10 --show-sample
```

## Output

### File Locations
PDFs are saved to:
- Default: `generated_leases/`
- Custom: Specified by `--output` parameter

### Filename Format
```
Commercial_Lease_001_Acme_Corporation.pdf
Commercial_Lease_002_TechFlow_Solutions_Inc.pdf
```

## Document Specifications

### Page Count
Each lease is approximately **10-12 pages** and includes:

1. Title page with basic information
2. Parties (Landlord & Tenant)
3. Premises description
4. Lease term
5. Financial terms (detailed)
6. Use and maintenance
7. Insurance and indemnification
8. Operating expenses
9. Utilities and services
10. Alterations and improvements
11. Assignment and subletting
12. Default and remedies
13. Renewal options
14. Termination rights
15. Additional provisions (parking, signage, access, etc.)
16. Legal clauses
17. Signature page

### Data Fields Included

**All fields required by the extraction agent:**

- ✅ Landlord name and address
- ✅ Tenant name, address, and industry sector
- ✅ Property location (full address breakdown)
- ✅ Suite number
- ✅ Lease type
- ✅ Commencement and expiration dates
- ✅ Term in months
- ✅ Rentable square feet
- ✅ Annual base rent
- ✅ Monthly base rent
- ✅ Base rent per square foot
- ✅ Annual escalation percentage
- ✅ Additional rent estimate
- ✅ Pro rata share
- ✅ Security deposit
- ✅ Renewal options
- ✅ Renewal notice days
- ✅ Termination rights
- ✅ Guarantor information

### Data Ranges

The generator uses realistic ranges:

| Field | Range |
|-------|-------|
| Square Feet | 2,000 - 25,000 RSF |
| Base Rent PSF | $25.00 - $85.00 |
| Term | 36, 48, 60, 84, or 120 months |
| Escalation | 2%, 3%, or 4% annually |
| Security Deposit | 1-3 months rent |
| Renewal Notice | 90-360 days |

## Customization

### Add More Addresses

Edit `generate_leases.py` and add to `US_ADDRESSES`:

```python
US_ADDRESSES = [
    {"street": "Your Street", "city": "City", "state": "ST", "zip": "12345", "country": "United States"},
    # ... more addresses
]
```

### Add More Company Names

Edit `TENANT_NAMES` or `LANDLORD_NAMES`:

```python
TENANT_NAMES = [
    "Your Company Name",
    # ... more names
]
```

### Modify Financial Ranges

In the `generate_lease_data()` method:

```python
# Change square footage range
square_feet = random.randint(5000, 100000)

# Change rent per square foot range
base_rent_psf = round(random.uniform(40.0, 120.0), 2)

# Change term options
term_months = random.choice([36, 60, 84, 120, 180])
```

## Integration with Extraction System

### Upload to Extraction Pipeline

1. Generate leases:
   ```bash
   python batch_generate.py -c 50
   ```

2. Upload PDFs to your system via:
   - Frontend upload interface
   - API endpoint
   - Direct Databricks upload

3. Monitor extraction results in Bronze table

### Validation Testing

Use generated leases to test:
- ✅ Extraction accuracy
- ✅ Field completeness
- ✅ Date parsing
- ✅ Financial calculations
- ✅ Address normalization
- ✅ Performance benchmarks

## Troubleshooting

### Issue: Import Error
```
ModuleNotFoundError: No module named 'reportlab'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Permission Denied
```
PermissionError: [Errno 13] Permission denied: 'generated_leases'
```

**Solution:**
```bash
# Create directory manually
mkdir generated_leases

# Or specify different directory
python batch_generate.py -o ~/Documents/leases
```

### Issue: PDFs Not Opening
```
PDF shows as corrupted
```

**Solution:**
- Ensure reportlab installed correctly
- Check disk space
- Try regenerating the specific file

## Performance

### Generation Speed
- ~1-2 seconds per lease
- 100 leases: ~2-3 minutes
- 1000 leases: ~20-30 minutes

### File Sizes
- Average: 30-40 KB per PDF
- 100 leases: ~3-4 MB total
- 1000 leases: ~30-40 MB total

## Best Practices

1. **Start Small**: Generate 10-20 leases first to verify output
2. **Test Extraction**: Upload a few samples to test your pipeline
3. **Batch Generation**: For large sets, use batch_generate.py
4. **Version Control**: Keep generated leases separate from code
5. **Naming**: Use meaningful prefixes for different test scenarios

## Support

For issues or questions:
1. Check this guide
2. Review README.md
3. Examine the source code comments
4. Check extraction pipeline compatibility

## Next Steps

After generating leases:

1. **Test Upload** - Upload 1-2 leases to verify format
2. **Validate Extraction** - Check all fields extract correctly
3. **Benchmark** - Test system performance with larger batches
4. **Iterate** - Adjust generation parameters as needed
5. **Production** - Generate full test dataset

---

**Version:** 1.0  
**Last Updated:** January 2026

