"""
Heatmap API for ICE Locator MCP.

This module provides API endpoints for retrieving heatmap data for the web and mobile apps.
"""
import sys
import os

# Add the database directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Optional

# Import database modules
from database.manager import DatabaseManager
from database.models import Facility


class HeatmapAPI:
    """API layer for heatmap data."""
    
    def __init__(self, database_url: str = None):
        """
        Initialize the heatmap API.
        
        Args:
            database_url: PostgreSQL connection string
        """
        # Default to environment variable or local database
        self.database_url = database_url or os.environ.get(
            "DATABASE_URL", 
            "postgresql://localhost/ice_locator"
        )
        self.db_manager = DatabaseManager(self.database_url)
    
    def connect_database(self):
        """Connect to the database."""
        try:
            self.db_manager.connect()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database connection failed: {str(e)}"
            )
    
    def disconnect_database(self):
        """Disconnect from the database."""
        self.db_manager.disconnect()
    
    def get_facilities(self) -> List[Dict]:
        """
        Get all facilities with their GPS coordinates.
        
        Returns:
            List of facilities with id, name, latitude, longitude, and address
        """
        try:
            self.connect_database()
            facilities = self.db_manager.get_all_facilities()
            
            result = []
            for facility in facilities:
                result.append({
                    "id": facility.id,
                    "name": facility.name,
                    "latitude": facility.latitude,
                    "longitude": facility.longitude,
                    "address": facility.address
                })
            
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve facilities: {str(e)}"
            )
        finally:
            self.disconnect_database()
    
    def get_facility_current_detainees(self, facility_id: int) -> Dict:
        """
        Get current detainee count for a specific facility.
        
        Args:
            facility_id: ID of the facility
            
        Returns:
            Dictionary with facility information and detainee count
        """
        try:
            self.connect_database()
            
            # Get facility details
            facilities = self.db_manager.get_all_facilities()
            facility = next((f for f in facilities if f.id == facility_id), None)
            
            if not facility:
                raise HTTPException(
                    status_code=404,
                    detail=f"Facility with ID {facility_id} not found"
                )
            
            # Get current detainee count
            detainee_counts = self.db_manager.get_current_detainee_count_by_facility()
            detainee_count = next(
                (item['detainee_count'] for item in detainee_counts 
                 if item['facility_id'] == facility_id), 0
            )
            
            return {
                "id": facility.id,
                "name": facility.name,
                "latitude": facility.latitude,
                "longitude": facility.longitude,
                "address": facility.address,
                "current_detainee_count": detainee_count
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve facility data: {str(e)}"
            )
        finally:
            self.disconnect_database()
    
    def get_heatmap_data(self) -> List[Dict]:
        """
        Get aggregated data for heatmap visualization.
        
        Returns:
            List of facilities with coordinates and detainee counts
        """
        try:
            self.connect_database()
            heatmap_data = self.db_manager.get_heatmap_data()
            return heatmap_data
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve heatmap data: {str(e)}"
            )
        finally:
            self.disconnect_database()


# Create FastAPI app
app = FastAPI(
    title="ICE Locator Heatmap API",
    description="API for retrieving heatmap data for ICE facility locations",
    version="1.0.0"
)

# Global heatmap API instance
heatmap_api: Optional[HeatmapAPI] = None


def get_heatmap_api():
    """Dependency to get the heatmap API instance."""
    global heatmap_api
    if heatmap_api is None:
        heatmap_api = HeatmapAPI()
    return heatmap_api


@app.on_event("startup")
async def startup_event():
    """Initialize the heatmap API on startup."""
    global heatmap_api
    heatmap_api = HeatmapAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ICE Locator Heatmap API", 
        "version": "1.0.0",
        "endpoints": [
            "/api/facilities",
            "/api/facility/{id}/current-detainees",
            "/api/heatmap-data"
        ]
    }


@app.get("/api/facilities")
async def get_facilities(api: HeatmapAPI = Depends(get_heatmap_api)):
    """
    Get all facilities with their GPS coordinates.
    
    Returns:
        List of facilities with id, name, latitude, longitude, and address
    """
    return api.get_facilities()


@app.get("/api/facility/{facility_id}/current-detainees")
async def get_facility_current_detainees(
    facility_id: int, 
    api: HeatmapAPI = Depends(get_heatmap_api)
):
    """
    Get current detainee count for a specific facility.
    
    Args:
        facility_id: ID of the facility
        
    Returns:
        Facility information with current detainee count
    """
    return api.get_facility_current_detainees(facility_id)


@app.get("/api/heatmap-data")
async def get_heatmap_data(api: HeatmapAPI = Depends(get_heatmap_api)):
    """
    Get aggregated data for heatmap visualization.
    
    Returns:
        List of facilities with coordinates and detainee counts
    """
    return api.get_heatmap_data()