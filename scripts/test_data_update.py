#!/usr/bin/env python3
"""
Test script for the facility data update process.
This can be run locally to test the data fetching and processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.update_facility_data import FacilityDataUpdater

def test_data_update():
    """Test the data update process."""
    print("🧪 Testing facility data update process...")
    
    updater = FacilityDataUpdater()
    
    try:
        # Test data fetching
        print("\n1️⃣ Testing data fetch...")
        raw_data = updater.fetch_trac_data()
        print(f"✅ Fetched {len(raw_data)} records")
        
        # Test data processing
        print("\n2️⃣ Testing data processing...")
        processed_data = updater.process_facility_data(raw_data)
        print(f"✅ Processed {processed_data['metadata']['total_facilities']} facilities")
        print(f"✅ Total population: {processed_data['metadata']['total_population']:,}")
        
        # Test data validation
        print("\n3️⃣ Testing data validation...")
        is_valid = updater.validate_data(processed_data)
        if is_valid:
            print("✅ Data validation passed")
        else:
            print("❌ Data validation failed")
            return False
        
        # Test file writing (to a test location)
        print("\n4️⃣ Testing file writing...")
        test_path = "test_facilities.json"
        original_path = updater.output_path
        updater.output_path = test_path
        
        updater.update_facilities_file(processed_data)
        
        # Clean up test file
        if os.path.exists(test_path):
            os.remove(test_path)
            print("✅ Test file created and cleaned up")
        
        # Restore original path
        updater.output_path = original_path
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_data_update()
    sys.exit(0 if success else 1)
