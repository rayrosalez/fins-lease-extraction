#!/usr/bin/env python3
"""
Batch lease generator with command-line options
"""

import argparse
from generate_leases import LeaseGenerator
import os

def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic commercial lease agreements',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_generate.py --count 25
  python batch_generate.py --count 50 --output custom_leases
  python batch_generate.py --count 100 --prefix TestLease
        """
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=10,
        help='Number of leases to generate (default: 10)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='generated_leases',
        help='Output directory (default: generated_leases)'
    )
    
    parser.add_argument(
        '-p', '--prefix',
        type=str,
        default='Commercial_Lease',
        help='Filename prefix (default: Commercial_Lease)'
    )
    
    parser.add_argument(
        '--show-sample',
        action='store_true',
        help='Show sample lease data before generating'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = LeaseGenerator(output_dir=args.output)
    
    # Show sample if requested
    if args.show_sample:
        print("\n" + "="*70)
        print("SAMPLE LEASE DATA")
        print("="*70 + "\n")
        sample = generator.generate_lease_data()
        print(f"Tenant: {sample['tenant_name']}")
        print(f"Landlord: {sample['landlord_name']}")
        print(f"Property: {sample['property_full_address']}")
        print(f"Square Feet: {sample['rentable_square_feet']:,}")
        print(f"Annual Rent: ${sample['annual_base_rent']:,}")
        print(f"Term: {sample['term_months']} months")
        print("\n" + "="*70 + "\n")
        
        response = input("Continue with generation? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Generate leases
    print(f"\n{'='*70}")
    print(f"BATCH LEASE GENERATION")
    print(f"{'='*70}\n")
    print(f"Count: {args.count}")
    print(f"Output: {args.output}")
    print(f"Prefix: {args.prefix}")
    print()
    
    generated_files = []
    for i in range(args.count):
        lease_data = generator.generate_lease_data()
        filename = f"{args.prefix}_{i+1:03d}_{lease_data['tenant_name'].replace(' ', '_')}.pdf"
        filepath = generator.create_lease_pdf(lease_data, filename)
        generated_files.append(filepath)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{args.count} leases generated...")
    
    print(f"\n{'='*70}")
    print(f"✓ Successfully generated {args.count} lease agreements")
    print(f"✓ Location: {os.path.abspath(args.output)}")
    print(f"{'='*70}\n")
    
    # Show file list
    print("Generated files:")
    for f in generated_files[:5]:  # Show first 5
        print(f"  - {os.path.basename(f)}")
    
    if len(generated_files) > 5:
        print(f"  ... and {len(generated_files) - 5} more")
    
    print()

if __name__ == "__main__":
    main()

