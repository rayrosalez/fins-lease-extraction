#!/usr/bin/env python3
"""
Verify that all required extraction fields are present in generated leases
"""

from generate_leases import LeaseGenerator
from datetime import datetime
import json

def verify_fields():
    """Verify all required fields are present"""
    
    # Required fields from the extraction schema
    required_fields = {
        "landlord": ["landlord_name", "landlord_address"],
        "tenant": ["tenant_name", "tenant_address", "industry_sector"],
        "property_location": [
            "property_full_address", "property_street", "property_city",
            "property_state", "property_zip", "property_country"
        ],
        "lease_details": [
            "suite_number", "lease_type", "commencement_date",
            "expiration_date", "term_months", "rentable_square_feet"
        ],
        "financial_terms": [
            "annual_base_rent", "monthly_base_rent", "base_rent_psf",
            "annual_escalation_pct", "additional_rent_estimate",
            "pro_rata_share", "security_deposit"
        ],
        "risk_and_options": [
            "renewal_options", "renewal_notice_days",
            "termination_rights", "guarantor"
        ]
    }
    
    print("\n" + "="*70)
    print("FIELD VERIFICATION")
    print("="*70 + "\n")
    
    # Generate sample lease
    generator = LeaseGenerator()
    lease_data = generator.generate_lease_data()
    
    all_present = True
    total_fields = 0
    present_fields = 0
    
    # Check each category
    for category, fields in required_fields.items():
        print(f"\n📋 {category.upper().replace('_', ' ')}")
        print("-" * 70)
        
        for field in fields:
            total_fields += 1
            if field in lease_data:
                value = lease_data[field]
                
                # Format value for display
                if isinstance(value, datetime):
                    display_value = value.strftime('%Y-%m-%d')
                elif isinstance(value, float):
                    display_value = f"{value:.4f}" if value < 1 else f"{value:.2f}"
                elif isinstance(value, int):
                    display_value = f"{value:,}"
                else:
                    display_value = str(value)
                
                # Truncate long values
                if len(display_value) > 50:
                    display_value = display_value[:47] + "..."
                
                print(f"  ✅ {field:30s} {display_value}")
                present_fields += 1
            else:
                print(f"  ❌ {field:30s} MISSING")
                all_present = False
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"Total Required Fields:  {total_fields}")
    print(f"Present:                {present_fields}")
    print(f"Missing:                {total_fields - present_fields}")
    print(f"Status:                 {'✅ PASS' if all_present else '❌ FAIL'}")
    print("="*70 + "\n")
    
    if all_present:
        print("✅ All required fields are present in generated leases!")
        print("   The PDFs should extract correctly.\n")
        return True
    else:
        print("❌ Some required fields are missing!")
        print("   Generated leases may not extract properly.\n")
        return False

if __name__ == "__main__":
    verify_fields()

