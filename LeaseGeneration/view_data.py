#!/usr/bin/env python3
"""
View lease data in JSON format (useful for debugging and validation)
"""

from generate_leases import LeaseGenerator
import json
from datetime import datetime

def datetime_handler(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f"Type {type(obj)} not serializable")

def view_lease_data():
    """Generate lease data and display as formatted JSON"""
    generator = LeaseGenerator()
    lease_data = generator.generate_lease_data()
    
    print("\n" + "="*70)
    print("LEASE DATA JSON VIEW")
    print("="*70 + "\n")
    
    # Pretty print the JSON
    json_output = json.dumps(lease_data, indent=2, default=datetime_handler)
    print(json_output)
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    view_lease_data()

