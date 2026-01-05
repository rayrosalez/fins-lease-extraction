# LeaseGeneration - Quick Reference

## 🚀 Most Common Commands

```bash
# Basic generation (10 leases)
python generate_leases.py

# Generate 50 leases
python batch_generate.py --count 50

# Test single lease
python test_generator.py

# Verify all fields present
python verify_fields.py
```

## 📂 File Structure

```
LeaseGeneration/
├── generate_leases.py      # Main generator (USE THIS)
├── batch_generate.py       # Batch with options
├── test_generator.py       # Quick test
├── verify_fields.py        # Check fields
├── inspect_pdf.py          # View PDF content
├── view_data.py            # See JSON data
├── quickstart.sh           # One-click setup
├── requirements.txt        # Dependencies
└── generated_leases/       # Output folder
    └── *.pdf               # Your leases
```

## ✅ What You Get

- **10-12 page PDFs** - Professional lease documents
- **28 fields** - All extraction fields present
- **Real addresses** - Actual US commercial properties
- **Realistic data** - Industry-standard terms

## 🎯 Field Categories (28 total)

| Category | Count | Examples |
|----------|-------|----------|
| Landlord | 2 | Name, Address |
| Tenant | 3 | Name, Address, Industry |
| Property | 6 | Street, City, State, ZIP, Country |
| Lease Details | 6 | Suite, Type, Dates, Term, Sq Ft |
| Financial | 7 | Rent, Escalation, Deposit |
| Risk/Options | 4 | Renewal, Termination, Guarantor |

## 📊 Performance

| Leases | Time | Size |
|--------|------|------|
| 10 | 15 sec | 300 KB |
| 50 | 1 min | 1.5 MB |
| 100 | 2-3 min | 3-4 MB |

## 🔧 Customization

Edit `generate_leases.py`:
- Line ~40: `US_ADDRESSES` - Add addresses
- Line ~60: `TENANT_NAMES` - Add companies
- Line ~200: `generate_lease_data()` - Adjust ranges

## 📖 Documentation

- `README.md` - Start here
- `USAGE_GUIDE.md` - Detailed instructions
- `FIELD_MAPPING.md` - Where fields appear in PDFs
- `SUMMARY.txt` - Complete overview

## 🧪 Testing Workflow

1. Generate test: `python test_generator.py`
2. Verify fields: `python verify_fields.py`
3. Upload 1 PDF to your system
4. Check extraction results
5. Generate full batch if successful

## 💡 Pro Tips

- Start with 5-10 leases for testing
- Use `--show-sample` to preview before generating
- Check `verify_fields.py` output to confirm completeness
- Use `inspect_pdf.py` to debug extraction issues

## 🆘 Quick Troubleshooting

**Module not found?**
```bash
pip install -r requirements.txt
```

**Permission denied?**
```bash
chmod +x quickstart.sh
```

**Can't find PDFs?**
```bash
ls generated_leases/
```

## 🎓 Example Session

```bash
cd LeaseGeneration
pip install -r requirements.txt
python test_generator.py          # Test one
python verify_fields.py           # Check fields
python generate_leases.py         # Generate 10
python inspect_pdf.py             # Inspect latest
```

## 📞 Help

- Check `USAGE_GUIDE.md` for detailed help
- Run `python batch_generate.py --help`
- Review error messages for specifics

---

**Quick Start**: `cd LeaseGeneration && python generate_leases.py`

