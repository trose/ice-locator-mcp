"""
Unit tests for the heatmap API.
"""
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ice_locator_mcp.api.heatmap_api import app, HeatmapAPI


class TestHeatmapAPI(unittest.TestCase):
    """Test cases for the heatmap API."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("endpoints", data)
        self.assertEqual(data["message"], "ICE Locator Heatmap API")
    
    @patch('ice_locator_mcp.api.heatmap_api.HeatmapAPI.get_facilities')
    def test_get_facilities_endpoint(self, mock_get_facilities):
        """Test the get facilities endpoint."""
        # Mock the return value
        mock_get_facilities.return_value = [
            {
                "id": 1,
                "name": "Test Facility",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Test St"
            }
        ]
        
        response = self.client.get("/api/facilities")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Facility")
    
    @patch('ice_locator_mcp.api.heatmap_api.HeatmapAPI.get_facility_current_detainees')
    def test_get_facility_current_detainees_endpoint(self, mock_get_facility):
        """Test the get facility current detainees endpoint."""
        # Mock the return value
        mock_get_facility.return_value = {
            "id": 1,
            "name": "Test Facility",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "address": "123 Test St",
            "current_detainee_count": 5
        }
        
        response = self.client.get("/api/facility/1/current-detainees")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["current_detainee_count"], 5)
    
    @patch('ice_locator_mcp.api.heatmap_api.HeatmapAPI.get_heatmap_data')
    def test_get_heatmap_data_endpoint(self, mock_get_heatmap_data):
        """Test the get heatmap data endpoint."""
        # Mock the return value
        mock_get_heatmap_data.return_value = [
            {
                "id": 1,
                "name": "Test Facility",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Test St",
                "detainee_count": 5
            }
        ]
        
        response = self.client.get("/api/heatmap-data")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["detainee_count"], 5)


class TestHeatmapAPIClass(unittest.TestCase):
    """Test cases for the HeatmapAPI class."""
    
    def setUp(self):
        """Set up test heatmap API."""
        self.heatmap_api = HeatmapAPI("sqlite:///test.db")
    
    def test_heatmap_api_initialization(self):
        """Test HeatmapAPI initialization."""
        self.assertIsInstance(self.heatmap_api, HeatmapAPI)
        self.assertEqual(self.heatmap_api.database_url, "sqlite:///test.db")
    
    @patch('ice_locator_mcp.api.heatmap_api.DatabaseManager')
    def test_connect_database(self, mock_db_manager):
        """Test database connection."""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        
        heatmap_api = HeatmapAPI()
        heatmap_api.connect_database()
        
        mock_db_manager.assert_called()
        mock_db_instance.connect.assert_called()
    
    @patch('ice_locator_mcp.api.heatmap_api.DatabaseManager')
    def test_disconnect_database(self, mock_db_manager):
        """Test database disconnection."""
        mock_db_instance = Mock()
        mock_db_manager.return_value = mock_db_instance
        
        heatmap_api = HeatmapAPI()
        heatmap_api.disconnect_database()
        
        mock_db_instance.disconnect.assert_called()


if __name__ == "__main__":
    unittest.main()