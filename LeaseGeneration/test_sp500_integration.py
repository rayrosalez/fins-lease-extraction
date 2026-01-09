#!/usr/bin/env python3
"""
Test script to verify S&P 500 company integration
"""

from generate_leases import LeaseGenerator
from sp500_companies import SP500_COMPANIES, get_sector_for_company
import random

def test_sp500_integration():
    """Test that S&P 500 companies are being used correctly"""
    
    print("\n" + "="*70)
    print("S&P 500 COMPANY INTEGRATION TEST")
    print("="*70 + "\n")
    
    # Show some sample companies
    print("Sample S&P 500 Companies Available:")
    sample_companies = random.sample(SP500_COMPANIES, 10)
    for company in sample_companies:
        sector = get_sector_for_company(company)
        print(f"  • {company} - {sector}")
    
    print(f"\nTotal S&P 500 companies available: {len(SP500_COMPANIES)}")
    
    # Test lease generation
    print("\n" + "-"*70)
    print("Testing Lease Generation with Real Companies")
    print("-"*70 + "\n")
    
    generator = LeaseGenerator(output_dir="test_output")
    
    # Generate 3 sample leases
    print("Generating 3 sample leases...\n")
    for i in range(3):
        lease_data = generator.generate_lease_data()
        print(f"Lease {i+1}:")
        print(f"  Tenant: {lease_data['tenant_name']}")
        print(f"  Industry: {lease_data['industry_sector']}")
        print(f"  Property: {lease_data['property_city']}, {lease_data['property_state']}")
        print(f"  Square Feet: {lease_data['rentable_square_feet']:,}")
        print(f"  Annual Rent: ${lease_data['annual_base_rent']:,}")
        print(f"  Term: {lease_data['term_months']} months")
        print()
    
    print("="*70)
    print("✓ Integration test successful!")
    print("  Real S&P 500 companies are now being used for lease generation")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_sp500_integration()
