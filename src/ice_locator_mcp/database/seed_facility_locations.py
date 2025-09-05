"""
Script to seed facility locations with GPS coordinates.
This script can gather GPS coordinates for facilities either from a predefined list
or by using geocoding services.
"""
import os
import json
import csv
from datetime import datetime
from .models import Facility
from .manager import DatabaseManager


def get_facility_list(csv_file_path: str = None) -> list:
    """
    Extract unique facility names from the enriched detainees CSV.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        List of unique facility names
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'enriched_detainees.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    facilities = set()
    
    # Read facilities from CSV
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            facility = row.get('facility_name', '').strip()
            if facility:
                facilities.add(facility)
    
    return list(facilities)


def seed_facility_locations(database_url: str):
    """
    Seed facility locations with basic information.
    In a real implementation, this would use geocoding services to get GPS coordinates.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get facility list
        facilities = get_facility_list()
        seeded_count = 0
        
        # For demonstration purposes, we'll use dummy coordinates
        # In a real implementation, you would use a geocoding service
        dummy_coordinates = {
            "Adams County Correctional Center": (31.4839, -91.5140),
            "Baltimore Field Office": (39.2904, -76.6122),
            "Broward Transitional Center": (26.1224, -80.1368),
            "Chicago Field Office": (41.8781, -87.6298),
            "Cibola County Correctional Center": (34.9167, -107.6500),
            "Edinburg Processing Center": (26.3303, -98.1597),
            "El Paso Processing Center": (31.7683, -106.4517),
            "Folsom State Prison": (38.6573, -121.1731),
            "Houston Contract Detention Facility": (29.7604, -95.3698),
            "Karnes County Correctional Center": (28.9084, -97.9263),
            "La Palma Correctional Center": (32.9600, -115.2900),
            "Los Angeles Field Office": (34.0522, -118.2437),
            "Miami Field Office": (25.7617, -80.1918),
            "Otero County Processing Center": (32.5500, -107.3500),
            "Pendleton Correctional Facility": (40.0833, -85.6167),
            "Port Isabel Service Processing Center": (26.0833, -97.3667),
            "Prairieland Detention Complex": (32.5833, -94.0500),
            "Sacramento Field Office": (38.5816, -121.4944),
            "San Antonio Field Office": (29.4241, -98.4936),
            "San Diego Field Office": (32.7157, -117.1611),
            "San Luis Detention Center": (32.5000, -114.7000),
            "Stewart Detention Center": (32.0833, -84.7000),
            "Tallahassee Field Office": (30.4383, -84.2807),
            "Tucson Field Office": (32.2217, -110.9265),
            # Add facilities from CSV with Florida locations since most are in Florida
            "Florida State Prison": (29.9333, -82.2000),
            "Miami Processing Center": (25.7617, -80.1918),
            "Palm Beach County Jail": (26.7056, -80.0364),
            "Alligator Alcatraz Detention Center": (25.8577, -81.3985),
            "Orange County Jail": (28.5383, -81.3792),
            "Broward Transitional Center": (26.1224, -80.1368)
        }
        
        for facility_name in facilities:
            # Check if facility already exists
            existing_facilities = db_manager.get_all_facilities()
            if any(f.name == facility_name for f in existing_facilities):
                print(f"Facility {facility_name} already exists, skipping...")
                continue
            
            # Get coordinates or use default
            lat, lon = dummy_coordinates.get(facility_name, (0.0, 0.0))
            
            # Create facility object
            facility = Facility(
                id=None,
                name=facility_name,
                latitude=lat,
                longitude=lon,
                address=None,  # Would be populated in a real implementation
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Insert into database
            try:
                db_manager.insert_facility(facility)
                seeded_count += 1
                print(f"Seeded facility: {facility_name}")
            except Exception as e:
                print(f"Error inserting facility {facility_name}: {e}")
                continue
        
        print(f"Successfully seeded {seeded_count} facilities")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # This would normally be configured through environment variables
    DATABASE_URL = "postgresql://localhost/ice_locator"
    seed_facility_locations(DATABASE_URL)