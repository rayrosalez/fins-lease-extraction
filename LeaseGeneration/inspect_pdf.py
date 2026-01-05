#!/usr/bin/env python3
"""
Inspect a generated lease PDF and display summary information
"""

import sys
import os
from datetime import datetime

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

def inspect_pdf(pdf_path):
    """Inspect a lease PDF and show summary"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return False
    
    print("\n" + "="*70)
    print("PDF LEASE INSPECTOR")
    print("="*70 + "\n")
    
    # Basic file info
    file_size = os.path.getsize(pdf_path)
    file_name = os.path.basename(pdf_path)
    
    print(f"📄 File Information:")
    print(f"   Filename:  {file_name}")
    print(f"   Size:      {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   Path:      {pdf_path}")
    print()
    
    # Try to read PDF details
    if HAS_PYPDF2:
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            print(f"📋 PDF Details:")
            print(f"   Pages:     {num_pages}")
            print()
            
            # Try to extract some text from first page
            print(f"📝 First Page Preview:")
            print("-" * 70)
            first_page_text = reader.pages[0].extract_text()
            
            # Show first 500 characters
            preview = first_page_text[:500].strip()
            print(preview)
            if len(first_page_text) > 500:
                print("...")
            print("-" * 70)
            print()
            
            # Look for key terms
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()
            
            print("🔍 Field Detection (in text):")
            
            checks = [
                ("Landlord Name", "LANDLORD:" in full_text or "Landlord:" in full_text),
                ("Tenant Name", "TENANT:" in full_text or "Tenant:" in full_text),
                ("Property Address", "Property Address:" in full_text or "PROPERTY ADDRESS:" in full_text),
                ("Suite Number", "Suite" in full_text),
                ("Commencement Date", "Commencement Date" in full_text or "COMMENCEMENT DATE" in full_text),
                ("Expiration Date", "Expiration Date" in full_text or "EXPIRATION DATE" in full_text),
                ("Base Rent", "Base Rent" in full_text or "BASE RENT" in full_text),
                ("Annual Escalation", "escalation" in full_text.lower()),
                ("Renewal Options", "Renewal" in full_text or "renewal" in full_text),
                ("Security Deposit", "Security Deposit" in full_text or "SECURITY DEPOSIT" in full_text),
            ]
            
            for field, present in checks:
                status = "✅" if present else "⚠️"
                print(f"   {status} {field}")
            
            print()
            
        except Exception as e:
            print(f"⚠️  Could not read PDF details: {e}\n")
    else:
        print("ℹ️  Install PyPDF2 for detailed PDF inspection:")
        print("   pip install PyPDF2\n")
    
    print("="*70 + "\n")
    return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        # Default to showing most recent PDF
        lease_dir = "generated_leases"
        if os.path.exists(lease_dir):
            pdfs = [f for f in os.listdir(lease_dir) if f.endswith('.pdf')]
            if pdfs:
                # Sort by modification time, get most recent
                pdfs.sort(key=lambda x: os.path.getmtime(os.path.join(lease_dir, x)), reverse=True)
                pdf_path = os.path.join(lease_dir, pdfs[0])
                print(f"\nInspecting most recent PDF: {pdfs[0]}\n")
            else:
                print("\n❌ No PDFs found in generated_leases/")
                print("Generate some leases first: python generate_leases.py\n")
                return
        else:
            print("\n❌ No generated_leases/ directory found")
            print("Generate some leases first: python generate_leases.py\n")
            return
    else:
        pdf_path = sys.argv[1]
    
    inspect_pdf(pdf_path)

if __name__ == "__main__":
    main()

