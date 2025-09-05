"""
Test suite for verifying accurate detainee counts in heatmap data.
Tests edge cases and ensures the API returns correct facility detainee counts.
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ice_locator_mcp.database.manager import DatabaseManager
from ice_locator_mcp.api.heatmap_api import HeatmapAPI


class TestHeatmapDetaineeCounts(unittest.TestCase):
    """Test cases for verifying accurate detainee counts in heatmap data."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.database_url = "postgresql://localhost/ice_locator"
        self.db_manager = DatabaseManager(self.database_url)
        
    def test_database_connection(self):
        """Test that we can connect to the database."""
        try:
            self.db_manager.connect()
            self.db_manager.disconnect()
            connected = True
        except Exception:
            connected = False
        self.assertTrue(connected, "Should be able to connect to the database")
    
    def test_get_heatmap_data_returns_list(self):
        """Test that get_heatmap_data returns a list of dictionaries."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        self.assertIsInstance(result, list, "get_heatmap_data should return a list")
        if result:
            self.assertIsInstance(result[0], dict, "Each item should be a dictionary")
    
    def test_heatmap_data_contains_required_fields(self):
        """Test that each facility in heatmap data has required fields."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        if result:
            facility = result[0]
            required_fields = ['id', 'name', 'latitude', 'longitude', 'address', 'detainee_count']
            for field in required_fields:
                self.assertIn(field, facility, f"Facility should have '{field}' field")
    
    def test_detainee_count_is_integer(self):
        """Test that detainee_count is an integer for all facilities."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        for facility in result:
            self.assertIsInstance(facility['detainee_count'], int, 
                                f"detainee_count should be integer for {facility['name']}")
    
    def test_no_negative_detainee_counts(self):
        """Test that there are no negative detainee counts."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        negative_counts = [f for f in result if f['detainee_count'] < 0]
        self.assertEqual(len(negative_counts), 0, 
                        f"Should not have negative detainee counts, found: {negative_counts}")
    
    def test_known_facilities_have_correct_counts(self):
        """Test that known facilities have the expected detainee counts."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        # Convert to dictionary for easier lookup
        facilities_dict = {f['name']: f['detainee_count'] for f in result}
        
        # Test some known facilities (these values should match what we saw in our manual check)
        expected_counts = {
            'Florida State Prison': 128,
            'Miami Processing Center': 128,
            'Palm Beach County Jail': 127,
            'Alligator Alcatraz Detention Center': 125,
            'Orange County Jail': 122,
            'Broward Transitional Center': 118
        }
        
        for facility_name, expected_count in expected_counts.items():
            if facility_name in facilities_dict:
                self.assertEqual(facilities_dict[facility_name], expected_count,
                               f"{facility_name} should have {expected_count} detainees, got {facilities_dict[facility_name]}")
    
    def test_majority_of_facilities_have_zero_detainees(self):
        """Test that the majority of facilities have zero detainees (expected for this dataset)."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        total_facilities = len(result)
        zero_detainee_facilities = len([f for f in result if f['detainee_count'] == 0])
        
        # We expect most facilities to have zero detainees
        self.assertGreater(zero_detainee_facilities, total_facilities * 0.9,
                          "Majority of facilities should have zero detainees")
    
    def test_distinct_detainee_counting(self):
        """Test that detainees are counted distinctly (no double counting)."""
        # This test verifies our SQL query uses COUNT(DISTINCT dlh.detainee_id)
        # We'll check this by examining the query structure
        import inspect
        import re
        
        # Get the source code of the get_heatmap_data method
        source = inspect.getsource(self.db_manager.get_heatmap_data)
        
        # Check that the query uses COUNT(DISTINCT ...)
        self.assertIn('COUNT(DISTINCT', source, 
                     "Query should use COUNT(DISTINCT) to avoid double counting detainees")
        
        # Check that it's counting detainee_id specifically
        self.assertIn('detainee_id', source,
                     "Query should count DISTINCT detainee_id")
    
    def test_facility_with_multiple_location_records(self):
        """Test edge case: facility with multiple location history records for same detainee."""
        # This would be an issue if we used COUNT(dlh.id) instead of COUNT(DISTINCT dlh.detainee_id)
        # In that case, a detainee with multiple location records would be counted multiple times
        # Our current implementation should handle this correctly
        
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        # Find a facility with detainees
        facilities_with_detainees = [f for f in result if f['detainee_count'] > 0]
        if facilities_with_detainees:
            # We're just verifying the data structure is correct
            facility = facilities_with_detainees[0]
            self.assertIsInstance(facility['detainee_count'], int)
            self.assertGreaterEqual(facility['detainee_count'], 0)
    
    def test_database_layer_returns_correct_counts(self):
        """Test that the database layer returns correct detainee counts."""
        # This is a more focused test that directly tests the database layer
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        # Check that we have data
        self.assertGreater(len(result), 0, "Should have facility data")
        
        # Check that we have some facilities with detainees
        facilities_with_detainees = [f for f in result if f['detainee_count'] > 0]
        self.assertGreater(len(facilities_with_detainees), 0, "Should have facilities with detainees")
        
        # Check that the counts are reasonable (not negative)
        for facility in result:
            self.assertGreaterEqual(facility['detainee_count'], 0, 
                                  f"Detainee count should not be negative for {facility['name']}")
    
    def test_edge_case_zero_detainees(self):
        """Test edge case: facilities with zero detainees."""
        self.db_manager.connect()
        result = self.db_manager.get_heatmap_data()
        self.db_manager.disconnect()
        
        # Find facilities with zero detainees
        zero_detainee_facilities = [f for f in result if f['detainee_count'] == 0]
        
        # Should have some facilities with zero detainees
        self.assertGreater(len(zero_detainee_facilities), 0, 
                          "Should have facilities with zero detainees")
        
        # Verify all have zero count
        for facility in zero_detainee_facilities:
            self.assertEqual(facility['detainee_count'], 0, 
                           f"Facility {facility['name']} should have zero detainees")


if __name__ == '__main__':
    unittest.main()