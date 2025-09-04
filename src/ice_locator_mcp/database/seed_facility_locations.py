"""
Script to seed facility locations with GPS coordinates.
This script can gather GPS coordinates for facilities either from a predefined list
or by using geocoding services.
"""
import os
import json
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
    
    # For now, we'll use a predefined list of common ICE facilities
    # In a real implementation, this would extract from the CSV
    common_facilities = [
        "Adams County Correctional Center",
        "Allen County Jail",
        "Arizona State Prison Complex-EB Jordan",
        "Baker County Correctional Facility",
        "Baltimore Field Office",
        "Barranquitas Correctional Facility",
        "Bossier Deportation Facility",
        "Broward Transitional Center",
        "Butler County Jail",
        "Calhoun County Correctional Center",
        "Campbell County Correctional Facility",
        "Caroline County Sheriff's Office",
        "Chase County Detention Center",
        "Chester County Prison",
        "Chicago Field Office",
        "Cibola County Correctional Center",
        "Clay County Jail",
        "Colfax County Correctional Facility",
        "CoreCivic of Tennessee",
        "Dallas County Jail",
        "Dodge County Correctional Facility",
        "Donley County Correctional Center",
        "Edinburg Processing Center",
        "El Paso Processing Center",
        "El Reno Federal Correctional Institution",
        "Emporia Correctional Facility",
        "Eufaula Federal Correctional Institution",
        "Fayette County Correctional Institution",
        "Florence Correctional Facility",
        "Florida County Jail",
        "Folsom State Prison",
        "Franklin County Jail",
        "Georgia State Prison",
        "Giles County Correctional Facility",
        "Graham County Correctional Institution",
        "Guayama Correctional Facility",
        "Harnett County Correctional Institution",
        "Henderson County Correctional Facility",
        "Houston Contract Detention Facility",
        "Hudson County Correctional Center",
        "Imperial Regional Detention Facility",
        "Iowa County Jail",
        "Jackson County Correctional Facility",
        "Karnes County Correctional Center",
        "Kemper County Correctional Facility",
        "Kootenai County Jail",
        "La Palma Correctional Center",
        "Las Brisas Academy Juvenile Correctional Facility",
        "Lee County Correctional Institution",
        "Leominster State Prison",
        "Letcher County Correctional Complex",
        "Liberty County Jail",
        "Limestone County Correctional Center",
        "Los Angeles Field Office",
        "Mesa Verde Detention Facility",
        "Miami Field Office",
        "Minidoka County Jail",
        "Monroe County Correctional Facility",
        "Montgomery County Correctional Facility",
        "Morgan County Correctional Complex",
        "Nassau County Correctional Center",
        "New Mexico State Penitentiary",
        "New York City Field Office",
        "Northwest Florida Reception Center",
        "Otero County Processing Center",
        "Palm Beach County Jail",
        "Pendleton Correctional Facility",
        "Philadelphia Field Office",
        "Pike County Correctional Facility",
        "Port Isabel Service Processing Center",
        "Prairieland Detention Complex",
        "Pulaski County Detention Center",
        "Richmond County Correctional Center",
        "Robert A. Deyton Correctional Institution",
        "Rolling Plains Detention Center",
        "Sacramento Field Office",
        "San Antonio Field Office",
        "San Diego Field Office",
        "San Luis Detention Center",
        "San Pedro Service Processing Center",
        "Sandoval County Correctional Facility",
        "Scott County Jail",
        "Sherburne County Jail",
        "Sierra Detention Center",
        "South Bay Correctional Facility",
        "South Georgia Regional Prison",
        "Southwest Georgia Regional Prison",
        "Stanton County Correctional Facility",
        "Stewart Detention Center",
        "Tallahatchie County Correctional Facility",
        "Tallahassee Field Office",
        "Tarrant County Jail",
        "Tucson Field Office",
        "Val Verde Correctional Facility",
        "Washington County Detention Center",
        "Winn Correctional Center",
        "York County Prison"
    ]
    
    return common_facilities


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