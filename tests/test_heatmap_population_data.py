"""
Test script to verify that the heatmap API correctly returns population count data.
"""
import requests
import json


def test_heatmap_population_data():
    """Test that the heatmap API returns population count data."""
    try:
        # Make request to the heatmap API
        response = requests.get("http://localhost:8082/api/heatmap-data")
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Verify that we have data
        assert len(data) > 0, "API should return facility data"
        
        # Check that the first facility has the expected fields
        first_facility = data[0]
        required_fields = ['id', 'name', 'latitude', 'longitude', 'address', 'population_count', 'detainee_count']
        
        for field in required_fields:
            assert field in first_facility, f"Facility should have '{field}' field"
        
        # Check that population_count and detainee_count are integers or None
        if first_facility['population_count'] is not None:
            assert isinstance(first_facility['population_count'], int), "population_count should be an integer or None"
        
        assert isinstance(first_facility['detainee_count'], int), "detainee_count should be an integer"
        
        # Find a facility with population data (if any)
        facilities_with_population = [f for f in data if f['population_count'] is not None and f['population_count'] > 0]
        
        if facilities_with_population:
            facility = facilities_with_population[0]
            print(f"✓ Facility '{facility['name']}' has population count: {facility['population_count']}")
            print(f"✓ Facility '{facility['name']}' has detainee count: {facility['detainee_count']}")
        else:
            print("⚠ No facilities with population data found in this sample")
        
        # Count facilities with and without population data
        facilities_with_pop = len([f for f in data if f['population_count'] is not None])
        facilities_without_pop = len([f for f in data if f['population_count'] is None])
        
        print(f"✓ Total facilities: {len(data)}")
        print(f"✓ Facilities with population data: {facilities_with_pop}")
        print(f"✓ Facilities without population data: {facilities_without_pop}")
        
        print("✓ All tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to the heatmap API. Make sure the server is running on port 8082.")
        return False
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("Testing heatmap API population count data...")
    test_heatmap_population_data()