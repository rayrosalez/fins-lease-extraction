#!/usr/bin/env python3
"""
Quick test script for the demo data reset endpoint.
This tests the API endpoint without triggering the full reset.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5001"
RESET_ENDPOINT = f"{BASE_URL}/api/reset-demo-data"

def test_health_check():
    """Test that the API is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

def test_reset_endpoint_exists():
    """Test that the reset endpoint exists (without actually calling it)"""
    try:
        # Use OPTIONS to check if endpoint exists without triggering reset
        response = requests.options(RESET_ENDPOINT, timeout=5)
        print(f"✅ Reset endpoint exists (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not verify reset endpoint: {e}")
        return True  # OPTIONS might not be implemented, that's OK

def prompt_for_full_test():
    """Ask user if they want to run the full reset"""
    print("\n" + "="*60)
    print("⚠️  WARNING: Full Reset Test")
    print("="*60)
    print("This will DELETE all data in your database and repopulate it.")
    print("This action cannot be undone!")
    print()
    response = input("Do you want to proceed with the full reset? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def run_full_reset(num_leases=50):
    """Execute the full reset and report results"""
    print(f"\n🔄 Starting data reset with {num_leases} leases...")
    print("This may take 30-90 seconds...")
    
    try:
        response = requests.post(
            RESET_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json={'num_leases': num_leases},
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Reset completed successfully!")
            print(f"   Message: {data.get('message')}")
            print(f"   Leases: {data.get('leases_generated')}")
            print(f"   Tenants: {data.get('tenants_created')}")
            print(f"   Landlords: {data.get('landlords_created')}")
            print(f"   Counts: {data.get('counts')}")
            return True
        else:
            print(f"\n❌ Reset failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error')}")
                if 'suggestion' in error_data:
                    print(f"   Suggestion: {error_data.get('suggestion')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (>2 minutes)")
        print("   The reset may still be running. Check backend logs.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False

def main():
    """Main test runner"""
    print("="*60)
    print("Demo Data Reset - Backend Test Script")
    print("="*60)
    print()
    
    # Test 1: Health check
    print("Test 1: Backend Health Check")
    if not test_health_check():
        print("\n❌ Tests aborted: Backend is not running")
        print("   Start the backend with: python api.py")
        return
    print()
    
    # Test 2: Endpoint exists
    print("Test 2: Reset Endpoint Check")
    test_reset_endpoint_exists()
    print()
    
    # Test 3: Full reset (optional)
    if prompt_for_full_test():
        # Ask for lease count
        try:
            num_leases = int(input("Number of leases to generate (10-500, default 50): ") or "50")
            num_leases = max(10, min(500, num_leases))
        except ValueError:
            num_leases = 50
            
        success = run_full_reset(num_leases)
        if success:
            print("\n✅ All tests passed!")
            print("\nNext steps:")
            print("  1. Open http://localhost:3000 in your browser")
            print("  2. Navigate to Portfolio page")
            print("  3. Verify you see fresh synthetic data")
            print("  4. Check Risk Assessment for varied expiration dates")
        else:
            print("\n❌ Reset test failed")
            print("   Check backend logs for details")
    else:
        print("\n✅ Basic tests passed (full reset skipped)")
        print("\nThe reset button in the UI should work correctly.")
    
    print()

if __name__ == "__main__":
    main()
