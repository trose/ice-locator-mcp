"""
Test script to verify population count data for specific facilities.
"""
import requests
import json


def test_specific_facility_population():
    """Test that specific facilities have the correct population count data."""
    try:
        # Make request to the heatmap API
        response = requests.get("http://localhost:8082/api/heatmap-data")
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Create a dictionary for easier lookup
        facilities_dict = {facility['name']: facility for facility in data}
        
        # Test specific facilities that should have population data
        expected_populations = {
            "Broward Transitional Center": 651,
            "Baker County Sheriff's Office, FLORIDA": 260,
            "Orange County Jail": 165
        }
        
        print("Testing specific facility population data:")
        all_tests_passed = True
        
        for facility_name, expected_population in expected_populations.items():
            if facility_name in facilities_dict:
                facility = facilities_dict[facility_name]
                actual_population = facility['population_count']
                
                if actual_population == expected_population:
                    print(f"✓ {facility_name}: {actual_population} (expected: {expected_population})")
                else:
                    print(f"✗ {facility_name}: {actual_population} (expected: {expected_population})")
                    all_tests_passed = False
            else:
                print(f"⚠ {facility_name}: Not found in API response")
        
        # Test that population counts are reasonable (not negative)
        negative_populations = [f for f in data if f['population_count'] is not None and f['population_count'] < 0]
        if negative_populations:
            print(f"✗ Found {len(negative_populations)} facilities with negative population counts")
            all_tests_passed = False
        else:
            print("✓ No facilities with negative population counts")
        
        # Test that all facilities have required fields
        required_fields = ['id', 'name', 'latitude', 'longitude', 'address', 'population_count', 'detainee_count']
        missing_fields_facilities = []
        
        for facility in data:
            missing_fields = [field for field in required_fields if field not in facility]
            if missing_fields:
                missing_fields_facilities.append((facility['name'], missing_fields))
        
        if missing_fields_facilities:
            print(f"✗ Found {len(missing_fields_facilities)} facilities missing required fields:")
            for name, missing in missing_fields_facilities[:5]:  # Show first 5
                print(f"  - {name}: missing {missing}")
            all_tests_passed = False
        else:
            print("✓ All facilities have required fields")
        
        if all_tests_passed:
            print("\n✓ All specific facility tests passed!")
        else:
            print("\n✗ Some specific facility tests failed!")
            
        return all_tests_passed
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the heatmap API. Make sure the server is running on port 8082.")
        return False
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    test_specific_facility_population()