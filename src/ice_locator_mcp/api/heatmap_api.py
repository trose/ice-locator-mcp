"""
Heatmap API for ICE Locator MCP.

This module provides API endpoints for retrieving heatmap data for the web and mobile apps.
"""

import sys
import os

# Add the src directory to the path so we can import the database package
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional

# Import database modules using the correct package structure
from ice_locator_mcp.database.manager import DatabaseManager
from ice_locator_mcp.database.mock_manager import MockDatabaseManager
from ice_locator_mcp.database.sqlite_manager import SQLiteDatabaseManager
from ice_locator_mcp.database.models import Facility


class HeatmapAPI:
    """API layer for heatmap data."""

    def __init__(self, database_url: Optional[str] = None, use_sqlite: bool = True):
        """
        Initialize the heatmap API.

        Args:
            database_url: PostgreSQL connection string (if not using SQLite)
            use_sqlite: If True, use SQLite database for local development
        """
        self.use_sqlite = use_sqlite
        if use_sqlite:
            self.database_path = os.environ.get(
                "SQLITE_DATABASE_PATH", "ice_locator_facilities.db"
            )
            self.db_manager = None
        else:
            # Use provided database_url or fallback
            self.database_url = database_url or os.environ.get(
                "DATABASE_URL", "postgresql://localhost/ice_locator"
            )
            self.db_manager = None
        self.use_mock = False

    def connect_database(self):
        """Connect to the database."""
        try:
            if self.use_sqlite:
                self.db_manager = SQLiteDatabaseManager(self.database_path)
                self.db_manager.connect()
                self.use_mock = False
            else:
                self.db_manager = DatabaseManager(self.database_url)
                self.db_manager.connect()
                self.use_mock = False
        except Exception as e:
            print(f"Database connection failed: {e}")
            print("Using mock database manager for testing")
            self.db_manager = MockDatabaseManager()
            self.use_mock = True

    def disconnect_database(self):
        """Disconnect from the database."""
        if not self.use_mock and self.db_manager:
            self.db_manager.disconnect()

    def get_facilities(self) -> List[Dict]:
        """
        Get all facilities with their GPS coordinates and population counts.

        Returns:
            List of facilities with id, name, latitude, longitude, address, and population_count
        """
        try:
            self.connect_database()
            facilities = self.db_manager.get_all_facilities()

            result = []
            for facility in facilities:
                result.append(
                    {
                        "id": facility.id,
                        "name": facility.name,
                        "latitude": facility.latitude,
                        "longitude": facility.longitude,
                        "address": facility.address,
                        "population_count": facility.population_count,
                    }
                )

            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve facilities: {str(e)}"
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
                    status_code=404, detail=f"Facility with ID {facility_id} not found"
                )

            # Get current detainee count
            detainee_counts = self.db_manager.get_current_detainee_count_by_facility()
            detainee_count = next(
                (
                    item["detainee_count"]
                    for item in detainee_counts
                    if item["facility_id"] == facility_id
                ),
                0,
            )

            return {
                "id": facility.id,
                "name": facility.name,
                "latitude": facility.latitude,
                "longitude": facility.longitude,
                "address": facility.address,
                "current_detainee_count": detainee_count,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve facility data: {str(e)}"
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
                status_code=500, detail=f"Failed to retrieve heatmap data: {str(e)}"
            )
        finally:
            self.disconnect_database()

    def get_facilities_with_population(self) -> List[Dict]:
        """
        Get all facilities with their population counts for heatmap visualization.

        Returns:
            List of facilities with coordinates and population counts
        """
        try:
            self.connect_database()
            if hasattr(self.db_manager, "get_facilities_with_population"):
                facilities = self.db_manager.get_facilities_with_population()
            else:
                # Fallback to regular facilities if method doesn't exist
                facilities = self.db_manager.get_all_facilities()
                facilities = [
                    {
                        "id": f.id,
                        "name": f.name,
                        "latitude": f.latitude,
                        "longitude": f.longitude,
                        "address": f.address,
                        "population_count": f.population_count,
                        "created_at": f.created_at.isoformat()
                        if f.created_at
                        else None,
                        "updated_at": f.updated_at.isoformat()
                        if f.updated_at
                        else None,
                    }
                    for f in facilities
                    if f.population_count is not None and f.population_count > 0
                ]
            return facilities
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve facilities with population: {str(e)}",
            )
        finally:
            self.disconnect_database()

    def get_facility_statistics(self) -> Dict:
        """
        Get overall facility statistics.

        Returns:
            Dictionary with facility statistics
        """
        try:
            self.connect_database()
            if hasattr(self.db_manager, "get_facility_statistics"):
                stats = self.db_manager.get_facility_statistics()
            else:
                # Fallback statistics
                facilities = self.db_manager.get_all_facilities()
                total_facilities = len(facilities)
                total_population = sum(f.population_count or 0 for f in facilities)
                avg_population = (
                    total_population / total_facilities if total_facilities > 0 else 0
                )

                stats = {
                    "total_facilities": total_facilities,
                    "total_population": total_population,
                    "average_population": round(avg_population, 1),
                    "facilities_by_state": [],
                }
            return stats
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve facility statistics: {str(e)}",
            )
        finally:
            self.disconnect_database()


def create_app(database_url: str = None):
    """Create FastAPI app with database configuration."""
    # Create FastAPI app
    app = FastAPI(
        title="ICE Locator Heatmap API",
        description="API for retrieving heatmap data for ICE facility locations",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store database URL for global API instance
    app.state.database_url = database_url

    return app


# Create default app instance
app = create_app()

# Global heatmap API instance
heatmap_api: Optional[HeatmapAPI] = None


def get_heatmap_api(request: Request = None):
    """Dependency to get the heatmap API instance."""
    global heatmap_api
    if heatmap_api is None:
        # Try to get database_url from app state (for Lambda)
        database_url = None
        if request and hasattr(request.app.state, "database_url"):
            database_url = request.app.state.database_url
        heatmap_api = HeatmapAPI(
            database_url=database_url, use_sqlite=database_url is None
        )
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
            "/api/heatmap-data",
            "/api/facilities-with-population",
            "/api/facility-statistics",
        ],
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
    facility_id: int, api: HeatmapAPI = Depends(get_heatmap_api)
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


@app.get("/api/facilities-with-population")
async def get_facilities_with_population(api: HeatmapAPI = Depends(get_heatmap_api)):
    """
    Get all facilities with their population counts for heatmap visualization.

    Returns:
        List of facilities with coordinates and population counts
    """
    return api.get_facilities_with_population()


@app.get("/api/facility-statistics")
async def get_facility_statistics(api: HeatmapAPI = Depends(get_heatmap_api)):
    """
    Get overall facility statistics.

    Returns:
        Dictionary with facility statistics including total facilities, population, and breakdown by state
    """
    return api.get_facility_statistics()
