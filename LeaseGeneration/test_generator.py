#!/usr/bin/env python3
"""
Quick test script to generate a single lease and display its details
"""

from generate_leases import LeaseGenerator
import json

def test_single_lease():
    """Generate and display details of a single lease"""
    generator = LeaseGenerator()
    
    print("\n" + "="*70)
    print("LEASE GENERATOR TEST")
    print("="*70 + "\n")
    
    # Generate lease data
    print("Generating lease data...")
    lease_data = generator.generate_lease_data()
    
    # Display key details
    print("\n📋 LEASE DETAILS:")
    print("-" * 70)
    print(f"Landlord:              {lease_data['landlord_name']}")
    print(f"Tenant:                {lease_data['tenant_name']}")
    print(f"Industry:              {lease_data['industry_sector']}")
    print(f"Property:              {lease_data['property_full_address']}")
    print(f"Suite:                 {lease_data['suite_number']}")
    print(f"Square Feet:           {lease_data['rentable_square_feet']:,} RSF")
    print(f"Lease Type:            {lease_data['lease_type']}")
    print(f"Start Date:            {lease_data['commencement_date'].strftime('%Y-%m-%d')}")
    print(f"End Date:              {lease_data['expiration_date'].strftime('%Y-%m-%d')}")
    print(f"Term:                  {lease_data['term_months']} months")
    print(f"Annual Base Rent:      ${lease_data['annual_base_rent']:,}")
    print(f"Monthly Base Rent:     ${lease_data['monthly_base_rent']:,.2f}")
    print(f"Base Rent PSF:         ${lease_data['base_rent_psf']:.2f}")
    print(f"Annual Escalation:     {lease_data['annual_escalation_pct']}%")
    print(f"Security Deposit:      ${lease_data['security_deposit']:,}")
    print(f"Renewal Options:       {lease_data['renewal_options']}")
    print(f"Renewal Notice Days:   {lease_data['renewal_notice_days']} days")
    print("-" * 70)
    
    # Generate PDF
    print("\n📄 Generating PDF...")
    filepath = generator.create_lease_pdf(lease_data, "TEST_Lease_Sample.pdf")
    
    print("\n" + "="*70)
    print("✓ TEST COMPLETE")
    print(f"✓ PDF generated: {filepath}")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_single_lease()

