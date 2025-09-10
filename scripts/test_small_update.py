#!/usr/bin/env python3
"""
Test the full data update process with a small sample of facilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.update_facility_data import FacilityDataUpdater

def test_small_update():
    """Test the data update process with a small sample."""
    print("🧪 Testing small data update process...")
    
    updater = FacilityDataUpdater()
    
    try:
        # Fetch data
        print("\n1️⃣ Fetching TRAC data...")
        raw_data = updater.fetch_trac_data()
        print(f"✅ Fetched {len(raw_data)} records")
        
        # Process only first 20 facilities for testing
        print("\n2️⃣ Processing first 20 facilities (for testing)...")
        test_data = raw_data[:20]
        processed_data = updater.process_facility_data(test_data)
        
        print(f"✅ Processed {processed_data['metadata']['total_facilities']} facilities")
        print(f"✅ Total population: {processed_data['metadata']['total_population']:,}")
        
        # Test file writing (to a test location)
        print("\n3️⃣ Testing file writing...")
        test_path = "test_facilities.json"
        original_path = updater.output_path
        updater.output_path = test_path
        
        updater.update_facilities_file(processed_data)
        
        # Show sample of processed data
        print("\n4️⃣ Sample processed facilities:")
        for i, facility in enumerate(processed_data['facilities'][:3]):
            print(f"   {i+1}. {facility['name']}")
            print(f"      Location: {facility['latitude']:.4f}, {facility['longitude']:.4f}")
            print(f"      Population: {facility['population_count']:,}")
            print(f"      Address: {facility['address']}")
        
        # Clean up test file
        if os.path.exists(test_path):
            os.remove(test_path)
            print(f"\n✅ Test file created and cleaned up")
        
        # Restore original path
        updater.output_path = original_path
        
        print("\n🎉 Small update test complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_small_update()
    sys.exit(0 if success else 1)
