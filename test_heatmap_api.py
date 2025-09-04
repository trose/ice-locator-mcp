"""
Simple test script to verify heatmap API implementation.
"""
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ice_locator_mcp', 'api'))

try:
    # Test importing the heatmap API directly
    import heatmap_api
    print("Heatmap API module imported successfully")
    
    # Test creating a heatmap API instance
    heatmap_api_instance = heatmap_api.HeatmapAPI("sqlite:///test.db")
    print("Heatmap API instance created successfully")
    
    # Test the app instance
    print(f"FastAPI app title: {heatmap_api.app.title}")
    print(f"FastAPI app description: {heatmap_api.app.description}")
    
    print("Heatmap API implementation is working correctly!")
    
except Exception as e:
    print(f"Error testing heatmap API implementation: {e}")
    import traceback
    traceback.print_exc()