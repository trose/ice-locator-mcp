#!/usr/bin/env python3
"""
Test the heatmap API with SQLite database.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

from ice_locator_mcp.api.heatmap_api import HeatmapAPI

def test_heatmap_api():
    """Test the heatmap API functionality."""
    print("🧪 Testing Heatmap API with SQLite Database")
    
    # Initialize API with SQLite
    api = HeatmapAPI(use_sqlite=True)
    
    try:
        # Test facilities endpoint
        print("\n📋 Testing /api/facilities endpoint...")
        facilities = api.get_facilities()
        print(f"✅ Found {len(facilities)} facilities")
        
        if facilities:
            sample_facility = facilities[0]
            print(f"   Sample facility: {sample_facility['name']}")
            print(f"   Population: {sample_facility['population_count']}")
            print(f"   Coordinates: ({sample_facility['latitude']}, {sample_facility['longitude']})")
        
        # Test facilities with population endpoint
        print("\n📊 Testing /api/facilities-with-population endpoint...")
        facilities_with_pop = api.get_facilities_with_population()
        print(f"✅ Found {len(facilities_with_pop)} facilities with population data")
        
        if facilities_with_pop:
            # Show top 5 facilities by population
            sorted_facilities = sorted(facilities_with_pop, key=lambda x: x['population_count'], reverse=True)
            print("   Top 5 facilities by population:")
            for i, facility in enumerate(sorted_facilities[:5], 1):
                print(f"   {i}. {facility['name']} - {facility['population_count']:,}")
        
        # Test facility statistics endpoint
        print("\n📈 Testing /api/facility-statistics endpoint...")
        stats = api.get_facility_statistics()
        print(f"✅ Statistics retrieved:")
        print(f"   Total facilities: {stats['total_facilities']}")
        print(f"   Total population: {stats['total_population']:,}")
        print(f"   Average population: {stats['average_population']}")
        
        if stats.get('facilities_by_state'):
            print("   Top 5 states by population:")
            for i, state_data in enumerate(stats['facilities_by_state'][:5], 1):
                print(f"   {i}. {state_data['state']} - {state_data['state_population']:,} ({state_data['facility_count']} facilities)")
        
        # Test heatmap data endpoint
        print("\n🗺️ Testing /api/heatmap-data endpoint...")
        heatmap_data = api.get_heatmap_data()
        print(f"✅ Found {len(heatmap_data)} facilities for heatmap")
        
        if heatmap_data:
            sample_heatmap = heatmap_data[0]
            print(f"   Sample heatmap data: {sample_heatmap['name']}")
            print(f"   Population: {sample_heatmap['population_count']}")
            print(f"   Current detainees: {sample_heatmap['current_detainee_count']}")
        
        print("\n🎉 All API tests passed!")
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_heatmap_api()