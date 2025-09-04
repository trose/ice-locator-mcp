#!/usr/bin/env python3
"""
Mock Heatmap API for testing purposes.

This script provides a simple mock API that returns sample data
for testing the mobile app heatmap functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

app = FastAPI(
    title="Mock ICE Locator Heatmap API",
    description="Mock API for testing heatmap functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_FACILITIES = [
    {
        "id": 1,
        "name": "Los Angeles Detention Center",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "address": "123 Main St, Los Angeles, CA"
    },
    {
        "id": 2,
        "name": "New York Processing Center",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "456 Broadway, New York, NY"
    },
    {
        "id": 3,
        "name": "Chicago Immigration Facility",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "address": "789 Michigan Ave, Chicago, IL"
    },
    {
        "id": 4,
        "name": "Houston Detention Center",
        "latitude": 29.7604,
        "longitude": -95.3698,
        "address": "321 Texas St, Houston, TX"
    },
    {
        "id": 5,
        "name": "Miami Processing Center",
        "latitude": 25.7617,
        "longitude": -80.1918,
        "address": "555 Ocean Dr, Miami, FL"
    }
]

MOCK_HEATMAP_DATA = [
    {
        "id": 1,
        "name": "Los Angeles Detention Center",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "address": "123 Main St, Los Angeles, CA",
        "current_detainee_count": 127
    },
    {
        "id": 2,
        "name": "New York Processing Center",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "456 Broadway, New York, NY",
        "current_detainee_count": 89
    },
    {
        "id": 3,
        "name": "Chicago Immigration Facility",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "address": "789 Michigan Ave, Chicago, IL",
        "current_detainee_count": 64
    },
    {
        "id": 4,
        "name": "Houston Detention Center",
        "latitude": 29.7604,
        "longitude": -95.3698,
        "address": "321 Texas St, Houston, TX",
        "current_detainee_count": 203
    },
    {
        "id": 5,
        "name": "Miami Processing Center",
        "latitude": 25.7617,
        "longitude": -80.1918,
        "address": "555 Ocean Dr, Miami, FL",
        "current_detainee_count": 42
    }
]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mock ICE Locator Heatmap API",
        "version": "1.0.0",
        "endpoints": [
            "/api/facilities",
            "/api/facility/{id}/current-detainees",
            "/api/heatmap-data"
        ]
    }


@app.get("/api/facilities")
async def get_facilities() -> List[Dict]:
    """
    Get all facilities with their GPS coordinates.
    
    Returns:
        List of facilities with id, name, latitude, longitude, and address
    """
    return MOCK_FACILITIES


@app.get("/api/facility/{facility_id}/current-detainees")
async def get_facility_current_detainees(facility_id: int) -> Dict:
    """
    Get current detainee count for a specific facility.
    
    Args:
        facility_id: ID of the facility
        
    Returns:
        Facility information with current detainee count
    """
    facility = next((f for f in MOCK_HEATMAP_DATA if f["id"] == facility_id), None)
    if not facility:
        return {
            "error": "Facility not found"
        }
    return facility


@app.get("/api/heatmap-data")
async def get_heatmap_data() -> List[Dict]:
    """
    Get aggregated data for heatmap visualization.
    
    Returns:
        List of facilities with coordinates and detainee counts
    """
    return MOCK_HEATMAP_DATA


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)