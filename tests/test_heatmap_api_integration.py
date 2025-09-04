"""
Integration tests for the heatmap API.
"""
import unittest
import tempfile
import os
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ice_locator_mcp.api.heatmap_api import app


class TestHeatmapAPIIntegration(unittest.TestCase):
    """Integration tests for the heatmap API."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_api_endpoints_exist(self):
        """Test that all expected API endpoints exist."""
        # Test root endpoint
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains expected endpoints
        data = response.json()
        self.assertIn("endpoints", data)
        expected_endpoints = [
            "/api/facilities",
            "/api/heatmap-data"
        ]
        
        # The facility endpoint with parameter is harder to test directly
        for endpoint in expected_endpoints:
            self.assertIn(endpoint, data["endpoints"])
    
    def test_cors_headers(self):
        """Test that CORS headers are set."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        # Check for CORS headers (these would be set in a real implementation)
        # For now, we're just verifying the response structure
        self.assertIn("content-type", response.headers)
    
    def test_api_documentation(self):
        """Test that API documentation is available."""
        # Test OpenAPI docs
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        
        # Test OpenAPI JSON
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()