#!/usr/bin/env python3
"""
Test script for geocoding functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.update_facility_data import FacilityDataUpdater

def test_geocoding():
    """Test the geocoding functionality with a few sample facilities."""
    print("🧪 Testing geocoding functionality...")
    
    updater = FacilityDataUpdater()
    
    # Test with a few known facilities
    test_facilities = [
        {
            "name": "ADELANTO ICE PROCESSING CENTER",
            "city": "ADELANTO", 
            "state": "CA",
            "zip": "92301"
        },
        {
            "name": "STEWART DETENTION CENTER",
            "city": "LUMPKIN",
            "state": "GA", 
            "zip": "31815"
        },
        {
            "name": "DILLEY FAMILY RESIDENTIAL CENTER",
            "city": "DILLEY",
            "state": "TX",
            "zip": "78017"
        }
    ]
    
    print(f"\n🗺️  Testing geocoding for {len(test_facilities)} facilities...")
    
    for i, facility in enumerate(test_facilities, 1):
        print(f"\n{i}. Testing: {facility['name']}")
        coords = updater.geocode_facility(
            facility['name'],
            facility['city'], 
            facility['state'],
            facility['zip']
        )
        
        if coords:
            print(f"   ✅ Success: {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"   ❌ Failed to geocode")
    
    print(f"\n🎉 Geocoding test complete!")

if __name__ == "__main__":
    test_geocoding()
