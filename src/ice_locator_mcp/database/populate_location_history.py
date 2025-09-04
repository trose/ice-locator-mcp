"""
Script to populate location history for detainees.
This script creates initial location history records for detainees,
assigning them to facilities based on the enriched_detainees.csv data.
"""
import csv
import os
import random
from datetime import datetime, timedelta
from .models import DetaineeLocationHistory
from .manager import DatabaseManager


def populate_location_history(database_url: str, csv_file_path: str = None):
    """
    Populate location history for detainees based on CSV data.
    
    Args:
        database_url: PostgreSQL connection string
        csv_file_path: Path to the CSV file
    """
    if csv_file_path is None:
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'enriched_detainees.csv'
        )
    
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get all facilities to randomly assign detainees
        facilities = db_manager.get_all_facilities()
        
        if not facilities:
            print("No facilities found in database. Please run seed_facility_locations.py first.")
            return
        
        # Get all detainees
        # Note: This is a simplified approach. In a real implementation,
        # you would query the database directly for detainees.
        
        location_history_count = 0
        
        # Read CSV and create location history for each detainee
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Extract relevant information
                facility_name = row.get('facility', '').strip()
                
                # Skip if no facility data
                if not facility_name:
                    continue
                
                # Find matching facility
                matching_facility = None
                for facility in facilities:
                    if facility.name.lower() == facility_name.lower():
                        matching_facility = facility
                        break
                
                # If no exact match, randomly assign to a facility
                if not matching_facility:
                    matching_facility = random.choice(facilities)
                
                # For this implementation, we'll need to get the actual detainee ID
                # This is a simplified approach - in reality, you'd match on name or have IDs in the CSV
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                # Create location history object (current location with no end date)
                location_history = DetaineeLocationHistory(
                    id=None,
                    detainee_id=random.randint(1, 1000),  # Placeholder - would match actual detainee ID
                    facility_id=matching_facility.id,
                    start_date=datetime.now() - timedelta(days=random.randint(1, 365)),  # Random start date
                    end_date=None,  # Current location has no end date
                    created_at=datetime.now()
                )
                
                # Insert into database
                try:
                    db_manager.insert_location_history(location_history)
                    location_history_count += 1
                except Exception as e:
                    print(f"Error inserting location history: {e}")
                    continue
        
        print(f"Successfully created {location_history_count} location history records")
        
    finally:
        db_manager.disconnect()


def create_sample_location_history(database_url: str):
    """
    Create sample location history records for demonstration purposes.
    
    Args:
        database_url: PostgreSQL connection string
    """
    # Initialize database manager
    db_manager = DatabaseManager(database_url)
    db_manager.connect()
    
    try:
        # Get all facilities
        facilities = db_manager.get_all_facilities()
        
        if not facilities:
            print("No facilities found in database. Please run seed_facility_locations.py first.")
            return
        
        # Create sample location history records
        sample_count = 0
        
        # Create some sample location history records
        # In a real implementation, this would be based on actual detainee data
        for i in range(50):  # Create 50 sample records
            facility = random.choice(facilities)
            
            location_history = DetaineeLocationHistory(
                id=None,
                detainee_id=random.randint(1, 100),  # Sample detainee IDs
                facility_id=facility.id,
                start_date=datetime.now() - timedelta(days=random.randint(1, 100)),
                end_date=None if random.choice([True, False]) else datetime.now() - timedelta(days=random.randint(1, 50)),
                created_at=datetime.now()
            )
            
            try:
                db_manager.insert_location_history(location_history)
                sample_count += 1
            except Exception as e:
                print(f"Error inserting sample location history: {e}")
                continue
        
        print(f"Successfully created {sample_count} sample location history records")
        
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    # This would normally be configured through environment variables
    DATABASE_URL = "postgresql://localhost/ice_locator"
    
    # Create sample data for demonstration
    create_sample_location_history(DATABASE_URL)