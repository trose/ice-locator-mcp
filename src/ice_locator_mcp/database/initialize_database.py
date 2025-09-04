"""
Script to initialize the database for the heatmap feature.
This script creates the database schema and populates initial data.
"""
import os
import sys
from datetime import datetime
from .manager import DatabaseManager
from .models import Detainee, Facility, DetaineeLocationHistory


def initialize_database(database_url: str):
    """
    Initialize the database with schema and initial data.
    
    Args:
        database_url: PostgreSQL connection string
    """
    print("Initializing database for heatmap feature...")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Create tables
        print("Creating database tables...")
        db_manager.create_tables()
        print("Database tables created successfully.")
        
        # Check if we already have data
        facilities = db_manager.get_all_facilities()
        if facilities:
            print(f"Database already contains {len(facilities)} facilities. Skipping initial data population.")
            return
        
        # Create sample facilities
        print("Creating sample facilities...")
        sample_facilities = [
            ("Adams County Correctional Center", 31.4839, -91.5140, "Natchez, MS"),
            ("Baltimore Field Office", 39.2904, -76.6122, "Baltimore, MD"),
            ("Broward Transitional Center", 26.1224, -80.1368, "Miami, FL"),
            ("Chicago Field Office", 41.8781, -87.6298, "Chicago, IL"),
            ("Cibola County Correctional Center", 34.9167, -107.6500, "Milan, NM"),
            ("Edinburg Processing Center", 26.3303, -98.1597, "Edinburg, TX"),
            ("El Paso Processing Center", 31.7683, -106.4517, "El Paso, TX"),
            ("Folsom State Prison", 38.6573, -121.1731, "Folsom, CA"),
            ("Houston Contract Detention Facility", 29.7604, -95.3698, "Houston, TX"),
            ("Karnes County Correctional Center", 28.9084, -97.9263, "Karnes City, TX"),
        ]
        
        facility_ids = []
        for name, lat, lon, address in sample_facilities:
            facility = Facility(
                id=None,
                name=name,
                latitude=lat,
                longitude=lon,
                address=address,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            facility_id = db_manager.insert_facility(facility)
            facility_ids.append(facility_id)
            print(f"Created facility: {name}")
        
        # Create sample detainees
        print("Creating sample detainees...")
        sample_detainees = [
            ("John", "Smith"),
            ("Maria", "Garcia"),
            ("Robert", "Johnson"),
            ("Emily", "Williams"),
            ("Michael", "Brown"),
            ("Sarah", "Davis"),
            ("William", "Miller"),
            ("Jessica", "Wilson"),
            ("David", "Moore"),
            ("Lisa", "Taylor"),
        ]
        
        detainee_ids = []
        for first_name, last_name in sample_detainees:
            detainee = Detainee(
                id=None,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            detainee_id = db_manager.insert_detainee(detainee)
            detainee_ids.append(detainee_id)
            print(f"Created detainee: {first_name} {last_name}")
        
        # Create sample location history
        print("Creating sample location history...")
        from random import choice, randint
        from datetime import timedelta
        
        for detainee_id in detainee_ids:
            # Assign each detainee to a random facility
            facility_id = choice(facility_ids)
            
            # Some detainees are current (no end date), some have left (with end date)
            end_date = None if choice([True, False]) else datetime.now() - timedelta(days=randint(1, 30))
            
            location_history = DetaineeLocationHistory(
                id=None,
                detainee_id=detainee_id,
                facility_id=facility_id,
                start_date=datetime.now() - timedelta(days=randint(30, 365)),
                end_date=end_date,
                created_at=datetime.now()
            )
            
            db_manager.insert_location_history(location_history)
        
        print("Sample data created successfully.")
        print("Database initialization completed.")
        
    finally:
        db_manager.disconnect()


def main():
    """Main function to initialize the database."""
    # This would normally be configured through environment variables
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/ice_locator")
    
    try:
        initialize_database(DATABASE_URL)
        print("Database initialization completed successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()