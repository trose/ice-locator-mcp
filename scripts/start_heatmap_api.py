#!/usr/bin/env python3
"""
Start the heatmap API server.
"""

import sys
import os
import uvicorn

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

from ice_locator_mcp.api.heatmap_api import app

if __name__ == "__main__":
    print("🚀 Starting ICE Locator Heatmap API Server")
    print("📊 Using SQLite database: ice_locator_facilities.db")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("\nAvailable endpoints:")
    print("  GET /api/facilities - All facilities with coordinates and population")
    print("  GET /api/facilities-with-population - Facilities with population data")
    print("  GET /api/facility-statistics - Overall facility statistics")
    print("  GET /api/heatmap-data - Heatmap visualization data")
    print("  GET /api/facility/{id}/current-detainees - Current detainees for a facility")
    
    uvicorn.run("ice_locator_mcp.api.heatmap_api:app", host="0.0.0.0", port=8000, reload=True)
