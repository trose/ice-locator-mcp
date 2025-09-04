"""
Mock database manager for testing the heatmap feature without a real database.
"""

from typing import List
from datetime import datetime
from .models import Detainee, Facility, DetaineeLocationHistory


class MockDatabaseManager:
    """Mock database manager for testing the heatmap feature."""
    
    def __init__(self):
        """Initialize with mock data."""
        self.facilities = [
            Facility(
                id=1,
                name="Los Angeles Detention Center",
                latitude=34.0522,
                longitude=-118.2437,
                address="123 Main St, Los Angeles, CA",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Facility(
                id=2,
                name="New York Processing Center",
                latitude=40.7128,
                longitude=-74.0060,
                address="456 Broadway, New York, NY",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Facility(
                id=3,
                name="Chicago Immigration Facility",
                latitude=41.8781,
                longitude=-87.6298,
                address="789 Michigan Ave, Chicago, IL",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Facility(
                id=4,
                name="Houston Detention Center",
                latitude=29.7604,
                longitude=-95.3698,
                address="321 Texas St, Houston, TX",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Facility(
                id=5,
                name="Miami Processing Center",
                latitude=25.7617,
                longitude=-80.1918,
                address="555 Ocean Dr, Miami, FL",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # Mock location history with current detainees (end_date is None)
        self.location_history = [
            DetaineeLocationHistory(
                id=1,
                detainee_id=1,
                facility_id=1,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=2,
                detainee_id=2,
                facility_id=1,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=3,
                detainee_id=3,
                facility_id=2,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=4,
                detainee_id=4,
                facility_id=3,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=5,
                detainee_id=5,
                facility_id=4,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=6,
                detainee_id=6,
                facility_id=4,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
            DetaineeLocationHistory(
                id=7,
                detainee_id=7,
                facility_id=4,
                start_date=datetime.now(),
                end_date=None,
                created_at=datetime.now()
            ),
        ]
    
    def connect(self):
        """Mock connect method."""
        pass
    
    def disconnect(self):
        """Mock disconnect method."""
        pass
    
    def get_all_facilities(self) -> List[Facility]:
        """
        Retrieve all facilities from the mock database.
        
        Returns:
            List of Facility objects
        """
        return self.facilities
    
    def get_current_detainee_count_by_facility(self) -> List[dict]:
        """
        Get current detainee count for each facility.
        
        Returns:
            List of dictionaries with facility_id and detainee_count
        """
        counts = {}
        for facility in self.facilities:
            counts[facility.id] = 0
        
        # Count current detainees (where end_date is None)
        for history in self.location_history:
            if history.end_date is None:
                counts[history.facility_id] = counts.get(history.facility_id, 0) + 1
        
        results = []
        for facility_id, count in counts.items():
            facility = next((f for f in self.facilities if f.id == facility_id), None)
            if facility:
                results.append({
                    'facility_id': facility_id,
                    'facility_name': facility.name,
                    'detainee_count': count
                })
        
        return results
    
    def get_heatmap_data(self) -> List[dict]:
        """
        Get aggregated data for heatmap visualization.
        
        Returns:
            List of dictionaries with facility coordinates and detainee counts
        """
        counts = {}
        for facility in self.facilities:
            counts[facility.id] = 0
        
        # Count current detainees (where end_date is None)
        for history in self.location_history:
            if history.end_date is None:
                counts[history.facility_id] = counts.get(history.facility_id, 0) + 1
        
        results = []
        for facility in self.facilities:
            detainee_count = counts.get(facility.id, 0)
            results.append({
                'id': facility.id,
                'name': facility.name,
                'latitude': facility.latitude,
                'longitude': facility.longitude,
                'address': facility.address,
                'current_detainee_count': detainee_count
            })
        
        return results